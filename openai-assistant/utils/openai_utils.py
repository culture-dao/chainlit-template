import asyncio
import json
import os

import openai
from chainlit.logger import logger
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.beta import Thread


def initialize_openai_client() -> AsyncOpenAI:
    """
    Initializes and returns an OpenAI client using the API key from environment variables.

    Returns:
        openai.OpenAI: The initialized OpenAI client.

    Raises:
        ValueError: If the OpenAI API key is not found in the environment variables.
        Exception: If there is an issue initializing the OpenAI client.
    """
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        logger.error("OpenAI API key not found. Please check your environment variables.")
        raise ValueError("OpenAI API key not found")

    try:
        return openai.AsyncOpenAI()
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        raise


def get_playground_url(assistant_id, thread_id) -> None:
    """
    Returns the URL for the OpenAI Playground.

    Returns:
        str: The URL for the OpenAI Playground.
    """
    playground_url = f'https://platform.openai.com/playground?assistant={assistant_id}&mode=assistant&thread={thread_id}'
    logger.info(f'THREAD URL: {playground_url}')


async def get_thread_messages(client: AsyncOpenAI, thread_id) -> Thread:
    """
    Wrapper function for OAI message retrieval
    """
    try:
        thread = await client.beta.threads.messages.list(thread_id)
        return thread
    except Exception as e:
        logger.error(f"Error retrieving thread: {e}")
        raise


def update_file_map(client, file='assistants.json'):
    file_map = get_file_map(file)
    assistant_id = file_map.get("AFGE Virtual Steward")

    if assistant_id is not None:
        assistant = client.beta.assistants.retrieve(assistant_id)

        file_path_mapping = {}
        for root, dirs, files_in_dir in os.walk("public"):
            for filename in files_in_dir:
                file_path_mapping[filename] = os.path.join(root, filename)

        updated_file_map = {"AFGE Virtual Steward": assistant_id}
        for file_id in assistant.file_ids:
            if file_id not in file_map:
                file_details = client.files.retrieve(file_id)
                filename = getattr(file_details, 'filename', '')

                if filename in file_path_mapping:
                    file_path = file_path_mapping[filename]
                    updated_file_map[file_id] = {"name": filename, "file_path": file_path}

        with open(file, 'w') as f:
            json.dump(updated_file_map, f, indent=4)
    else:
        logger.info(f"Key 'AFGE Virtual Steward' not found in {file}.")


def get_file_map(file='assistants.json'):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    else:
        logger.info(f"No {file} found..")
        return {}


if __name__ == "__main__":
    client = openai.AsyncClient()
    buggy_thread = 'thread_id'
    messages = asyncio.run(get_thread_messages(client, buggy_thread))
    # Save your message as a fixture, whatever
    pass
