import asyncio
import logging
from typing import List

from openai.pagination import AsyncCursorPage
from openai.types.beta import Assistant
from openai.types.beta.assistant_update_params import ToolResourcesFileSearch, AssistantUpdateParams, ToolResources

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


async def assistants_list() -> List[Assistant]:
    assistants: AsyncCursorPage[Assistant] = await client.beta.assistants.list()
    return await AsyncPaginatorHelper.collect_all_items(assistants)


async def assistants_create(config) -> Assistant:
    return await client.beta.assistants.create(
        **config
    )


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


async def assistant_update(assistant_id, config) -> Assistant:
    try:
        return await client.beta.assistants.update(assistant_id, **config)
    except Exception as e:
        logging.error(f"Failed to update vector_stores due to an error: {e}")
        raise Exception("vector_stores_update failed") from e


async def attach_file_search(assistant_id, vector_store_id=None) -> Assistant:
    if vector_store_id is None:
        # get "Default Datastore"
        vector_store_id = 'vs_ZpE5J5qh5KMRMrwXkzsAxobM'
    tool = ToolResourcesFileSearch(vector_store_ids=[vector_store_id])
    tool_resources = ToolResources(file_search=tool)
    config = AssistantUpdateParams(tool_resources=tool_resources)
    result = await assistant_update(assistant_id, config)
    assert result.tool_resources.file_search
    return result


async def main() -> AssistantHandler:
    """
    This function returns a dictionary of Assistants.
    It looks for an existing config file and loads it.
    If one is not found, it will pull existing Assistants from OAI and dump them to a config.
    If no assistants are found, it will create our template assistant and save that to file.
    :return:
    """

    assistants = await AssistantHandler(ASSISTANT_CONFIG_PATH, Assistant).init()

    liminal_flow: Assistant = assistants.find_by_name("Liminal Flow Agent")
    if not liminal_flow.tool_resources.file_search:
        liminal_flow = await attach_file_search(liminal_flow)

    assistants["Liminal Flow Agent"] = liminal_flow

    return assistants


if __name__ == '__main__':
    assistants = asyncio.run(main())
