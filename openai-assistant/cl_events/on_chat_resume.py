import json
import chainlit as cl
from chainlit import ThreadDict, logger


async def on_chat_resume_logic(thread: ThreadDict, client):
    steps = thread.get('steps')

    # Find the right step that has the thread id we need.
    # Once found, retrieve it and pass it to the  on_message function.
    # Since we retrieved it and it's a thread, no modifications are needed to on_message.
    for step in steps:
        if step['input'] != '':
            parsed_input = json.loads(step['input'])
            kwargs = parsed_input.get('kwargs', {})
            thread_id = kwargs.get('thread_id', None)
            logger.info(f"Resuming chat with thread ID: {thread_id}")
            thread = await client.beta.threads.retrieve(thread_id)
            break
    if thread.id is None:
        response_content = "The old thread could not be fetched."
    else:
        response_content = "Welcome back! I'm ready to assist you. How can I help you today?"
    cl.user_session.set("thread", thread)
    await cl.Message(author="AFGE V.S.", content=response_content).send()
