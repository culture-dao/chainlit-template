from openai.types.beta import Thread
import chainlit as cl


async def on_start_chat_logic(client):
    # Create a new thread with the OpenAI API
    thread: Thread = await client.beta.threads.create()
    cl.user_session.set("thread", thread)

    # Send the initial welcome message to the user
    await cl.Message(author="Chatbot", content="Hi, I am ready. What is your query?").send()