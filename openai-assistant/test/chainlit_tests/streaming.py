"""
This is for testing the annotations or whatever other display functionality is needed
"""

import chainlit as cl
from openai import AsyncOpenAI

from utils.event_handler import EventHandler


@cl.on_chat_start
async def on_chat_start():
    client = AsyncOpenAI()
    thread = await client.beta.threads.create()
    async with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id='asst_GPa9ziLBlAg4gmZXCq6L5nF9',
            instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=EventHandler(),
    ) as stream:
        await stream.until_done()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
