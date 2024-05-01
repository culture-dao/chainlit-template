import asyncio
import logging
from typing import List

from openai.pagination import AsyncCursorPage
from openai.types.beta import Assistant

from utils.openai_handler import OpenAIHandler
from utils.openai_utils import client, AsyncPaginatorHelper

logger = logging.getLogger("chainlit")

ASSISTANT_CONFIG_PATH = 'assistant.yaml'


class AssistantHandler(OpenAIHandler):

    async def list(self):
        return await assistants_list()

    async def create(self, config):
        return await assistants_create(config)

    async def retrieve(self, assistant_id):
        return await assistant_retrieve(assistant_id)

    async def update(self, item_id):
        pass


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
        logger.error({e})
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


async def main() -> AssistantHandler:
    """
    This function returns a dictionary of Assistants.
    It looks for an existing config file and loads it.
    If one is not found, it will pull existing Assistants from OAI and dump them to a config.
    If no assistants are found, it will create our template assistant and save that to file.
    :return:
    """

    return await AssistantHandler(ASSISTANT_CONFIG_PATH, Assistant).init()

if __name__ == '__main__':
    assistants = asyncio.run(main())
    liminal_flow = assistants.find_by_name("Liminal Flow Agent")
    pass
