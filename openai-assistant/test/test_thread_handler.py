import logging

import chainlit as cl
from utils.annotations import OpenAIAdapter
from utils.openai_utils import get_thread_messages, initialize_openai_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chainlit")

client = initialize_openai_client()


@cl.on_chat_start
async def on_chat_start():
    messages = await get_thread_messages(client, 'thread_J05pHO7SIE0HWqQZJymAdo8Q')
    logger.info(messages.data)
    for thread_message in messages.data:
        message = OpenAIAdapter(thread_message)
        await message.set_citations()
        cl_message = message.get_message()

        logger.info(cl_message.elements)
        await cl_message.send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
