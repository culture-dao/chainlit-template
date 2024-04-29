import json
import logging

from typing import Dict, Any, Optional

import yaml
from openai.types.beta import Assistant
from pydantic import ValidationError

from utils.openai_utils import client

ASSISTANT_NAME = "My Assistant"

logger = logging.getLogger("chainlit")


def load_json(filename: str) -> Dict[str, Any]:
    """
        Loads a JSON object from a file.

        Args:
            filename: The name of the file to load the JSON from.

        Returns:
            The JSON object loaded from the file if it exists, otherwise an empty dictionary.
        """
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


def main():
    result = load_yaml('liminal_flow.yml')
    pass


if __name__ == '__main__':
    main()
