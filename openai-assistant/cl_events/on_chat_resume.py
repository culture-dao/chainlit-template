import json

import chainlit as cl
from chainlit import ThreadDict, logger


async def on_chat_resume_logic(thread: ThreadDict, client) -> None:
    """
    This function needs to make sure we can retrieve the original OAI Thread
    """

    steps = thread.get('steps')

    for step in steps:
        thread = await try_step(step, client)
        if thread:
            break

    if thread.id is None:
        response_content = "The old thread could not be fetched."
    else:
        response_content = "Welcome back! I'm ready to assist you. How can I help you today?"
    cl.user_session.set("thread", thread)

    await cl.Message(content=response_content).send()


async def try_step(step, client):
    if step['type'] == 'run':
        try:
            parsed_input = json.loads(step['input'])
            kwargs = parsed_input.get('kwargs', {})
            thread_id = kwargs.get('thread_id', None)
            logger.info(f"Resuming chat with thread ID: {thread_id}")
            return await client.beta.threads.retrieve(thread_id)

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
