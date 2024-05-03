import asyncio
import logging
from typing import List, Iterable

from openai.pagination import AsyncCursorPage
from openai.types.beta import Assistant, AssistantToolParam, FileSearchToolParam
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
    try:
        assistants: AsyncCursorPage[Assistant] = await client.beta.assistants.list()
        return await AsyncPaginatorHelper.collect_all_items(assistants)
    except Exception as e:
        logging.error(f"Failed to list assistants due to an error: {e}")
        raise Exception("assistants_list failed") from e


async def assistants_create(config=None) -> Assistant:
    try:
        return await client.beta.assistants.create(**config)
    except Exception as e:
        logging.error(f"Failed to create vector_stores due to an error: {e}")
        raise Exception("vector_stores_create failed") from e


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
        logging.error(f"Failed to retrieve assistants due to an error: {e}")
        raise Exception("assistants_retrieve failed") from e


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

    # TODO: How to turn on file search? Untested
    tools: Iterable[AssistantToolParam]
    tools = [FileSearchToolParam(type='file_search')]
    config = AssistantUpdateParams(tool_resources=tool_resources, tools=tools)

    result = await assistant_update(assistant_id, config)
    assert result.tool_resources.file_search
    return result


assistant_handler: AssistantHandler = AssistantHandler(ASSISTANT_CONFIG_PATH, Assistant)


async def main() -> AssistantHandler:
    await assistant_handler.init()

    liminal_flow: Assistant = assistant_handler.find_by_name("Liminal Flow Agent")
    if not liminal_flow.tool_resources.file_search:
        liminal_flow = await attach_file_search(liminal_flow)

    # Hacky, doesn't save the config
    assistant_handler.objects["Liminal Flow Agent"] = liminal_flow

    return assistant_handler


if __name__ == '__main__':
    assistants = asyncio.run(main())


