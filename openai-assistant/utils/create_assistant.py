import asyncio
import json
import logging
import os

from typing import Dict, Any, Optional

import yaml
from openai.pagination import AsyncCursorPage
from openai.resources.beta import AsyncAssistants
from openai.types.beta import Assistant

from utils.openai_utils import client

ASSISTANT_NAME = "My Assistant"

logger = logging.getLogger("chainlit")


ASSISTANT_CONFIG_PATH = 'assistant.yaml'


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


def load_yaml(filename: str) -> Dict[str, Any]:
    try:
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
            # Check if data is a dictionary and if so, create Assistant instances
            if isinstance(data, dict):
                return {key: Assistant.model_construct(**value) for key, value in data.items()}
    except FileNotFoundError:
        logger.error(f"{filename} not found.")
        return {}


def get_assistant_id(assistant_name: str = ASSISTANT_NAME) -> Optional[str]:
    """
    Retrieves the assistant ID by name from the loaded assistant dictionary.

    Args:
        assistant_name: The name of the assistant to retrieve the ID for. Defaults to ASSISTANT_NAME.

    Returns:
        The assistant ID if present in the dictionary, otherwise None.
    """
    # we're running into path issues with the test files.
    assistant_dict = load_json("assistants.json")
    return assistant_dict.get(assistant_name)


async def retrieve_assistant(assistant_id: str) -> Assistant:
    """
        Retrieves and logs details about an existing assistant by its ID.

        This async function attempts to retrieve an assistant using an API call.
        If successful, it logs the assistant's name and file count. If it fails,
        it logs the error encountered.

        Args:
            assistant_id: The ID of the assistant to retrieve.

        Returns:
            The retrieved assistant object on success, None on failure.
    """
    from openai import NotFoundError
    try:
        assistant = await client.beta.assistants.retrieve(assistant_id)
        logger.info(f"Retrieved existing assistant: {assistant.name}")
        return assistant
    except NotFoundError as e:
        logger.error({e.body['message']})
        raise
    except Exception as e:
        # A fallback for any unexpected exceptions
        logger.error(f"An unexpected error occurred: {e}")
        # Consider re-raising the exception after logging to make the problem noticeable
        raise


async def get_assistants():
    config_path = ASSISTANT_CONFIG_PATH
    load_or_create_file(config_path)
    assistants: AsyncCursorPage[Assistant] = await AsyncAssistants(client).list()

    assistants_dict = {}
    assistant: Assistant
    for assistant in assistants.data:
        assistants_dict[assistant.id] = assistant.dict()

    with open(config_path, 'w') as f:
        yaml.dump(assistants_dict, f)

    return assistants_dict


async def create_assistant(config) -> Assistant:
    return await client.beta.assistants.create(
        **config
    )


async def main():
    # Import our existing config file
    results = load_yaml(ASSISTANT_CONFIG_PATH)
    if not results:
        # No config, load from OAI
        results = await get_assistants()
    if not results:
        # No agents, load template
        results = load_yaml('liminal_flow.yml')
        for i in results.keys():
            assistant = results[i]
            if not assistant.id:
                results[i] = await create_assistant(assistant.to_dict())
        with open(ASSISTANT_CONFIG_PATH, 'w') as f:
            yaml.dump(results, f)


if __name__ == '__main__':
    asyncio.run(main())
