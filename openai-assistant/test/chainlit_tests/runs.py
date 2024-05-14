"""
This is for testing the annotations or whatever other display functionality is needed
"""
import logging
import chainlit as cl
from dotenv import load_dotenv
from openai.types.beta.threads.runs import ToolCall, FileSearchToolCall

from utils.event_handler import EventHandler
from utils.openai_utils import initialize_openai_client
from cl_events.step import process_thread_message
logging.basicConfig(level=logging.INFO)

load_dotenv(dotenv_path='../', override=True)


@cl.on_chat_start
async def on_chat_start():
    # client = initialize_openai_client('../../.env')
    # thread = await client.beta.threads.create()
    #
    # question = 'Search the docs and tell me something about it.'
    #
    # # Make sure it has an initial message, so it does not hallucinate
    # await client.beta.threads.messages.create(
    #     thread_id=thread.id,
    #     role="user",
    #     content=question,
    # )

    cl_message = cl.Message(content='here we go', author="User")
    await cl_message.send()

    e = EventHandler()

    file_search_tool_call = FileSearchToolCall.model_construct(type='file_search')

    await e.on_tool_call_created(file_search_tool_call)

if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
