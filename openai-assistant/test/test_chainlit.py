"""
This is for testing the annotations or whatever other display functionality is needed
"""

import chainlit as cl

from test.fixture import mock_message_with_multiple_annotations, message_no_citation, message_with_citation_2, \
    message_with_citation
from utils.annotations import build_message_with_annotations


@cl.on_chat_start
async def on_chat_start():
    """
    There is a FE bug here where the annotations don't render in order all the time.
    """
    value = "This is a message with a citation[1]. There can be multiple ones in a document[2][3]"
    annotations = [
        cl.Text(name="[1] Annotation Source", content='content of annotation', display="inline"),
        cl.Text(name="[2] Annotation Source", content='content of annotation', display="inline"),
        cl.Text(name="[3] Annotation Source", content='content of annotation', display="inline"),
    ]

    await cl.Message(
        content=value,
        elements=annotations,
    ).send()

    messages = [
        message_no_citation,
        message_with_citation,
        message_with_citation_2,
        mock_message_with_multiple_annotations
    ]
    for thread_message in messages:
        cl_message = build_message_with_annotations(thread_message)
        await cl_message.send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
