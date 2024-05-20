import logging
from typing import List, Dict, Optional

import chainlit as cl
from literalai import Thread
from chainlit_utils import process_files
from chainlit.types import ThreadDict

from cl_events.oauth_callback import oauth_callback_logic
from cl_events.on_chat_start import on_start_chat_logic
from cl_events.on_chat_resume import on_chat_resume_logic
from cl_events.step import step_logic
from utils.openai_utils import initialize_openai_client


logging.basicConfig(level=logging.INFO)

client = initialize_openai_client()

logger = logging.getLogger("chainlit")

ASSISTANT_NAME = "DEMO AGENT"

@cl.oauth_callback
async def oauth_callback(provider_id: str, token: str, raw_user_data: Dict[str, str], default_app_user: cl.User) -> \
        Optional[cl.User]:
    return await oauth_callback_logic(provider_id, token, raw_user_data, default_app_user)


@cl.on_chat_start
async def on_chat_start_callback():
    return await on_start_chat_logic(client)


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Chatbot": ASSISTANT_NAME}
    return rename_dict.get(orig_author, orig_author)


@cl.on_chat_resume
async def on_chat_resume_callback(thread: ThreadDict):
    return await on_chat_resume_logic(thread, client)


@cl.step(name=ASSISTANT_NAME, type="run", root=True)
async def run(thread_id: str, human_query: str, file_ids: List[str] = []):
    return await step_logic(thread_id, human_query, file_ids, client)


@cl.on_message
async def on_message(message_from_ui: cl.Message):
    thread: Thread = cl.user_session.get("thread")
    files_ids = await process_files(message_from_ui.elements)

    await run(
        thread_id=thread.id, human_query=message_from_ui.content, file_ids=files_ids
    )
