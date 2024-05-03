import chainlit as cl
from openai.types.beta import Thread

from utils.assistant_handler import assistant_handler


async def on_start_chat_logic(client):
    await assistant_handler.init()
    # Create a new thread with the OpenAI API
    thread: Thread = await client.beta.threads.create()
    cl.user_session.set("thread", thread)

    # Send the initial welcome message to the user
    await cl.Message(author="Liminal Flow Agent", content="Hi, I am the test agent. What's up?").send()
