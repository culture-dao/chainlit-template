import asyncio
import json
import logging
import os
from typing import TypeVar, Generic, List, Dict, Any, Type

import httpx
import openai
import yaml
from chainlit.logger import logger
from openai import AsyncOpenAI, DefaultHttpxClient, DefaultAsyncHttpxClient
from openai.pagination import AsyncPage
from openai.types.beta import Thread
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')

T = TypeVar('T')


class CustomHttpxClient(DefaultAsyncHttpxClient):
    def __init__(self, **kwargs):
        # kwargs.setdefault("timeout", httpx.Timeout(10.0, read=5.0, write=5.0))
        # kwargs.setdefault("limits", httpx.Limits(max_keepalive_connections=10, max_connections=100))
        super().__init__(**kwargs)

        # Add retry logic to the transport
        transport = httpx.AsyncHTTPTransport(retries=10)
        self._transport = transport


class AsyncPaginatorHelper(Generic[T]):
    """
    AsyncPage objects are limited to 100 results, 20 default, so we'll need pagination handling on the 'list' functions.
    """
    @staticmethod
    async def collect_all_items(paginator: AsyncPage[T]) -> List[T]:
        items = []
        async for item in paginator:
            logging.info(item)
            items.append(item)
        return items


def initialize_openai_client() -> AsyncOpenAI:
    """
    Initializes and returns an OpenAI client using the API key from environment variables.

    Returns:
        openai.OpenAI: The initialized OpenAI client.

    Raises:
        ValueError: If the OpenAI API key is not found in the environment variables.
        Exception: If there is an issue initializing the OpenAI client.
    """
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not openai.api_key:
        logger.error("OpenAI API key not found. Please check your environment variables.")
        raise ValueError("OpenAI API key not found")
    try:
        http_client = CustomHttpxClient()
        return openai.AsyncOpenAI(http_client=http_client)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        raise


# client = initialize_openai_client()


def get_playground_url(assistant_id, thread_id) -> None:
    """
    Returns the URL for the OpenAI Playground.

    Returns:
        str: The URL for the OpenAI Playground.
    """
    playground_url = f'https://platform.openai.com/playground?assistant={assistant_id}&mode=assistant&thread={thread_id}'
    logger.info(f'THREAD URL: {playground_url}')


async def get_thread_messages(client: AsyncOpenAI, thread_id) -> Thread:
    # TODO: Move to thread handler, get rid of client
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
    # Broken
    file_map = get_file_map(file)
    assistant_id = file_map.get("Assistant name")

    if assistant_id is not None:
        assistant = client.beta.assistants.retrieve(assistant_id)

        file_path_mapping = {}
        for root, dirs, files_in_dir in os.walk("public"):
            for filename in files_in_dir:
                file_path_mapping[filename] = os.path.join(root, filename)

        updated_file_map = {"Assistant name": assistant_id}
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
        logger.info(f"Key 'Assistant name' not found in {file}.")


def get_file_map(file='assistants.json'):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    else:
        logger.info(f"No {file} found..")
        return {}


def load_or_create_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)
    else:
        with open(filename, 'w') as file:
            return {}


def load_json(filename: str) -> Dict[str, Any]:
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"{filename} not found.")
        return {}


def load_yaml(filename: str, model: Type[BaseModel]) -> Dict[str, BaseModel]:
    """
    Originally used to import Assistant models from yaml config
    There is no validation on the objects
    """
    try:
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
            # Check if data is a dictionary and if so, create Type instances
            if isinstance(data, dict):
                return {key: model.model_construct(**value) for key, value in data.items()}
    except FileNotFoundError:
        logger.error(f"{filename} not found.")
        return {}


def list_to_dict(_list: list[[BaseModel]]) -> dict[str, object]:

    _dict = {}

    for obj in _list:
        _dict[obj.name] = obj

    return _dict


if __name__ == "__main__":
    buggy_thread = 'thread_id'
    messages = asyncio.run(get_thread_messages(client, buggy_thread))
    # Save your message as a fixture, whatever
    pass
