import base64
import logging
import os
from io import BytesIO
from typing import List

import chainlit as cl

from chainlit.element import ElementBased
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


@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    if chunk.isStart:
        buffer = BytesIO()
        buffer.name = f"input_audio.{chunk.mimeType.split('/')[1]}"
        cl.user_session.set("audio_buffer", buffer)
        cl.user_session.set("audio_mime_type", chunk.mimeType)
    cl.user_session.get("audio_buffer").write(chunk.data)


@cl.on_audio_end
async def on_audio_end(elements: list[ElementBased]):
    audio_buffer: BytesIO = cl.user_session.get("audio_buffer")
    audio_buffer.seek(0)
    audio_file = audio_buffer.read()
    audio_mime_type: str = cl.user_session.get("audio_mime_type")

    input_audio_el = cl.Audio(
        mime=audio_mime_type, content=audio_file, name=""
    )

    await cl.Message(
        author="You",
        content="",
        type="user_message",
        elements=[input_audio_el, *elements]
    ).send()

    whisper_input = (audio_buffer.name, audio_file, audio_mime_type)
    transcription = await speech_to_text(whisper_input)

    message = await cl.Message(
        author="You",
        type="user_message",
        content=transcription,
        elements=[]
    ).send()

    await on_message(message)


@cl.step(type="tool", name="Transcription")
async def speech_to_text(audio_file):
    current_step = cl.context.current_step
    try:
        current_step.output = "Running transcription..."
        await current_step.update()

        response = await client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )

        current_step.output = "Transcription completed"
        await current_step.update()

        return response.text

    except Exception as e:
        error_message = f"Error during transcription: {str(e)}"
        current_step.output = error_message
        await current_step.update()
        return error_message


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
