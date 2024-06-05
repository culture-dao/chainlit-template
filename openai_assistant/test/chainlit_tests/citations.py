import logging
import os

import chainlit as cl
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)

load_dotenv(dotenv_path='../../.env', override=True)

assistant_id = os.getenv('TEST_ASSISTANT_ID')


@cl.on_chat_start
async def on_chat_start():
    # Send a response back to the user with superscript text
    await cl.Message(
        content = "Some text",
        elements=[
            cl.Text(name="markdown_text", content="[1]", display="inline")
        ],
    ).send()

    await cl.Message(
        content="$^{[1]}$"
    ).send()
    await cl.Message(
        content="8\\textsuperscript{th} 8th"
    ).send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
