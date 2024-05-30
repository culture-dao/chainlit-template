import json

import chainlit as cl
from chainlit.types import ThreadDict
from chainlit.logger import logger
from openai import NotFoundError


async def on_chat_resume_logic(cl_thread: ThreadDict, client):
    oai_thread_id = get_thread_id(cl_thread)

    if oai_thread_id:
        await retrieve_thread(oai_thread_id, client)
        response_content = "Welcome back! I'm ready to assist you. How can I help you today?"
    else:
        response_content = "The old thread could not be fetched."

    return await cl.Message(content=response_content).send()


def get_thread_id(cl_thread: ThreadDict) -> str:
    """
    Given the datalayer thread object, find the associated OIA Thread ID.
    :param cl_thread:
    :return: The OAI thread ID
    """

    steps = cl_thread.get('steps')
    for step in steps:
        if step['type'] == 'run':
            parsed_input = json.loads(step['input'])
            kwargs = parsed_input.get('kwargs', {})
            thread_id = kwargs.get('thread_id', None)
            if thread_id is None:
                raise Exception("THREAD ID IS NONE")
            return thread_id
    raise Exception("THREAD ID NOT FOUND")


async def retrieve_thread(thread_id, client) -> None:

    if thread_id is not None:
        logger.info(f"Resuming chat with thread ID: {thread_id}")
        try:
            thread = await client.beta.threads.retrieve(thread_id)
            cl.user_session.set("thread", thread)
        except NotFoundError as e:
            logger.error(f"THREAD NOT FOUND: {e}")
            raise ValueError("Thread ID is no longer accessible.")
