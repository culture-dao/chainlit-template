"""
Dev/Integration test with sample OAI call to CL output.
BEWARE: if you have multiple browser tabs open, then will all refresh,
and you'll see multiple runs and messages being passed through.

"""
import logging

import chainlit as cl
from dotenv import load_dotenv

from utils.event_handler import EventHandler
from utils.openai_utils import initialize_openai_client, get_playground_url

logging.basicConfig(level=logging.INFO)

load_dotenv(dotenv_path='../', override=True)

assistant_id = 'asst_2lanl1dvlTkCpOofxiPrHvzr'


@cl.on_chat_start
async def on_chat_start():
    client = initialize_openai_client()
    thread = await client.beta.threads.create()

    logging.info(get_playground_url(thread.id, assistant_id))

    # The question to ask the model
    question = 'Search the docs and tell me something about it.'

    # Make sure it has an initial message, so it does not hallucinate
    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
    )

    # Send the original question and display as 'User'
    cl_message = cl.Message(content=question, author="User")
    await cl_message.send()

    # Dummy message to start the step
    await cl.Message(content='').send()
    e: EventHandler = EventHandler(client=client)

    # Process the question and display the question in the UI
    async with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions="Search the file and describe it in less than 20 words.",
            event_handler=e
    ) as stream:
        await stream.until_done()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
