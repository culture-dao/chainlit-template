import asyncio
import logging
from typing import List, Dict

from openai import AsyncOpenAI
from openai.pagination import AsyncCursorPage
from openai.types import FileObject
from openai.types.beta import VectorStore
from openai.types.beta.vector_stores import VectorStoreFile

from utils.files_handler import files_handler
from utils.openai_handler import OpenAIHandler
from utils.openai_utils import AsyncPaginatorHelper
from utils.vector_store_files_handler import vector_store_files_handler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
logging.getLogger("httpx").setLevel("WARNING")

VECTOR_STORES_CONFIG_PATH = 'vector_stores.yaml'


class VectorStoresHandler(OpenAIHandler):
    def __init__(self, config_path: str):
        super().__init__(config_path, VectorStore)
        self._vector_files = None
        self.files_handler = files_handler  # VSF Handler

    async def list(self):
        return await self._vector_stores_list()

    async def create(self, config):
        return await self._vector_stores_create(config)

    async def retrieve(self, vector_store_id):
        return await self._vector_stores_retrieve(vector_store_id)

    async def update(self, item_id, config=None):
        return await self._vector_stores_update(item_id, config)

    async def delete(self, vector_store_id) -> bool:
        result = await self.client.beta.vector_stores.delete(vector_store_id)
        return result.deleted

    async def delete_empty(self):
        logging.info('Starting Empty Vector Store Purge')
        empty_vector_store_ids = [vs.id for vs in self.remotes if vs.file_counts.total == 0]

        delete_tasks = [self.delete(vs_id) for vs_id in empty_vector_store_ids]
        logging.info(f"Empty Stores:\n{delete_tasks}")

        delete_results = await asyncio.gather(*delete_tasks)

        self.remotes = [vs for vs in self.remotes if
                    vs.id not in empty_vector_store_ids or not delete_results[empty_vector_store_ids.index(vs.id)]]

    async def retrieve_files(self, vector_store_id: str) -> [VectorStoreFile]:
        """
        Gets the vector store files for a particular vector store
        :param vector_store_id:
        :return: list of VectorStoreFile
        """
        try:
            vsf = self.client.beta.vector_stores.files.list(vector_store_id)
            return await AsyncPaginatorHelper.collect_all_items(vsf)
        except Exception as e:
            logging.error(f"Failed to list vector store files due to an error: {e}")
            raise Exception("vector_stores.files.list failed") from e

    async def resolve_files(self, vector_store_ids: List[str]) -> Dict[str, FileObject]:
        """
        Retrieves vector store files, gets the associated file and returns a map using the ID as key.
        :param vector_store_ids: list of vector stores
        :return: a map of file objects, using the ID as key
        """
        all_files = {}
        for vs_id in vector_store_ids:
            vector_store_files: [VectorStoreFile] = await self.retrieve_files(vs_id)
            for vsf in vector_store_files:
                file: FileObject = await self.files_handler.retrieve(vsf.id)
                all_files[file.id] = file
        return all_files

    @property
    async def vector_files(self):
        if not self._vector_files:  # If files are not loaded yet
            self._vector_files = []
            for vs in await self._vector_stores_list():
                if vs.file_counts.total == 0:  # there are no files
                    continue
                files: [VectorStoreFile] = await self.retrieve_files(vs.id)
                self._vector_files.extend(files)
        return self._vector_files

    async def _vector_stores_list(self) -> List[VectorStore]:
        """Lists all the vector_stores for a specific assistant"""
        try:
            vector_stores: AsyncCursorPage[VectorStore] = await self.client.beta.vector_stores.list()
            return await AsyncPaginatorHelper.collect_all_items(vector_stores)

        except Exception as e:
            logging.error(f"Failed to list vector_stores due to an error: {e}")
            raise Exception("vector_stores_list failed") from e

    async def _vector_stores_create(self, config=None) -> VectorStore:
        try:
            return await self.client.beta.vector_stores.create(**config)
        except Exception as e:
            logging.error(f"Failed to create vector_stores due to an error: {e}")
            raise Exception("vector_stores_create failed") from e

    async def _vector_stores_retrieve(self, vector_store_id: str) -> VectorStore:
        try:
            return await self.client.beta.vector_stores.retrieve(vector_store_id)
        except Exception as e:
            logging.error(f"Failed to retrieve vector_stores due to an error: {e}")
            raise Exception("vector_stores_retrieve failed") from e

    async def _vector_stores_update(self, vector_store_id: str, config):
        try:
            return await self.client.beta.vector_stores.update(vector_store_id, **config)
        except Exception as e:
            logging.error(f"Failed to update vector_stores due to an error: {e}")
            raise Exception("vector_stores_update failed") from e


vector_stores_handler: VectorStoresHandler = VectorStoresHandler(VECTOR_STORES_CONFIG_PATH)


async def main() -> VectorStoresHandler:
    await vector_stores_handler.init()
    await vector_stores_handler.delete_empty()
    default_store = vector_stores_handler.find_by_name("Default Datastore")
    if not default_store:
        await vector_stores_handler.create({'name': "Default Datastore"})
    return vector_stores_handler

if __name__ == "__main__":
    asyncio.run(main())
