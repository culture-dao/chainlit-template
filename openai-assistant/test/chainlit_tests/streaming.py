"""
This is for testing the annotations or whatever other display functionality is needed
"""
import logging
import chainlit as cl
from dotenv import load_dotenv

from utils.event_handler import EventHandler
from utils.openai_utils import initialize_openai_client
from cl_events.step import process_thread_message
logging.basicConfig(level=logging.INFO)

load_dotenv(dotenv_path='../', override=True)


@cl.on_chat_start
async def on_chat_start():
    client = initialize_openai_client('../../.env')
    thread = await client.beta.threads.create()

    question = 'Search the docs and tell me something about it.'

    # Make sure it has an initial message, so it does not hallucinate
    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
    )

    cl_message = cl.Message(content=question, author="User")
    await cl_message.send()

    e = EventHandler()

    async with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id='asst_2lanl1dvlTkCpOofxiPrHvzr',
            instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=e
    ) as stream:
        await stream.until_done()

    await process_thread_message(e.message_references, e.openAIMessage, client)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
