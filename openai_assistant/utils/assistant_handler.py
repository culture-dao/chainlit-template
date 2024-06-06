import asyncio
import logging
from typing import List, Iterable


from openai.pagination import AsyncCursorPage
from openai.types.beta import Assistant, AssistantToolParam, FileSearchToolParam
from openai.types.beta.assistant_update_params import ToolResourcesFileSearch, AssistantUpdateParams, ToolResources

from utils.files_handler import files_handler
from utils.openai_handler import OpenAIHandler
from utils.openai_utils import AsyncPaginatorHelper
from utils.vector_stores_handler import vector_stores_handler

logger = logging.getLogger("chainlit")

ASSISTANT_CONFIG_PATH = 'assistant.yaml'


class AssistantHandler(OpenAIHandler):
    def __init__(self, config_path: str):
        super().__init__(config_path, Assistant)
        self.file_handler = files_handler
        self.vector_store_handler = vector_stores_handler

    async def list(self):
        return await self._assistants_list()

    async def create(self, config):
        return await self._assistants_create(config)

    async def retrieve(self, assistant_id):
        return await self._assistant_retrieve(assistant_id)

    async def update(self, item_id):
        pass

    async def load_files(self, assistant_id):
        assistant = await self.retrieve(assistant_id)
        vector_store_ids = assistant.tool_resources.file_search.vector_store_ids

        return await self.vector_store_handler.resolve_files(vector_store_ids)

    async def _assistants_list(self) -> List[Assistant]:
        try:
            assistants: AsyncCursorPage[Assistant] = await self.client.beta.assistants.list()
            return await AsyncPaginatorHelper.collect_all_items(assistants)
        except Exception as e:
            logging.error(f"Failed to list assistants due to an error: {e}")
            raise Exception("assistants_list failed") from e

    async def _assistants_create(self, config=None) -> Assistant:
        try:
            return await self.client.beta.assistants.create(**config)
        except Exception as e:
            logging.error(f"Failed to create vector_stores due to an error: {e}")
            raise Exception("vector_stores_create failed") from e

    async def _assistant_retrieve(self, assistant_id: str) -> Assistant:
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
            assistant = await self.client.beta.assistants.retrieve(assistant_id)
            logger.info(f"Retrieved existing assistant: {assistant.name}")
            return assistant
        except NotFoundError as e:
            logger.error({e})
            raise
        except Exception as e:
            logging.error(f"Failed to retrieve assistants due to an error: {e}")
            raise Exception("assistants_retrieve failed") from e

    async def _assistant_update(self, assistant_id, config) -> Assistant:
        try:
            return await self.client.beta.assistants.update(assistant_id, **config)
        except Exception as e:
            logging.error(f"Failed to update vector_stores due to an error: {e}")
            raise Exception("vector_stores_update failed") from e

    async def attach_file_search(self, assistant_id, vector_store_id=None) -> Assistant:
        if vector_store_id is None:
            # get "Default Datastore"
            raise Exception("assistant_handler.attach_file_search: Missing Datastore")
        tool = ToolResourcesFileSearch(vector_store_ids=[vector_store_id])
        tool_resources = ToolResources(file_search=tool)

        # TODO: How to turn on file search? Untested
        tools: Iterable[AssistantToolParam]
        tools = [FileSearchToolParam(type='file_search')]
        config = AssistantUpdateParams(tool_resources=tool_resources, tools=tools)

        result = await self._assistant_update(assistant_id, config)
        assert result.tool_resources.file_search
        return result


assistant_handler: AssistantHandler = AssistantHandler(ASSISTANT_CONFIG_PATH)


async def main() -> AssistantHandler:

    await assistant_handler.init()

    default_agent: Assistant = assistant_handler.find_by_name("Default Agent")
    if not default_agent.tool_resources.file_search:
        default_agent = await assistant_handler.attach_file_search(default_agent)

    # Hacky, doesn't save the config
    assistant_handler.objects["Default Agent"] = default_agent

    return assistant_handler


if __name__ == '__main__':
    asyncio.run(main())


