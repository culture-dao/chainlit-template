import unittest
from typing import List, Iterable
from unittest.mock import MagicMock

from openai.types.beta import VectorStore

from utils import vector_stores_handler


class TestVectorStoresHandler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.vector_id = 'vs_ZpE5J5qh5KMRMrwXkzsAxobM'
        self.assistant_id = "fake_assistant_id"
        self.client = MagicMock()

    @unittest.skip("Don't make stores if we aren't going to clean them up")
    async def test_vector_stores_create(self):
        store: VectorStore = await vector_stores_handler.vector_stores_create()
        self.assertTrue(isinstance(store, VectorStore), "No VectorStore returned")

    async def test_vector_stores_list(self):
        vector_stores: List[VectorStore] = await vector_stores_handler.vector_stores_list()

        self.assertTrue(isinstance(vector_stores, Iterable), "obj should be an iterable")
        self.assertTrue(all(isinstance(item, VectorStore) for item in vector_stores),
                        "all items in files should be of type VectorStore")

    async def test_vector_store_retrieve(self):
        store: VectorStore = await vector_stores_handler.vector_stores_retrieve(self.vector_id)
        self.assertTrue(isinstance(store, VectorStore))

    async def test_vector_store_update(self):
        id = 'vs_ZpE5J5qh5KMRMrwXkzsAxobM'
        config = {
            "name": "Default Datastore"
        }
        result = await vector_stores_handler.vector_stores_update(id, config)
        self.assertEqual(result.name, "Default Datastore")


if __name__ == '__main__':
    unittest.main()
