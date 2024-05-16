import json
import chainlit as cl
from chainlit import ThreadDict, logger
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
            logger.info(f"Resuming chat with thread ID: {thread_id}")
            try:
                thread = await client.beta.threads.retrieve(thread_id)
                if thread.id is None:
                    pass
                else:
                    cl.user_session.set("thread", thread)
                    response_content = "Welcome back! I'm ready to assist you. How can I help you today?"
            except NotFoundError:
                pass
            break
    logger.info(response_content)
    await cl.Message(content=response_content).send()
