import logging
from typing import Dict, List, Optional

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


@cl.oauth_callback
async def oauth_callback(provider_id: str, token: str, raw_user_data: Dict[str, str], default_app_user: cl.User) -> \
        Optional[cl.User]:
    return await oauth_callback_logic(provider_id, token, raw_user_data, default_app_user)


@cl.on_chat_start
async def on_chat_start_callback():
    return await on_start_chat_logic(client)


@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"assistant": "ASSISTANT NAME"}
    return rename_dict.get(orig_author, orig_author)


@cl.on_chat_resume
async def on_chat_resume_callback(thread: ThreadDict):
    return await on_chat_resume_logic(thread, client)


@cl.step(name="Assistant", type="run", root=True)
async def run(thread_id: str, human_query: str, file_ids: List[str] = []):
    return await step_logic(thread_id, human_query, file_ids, client)


@cl.on_message
async def on_message(message_from_ui: cl.Message):
    thread: Thread = cl.user_session.get("thread")
    files_ids = await process_files(message_from_ui.elements)

    # Initialize or retrieve message history from session
    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message_from_ui.content})
    cl.user_session.set("message_history", message_history)

    await run(
        thread_id=thread.id, human_query=message_from_ui.content, file_ids=files_ids
    )

    # Create a new message object for streaming completion output
    msg = cl.Message(content="")
    await msg.send()

    # Settings for the streaming completions should be defined (customize as needed)
    settings = {
        "model": "gpt-3.5-turbo",  # Update model as per your requirement
        "max_tokens": 150,  # Adjust based on your use case
        "temperature": 0.7  # Adjust to control randomness
    }

    # Start streaming completions
    stream = await client.chat.completions.create(
        messages=message_history,
        stream=True,
        **settings
    )

    # Stream tokens as they are generated
    async for part in stream:
        if token := part.choices[0].delta.content:
            print("Streaming token:", token)
            await msg.stream_token(token)

    # Update message history with the response from the assistant
    message_history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("message_history", message_history)

    # Final update to the message sent to the user
    await msg.update()
