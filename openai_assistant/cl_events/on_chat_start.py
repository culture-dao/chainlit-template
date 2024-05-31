import os

import chainlit as cl
from openai.types.beta import Thread

from utils.assistant_handler import assistant_handler


async def on_start_chat_logic(client):
    await assistant_handler.init()
    assistant_name = os.getenv('ASSISTANT_NAME')
    assistant = assistant_handler.find_by_name(assistant_name)
    cl.user_session.set("assistant", assistant)

    # Create a new thread with the OpenAI API
    thread: Thread = await client.beta.threads.create()
    cl.user_session.set("thread", thread)

    # Send the initial welcome message to the user
    await cl.Message(author="Chatbot", content="Hi, I am ready. What is your query?").send()
