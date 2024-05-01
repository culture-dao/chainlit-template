import asyncio
import logging


from typing import List

import yaml
from openai.pagination import AsyncCursorPage
from openai.types.beta import Assistant

from utils.openai_utils import client, load_yaml, AsyncPaginatorHelper, list_to_dict

logger = logging.getLogger("chainlit")

ASSISTANT_CONFIG_PATH = 'assistant.yaml'


async def assistant_retrieve(assistant_id: str) -> Assistant:
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
        logger.error(f"An unexpected error occurred: {e}")
        raise


async def assistants_list() -> List[Assistant]:
    assistants: AsyncCursorPage[Assistant] = await client.beta.assistants.list()
    return await AsyncPaginatorHelper.collect_all_items(assistants)


async def assistants_create(config) -> Assistant:
    return await client.beta.assistants.create(
        **config
    )


async def main() -> List[Assistant]:
    """
    This function returns a dictionary of Assistants.
    It looks for an existing config file and loads it.
    If one is not found, it will pull existing Assistants from OAI and dump them to a config.
    If no assistants are found, it will create our template assistant and save that to file.
    :return:
    """
    # Import our existing config file
    results = load_yaml(ASSISTANT_CONFIG_PATH, Assistant)
    if not results:
        # No config, load from OAI
        assistants = await assistants_list()
        results = list_to_dict(assistants)
        if not results:
            # No agents, load template
            results = load_yaml('liminal_flow.yml')
            for i in results.keys():
                assistant = results[i]
                if not assistant.id:
                    results[i] = await assistants_create(assistant.to_dict())
        with open(ASSISTANT_CONFIG_PATH, 'w') as f:
            yaml.dump(results, f)
    return results

if __name__ == '__main__':
    asyncio.run(main())
