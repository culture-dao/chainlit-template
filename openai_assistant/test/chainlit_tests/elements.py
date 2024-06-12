"""
This is for testing the annotations or whatever other display functionality is needed
"""

import chainlit as cl

from test.fixture import message_with_multiple_annotations_no_quotes, message_no_citation, message_with_invalid_index, \
    message_with_citation, message_with_multiple_annotations
from utils.annotations import OpenAIAdapter


@cl.on_chat_start
async def on_chat_start():
    """
    There is a FE bug here where the annotations don't render in order all the time.
    """
    value = ("""
        # Version 1

Message content, blah blah [1] blah [2]

> [Source doc 1](doc1.pdf): Quote or no quote
> [Source doc 2](doc2.pdf): Quote or no quote
 
# Version 2
Some text with [a link][1] and
another [link][2].

[1]: http://example.com/ "Title"
[2]: http://example.org/ "Title"

# Version 3

I have more [^1] to say up here.
[^1]: To say down here.
        """
             )

    await cl.Message(
        content=value,
    ).send()

    # messages = [
    #     message_no_citation,
    #     message_with_citation,
    #     message_with_invalid_index,
    #     message_with_multiple_annotations_no_quotes,
    #     message_with_multiple_annotations
    # ]
    # for thread_message in messages:
    #     adapter = OpenAIAdapter(thread_message)
    #     await adapter.main()
    #     await adapter.get_message().send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
