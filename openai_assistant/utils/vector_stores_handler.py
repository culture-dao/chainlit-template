import asyncio
import logging
from typing import List

from openai import AsyncOpenAI
from openai.pagination import AsyncCursorPage
from openai.types.beta import VectorStore

from utils.openai_handler import OpenAIHandler
from utils.openai_utils import AsyncPaginatorHelper

VECTOR_STORES_CONFIG_PATH = 'vector_stores.yaml'


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
logging.getLogger("httpx").setLevel("WARNING")


class VectorStoresHandler(OpenAIHandler):
    def __init__(self, config_path: str, client: AsyncOpenAI = None):
        super().__init__(config_path, VectorStore)
        self.client = client

    async def list(self):
        return await self.vector_stores_list()

    async def create(self, config):
        return await self.vector_stores_create()

    async def retrieve(self, vector_store_id):
        return await self.vector_stores_retrieve(vector_store_id)

    async def update(self, item_id, config=None):
        return await self.vector_stores_update(item_id, config)

    async def vector_stores_list(self) -> List[VectorStore]:
        """Lists all the vector_stores for a specific assistant"""
        try:
            vector_stores: AsyncCursorPage[VectorStore] = await self.client.beta.vector_stores.list()
            return await AsyncPaginatorHelper.collect_all_items(vector_stores)

        except Exception as e:
            logging.error(f"Failed to list vector_stores due to an error: {e}")
            raise Exception("vector_stores_list failed") from e

    async def vector_stores_create(self, config=None) -> VectorStore:
        try:
            return await self.client.beta.vector_stores.create(**config)
        except Exception as e:
            logging.error(f"Failed to create vector_stores due to an error: {e}")
            raise Exception("vector_stores_create failed") from e

    async def vector_stores_retrieve(self, vector_store_id: str) -> VectorStore:
        try:
            return await self.client.beta.vector_stores.retrieve(vector_store_id)
        except Exception as e:
            logging.error(f"Failed to retrieve vector_stores due to an error: {e}")
            raise Exception("vector_stores_retrieve failed") from e

    async def vector_stores_update(self, vector_store_id: str, config):
        try:
            return await self.client.beta.vector_stores.update(vector_store_id, **config)
        except Exception as e:
            logging.error(f"Failed to update vector_stores due to an error: {e}")
            raise Exception("vector_stores_update failed") from e


async def main():
    vector_stores = await VectorStoresHandler(VECTOR_STORES_CONFIG_PATH, VectorStore).init()
    default_store = vector_stores.find_by_name("Default Datastore")
    if not default_store:
        await vector_stores_create({'name': "Default Datastore"})


if __name__ == "__main__":
    asyncio.run(main())