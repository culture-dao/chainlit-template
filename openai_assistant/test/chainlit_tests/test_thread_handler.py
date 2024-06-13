import logging

import chainlit as cl
from utils.annotations import OpenAIAdapter
from utils.openai_utils import get_thread_messages, initialize_openai_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chainlit")

client = initialize_openai_client()


@cl.on_chat_start
async def on_chat_start():
    messages = await get_thread_messages(client, 'thread_pyYV3psCkuoIr3VylFoa0uQ4')
    logger.info(messages.data)
    for thread_message in messages.data:
        # Adapt the message using OpenAIAdapter
        adapter = OpenAIAdapter(thread_message)
        await adapter.main()
        # Get and send the adapted content
        content = adapter.get_content()
        await cl.Message(content=content).send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
