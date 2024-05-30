import json
import chainlit as cl
from chainlit.types import ThreadDict
from chainlit.logger import logger
from openai import NotFoundError


async def on_chat_resume_logic(cl_thread: ThreadDict, client):
    steps = cl_thread.get('steps')
    response_content = "The old thread could not be fetched."
    # Find the right step that has the thread id we need.
    # Once found, retrieve it and set it in the session.
    for step in steps:
        if step['type'] == 'run':
            parsed_input = json.loads(step['input'])
            kwargs = parsed_input.get('kwargs', {})
            thread_id = kwargs.get('thread_id', None)
            if thread_id is not None:
                logger.info(f"Resuming chat with thread ID: {thread_id}")
                try:
                    thread = await client.beta.threads.retrieve(thread_id)
                    if thread.id:
                        cl.user_session.set("thread", thread)
                        response_content = "Welcome back! I'm ready to assist you. How can I help you today?"
                except NotFoundError as e:
                    raise ValueError("Thread ID is no longer accessible.")
    logger.info(response_content)
    return await cl.Message(content=response_content).send()
