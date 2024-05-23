import asyncio
import logging
from typing import List

from openai import NotFoundError
from openai.pagination import AsyncPage
from openai.types import FileObject, FileDeleted

from utils.openai_handler import OpenAIHandler
from utils.openai_utils import AsyncPaginatorHelper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
logging.getLogger("httpx").setLevel("WARNING")

logger = logging.getLogger("chainlit")

CONFIG_PATH = 'files.yaml'


class FileHandler(OpenAIHandler):

    def __init__(self, config_path: str):
        super().__init__(config_path, FileObject)

    async def list(self):
        return await self._files_list()

    async def create(self, config):
        return await self._files_create(config)

    async def retrieve(self, assistant_id):
        return await self._files_retrieve(assistant_id)

    async def update(self, item_id):
        pass

    async def _files_list(self) -> List[FileObject]:
        """Lists all the files in our org"""
        try:
            files: AsyncPage[FileObject] = await self.client.files.list()
            return await AsyncPaginatorHelper.collect_all_items(files)

        except Exception as e:
            logging.error(f"Failed to list files due to an error: {e}")
            raise Exception("Failed to list files") from e

    async def _files_create(self, config):
        pass

    async def _files_delete(self,file_id):
        result: FileDeleted = await self.client.files.delete(file_id)
        assert result.deleted

    async def _files_retrieve(self,file_id: str) -> FileObject:
        try:
            return await self.client.files.retrieve(file_id)
        except NotFoundError as e:
            logging.error(f"{file_id} not found")
            raise e


file_handler: FileHandler = FileHandler(CONFIG_PATH)


async def main() -> FileHandler:
    await file_handler.init()
    return file_handler

if __name__ == '__main__':
    asyncio.run(main())
