from openai.types.beta import Thread
import chainlit as cl


async def on_start_chat_logic(client):
    # Create a new thread with the OpenAI API
    thread = await client.beta.threads.create()  # type: Thread
    cl.user_session.set("thread", thread)

    # Send the initial welcome message to the user
    await cl.Message(author="AFGE V.S.", content="Hi, I am the AFGE virtual steward! How can I help you today?").send()
