import logging

import chainlit as cl
from dotenv import load_dotenv

from test.fixture import message_with_citation, \
    message_no_citation, message_with_invalid_index, message_with_multiple_annotations_no_quotes, \
    message_with_multiple_annotations, message_with_no_quote
from utils.annotations import OpenAIAdapter

logging.basicConfig(level=logging.INFO)

load_dotenv(dotenv_path='../../.env', override=True)

annotations_fixtures = [message_with_citation,  # 1
                        message_with_invalid_index,  # 0
                        message_no_citation,  # 0
                        message_with_multiple_annotations_no_quotes,  # 0
                        message_with_multiple_annotations,  # 3
                        message_with_no_quote  # 0
                        ]


# File IDs are not valid, so footnotes do not appear.
@cl.on_chat_start
async def on_chat_start():
    for i, message in enumerate(annotations_fixtures, start=1):
        logging.info(len(message.content[0].text.annotations))
        # Send initial message
        await cl.Message(content=f"Message {i}").send()

        # Adapt the message using OpenAIAdapter
        adapter = OpenAIAdapter(message)
        await adapter.main()

        # Get and send the adapted content
        content = adapter.get_content()
        await cl.Message(content=content).send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
