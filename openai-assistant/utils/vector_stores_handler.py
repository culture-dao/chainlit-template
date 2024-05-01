import asyncio
import logging
from typing import List

import yaml
from openai.pagination import AsyncCursorPage
from openai.types.beta import VectorStore

from utils.openai_utils import client, AsyncPaginatorHelper, load_yaml, list_to_dict

VECTOR_STORES_CONFIG_PATH = 'vector_stores.yaml'


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
logging.getLogger("httpx").setLevel("WARNING")


async def vector_stores_create() -> VectorStore:
    try:
        return await client.beta.vector_stores.create()
    except Exception as e:
        logging.error(f"Failed to create vector_stores due to an error: {e}")
        raise Exception("vector_stores_create failed") from e


async def vector_stores_list() -> List[VectorStore]:
    """Lists all the vector_stores for a specific assistant"""
    try:
        vector_stores: AsyncCursorPage[VectorStore] = await client.beta.vector_stores.list()
        return await AsyncPaginatorHelper.collect_all_items(vector_stores)

    except Exception as e:
        logging.error(f"Failed to list vector_stores due to an error: {e}")
        raise Exception("vector_stores_list failed") from e


async def vector_stores_retrieve(vector_store_id: str) -> VectorStore:
    try:
        return await client.beta.vector_stores.retrieve(vector_store_id)
    except Exception as e:
        logging.error(f"Failed to retrieve vector_stores due to an error: {e}")
        raise Exception("vector_stores_retrieve failed") from e


async def main():
    results = load_yaml(VECTOR_STORES_CONFIG_PATH, VectorStore)
    if not results:
        vector_stores = await vector_stores_list()
        results = list_to_dict(vector_stores)
        if not results:
            results = await vector_stores_create()
    with open(VECTOR_STORES_CONFIG_PATH, 'w') as f:
        yaml.dump(results, f)


if __name__ == "__main__":
    asyncio.run(main())
