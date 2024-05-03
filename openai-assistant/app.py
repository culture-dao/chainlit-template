import logging
from typing import List

import chainlit as cl
from chainlit.types import ThreadDict
from literalai import Thread
from openai.types.beta.vector_stores import VectorStoreFile

from chainlit_utils import process_files
from cl_events.on_chat_resume import on_chat_resume_logic
from cl_events.on_chat_start import on_start_chat_logic
from cl_events.step import step_logic
from utils.openai_utils import client

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("chainlit")


@cl.on_chat_start
async def on_chat_start_callback():
    return await on_start_chat_logic(client)


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
# TODO: Name should be dynamic?
def rename(orig_author: str):
    rename_dict = {"assistant": "Liminal FLow"}
    return rename_dict.get(orig_author, orig_author)


@cl.on_chat_resume
async def on_chat_resume_callback(thread: ThreadDict):
    return await on_chat_resume_logic(thread, client)


@cl.step(name="Assistant", type="run", root=True)
async def run(thread_id: str, human_query: str, file_ids: List[VectorStoreFile]):
    return await step_logic(thread_id, human_query, file_ids, client)


@cl.on_message
async def on_message(message_from_ui: cl.Message):
    thread: Thread = cl.user_session.get("thread")
    files_ids: List[VectorStoreFile] = await process_files(message_from_ui.elements)

    await run(
        thread_id=thread.id, human_query=message_from_ui.content, file_ids=files_ids
    )
