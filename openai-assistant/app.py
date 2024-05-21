import logging
import os
from typing import List, Dict, Optional


import chainlit as cl
from chainlit.types import ThreadDict
from literalai import Thread
from openai import BadRequestError

from chainlit_utils import process_files
from cl_events.on_chat_resume import on_chat_resume_logic
from cl_events.on_chat_start import on_start_chat_logic
from cl_events.step import step_logic
from utils.openai_utils import initialize_openai_client

logging.basicConfig(level=logging.INFO)

client = initialize_openai_client()

logger = logging.getLogger("chainlit")

ASSISTANT_NAME = os.getenv('ASSISTANT_NAME')


# Uncomment for live deployments!
# @cl.oauth_callback
# async def oauth_callback(provider_id: str, token: str, raw_user_data: Dict[str, str], default_app_user: cl.User) -> \
#         Optional[cl.User]:
#     return await oauth_callback_logic(provider_id, token, raw_user_data, default_app_user)


@cl.on_chat_start
async def on_chat_start_callback():
    return await on_start_chat_logic(client)


# Simple, local auth for dev, don't use in PROD!
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Chatbot": ASSISTANT_NAME}
    return rename_dict.get(orig_author, orig_author)


@cl.on_chat_resume
async def on_chat_resume_callback(thread: ThreadDict):
    return await on_chat_resume_logic(thread, client)


@cl.step(name=ASSISTANT_NAME, type="run", root=True)
async def run(thread_id: str, human_query: str, file_ids: List[str]):
    return await step_logic(thread_id, human_query, file_ids, client)


@cl.on_message
async def on_message(message_from_ui: cl.Message):
    thread: Thread = cl.user_session.get("thread")
    try:
        files_ids: List[str] = await process_files(message_from_ui.elements)
        await run(
            thread_id=thread.id, human_query=message_from_ui.content, file_ids=files_ids
        )
    except BadRequestError as e:
        logger.error(e)
        # This exposes OAI to user, might want to throw a custom error here
        await cl.Message(author='System', content=e.body['message']).send()
