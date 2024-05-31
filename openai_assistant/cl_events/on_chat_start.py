import chainlit as cl
from openai.types.beta import Thread

from utils.assistant_handler import assistant_handler


async def on_start_chat_logic(client, assistant_name):
    await assistant_handler.init()
    assistant = assistant_handler.find_by_name(assistant_name)
    cl.user_session.set("assistant_id", assistant.id)

    # Create a new thread with the OpenAI API
    thread: Thread = await client.beta.threads.create()
    cl.user_session.set("thread", thread)

    # Send the initial welcome message to the user
    await cl.Message(author="Chatbot", content="Hi, I am ready. What is your query?").send()
