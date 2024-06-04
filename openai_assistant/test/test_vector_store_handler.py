import os
import unittest
from typing import List, Iterable
from unittest.mock import Mock

from dotenv import load_dotenv
from openai.types.beta import VectorStore

load_dotenv('../.env', override=True)
from utils.vector_stores_handler import vector_stores_handler  # noqa: E402
TEST_VECTORSTORE_ID = os.getenv('TEST_VECTORSTORE_ID')


class TestVectorStoresHandler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.vector_id = TEST_VECTORSTORE_ID
        self.assistant_id = "fake_assistant_id"
        self.file_handler = Mock()
        self.handler = vector_stores_handler

    @unittest.skip("Don't make stores if we aren't going to clean them up")
    async def test_vector_stores_create(self):
        store: VectorStore = await self.handler._vector_stores_create()
        self.assertTrue(isinstance(store, VectorStore), "No VectorStore returned")

    async def test_vector_stores_list(self):
        vector_stores: List[VectorStore] = await self.handler._vector_stores_list()

        self.assertTrue(isinstance(vector_stores, Iterable), "obj should be an iterable")
        self.assertTrue(all(isinstance(item, VectorStore) for item in vector_stores),
                        "all items in files should be of type VectorStore")

    async def test_vector_store_retrieve(self):
        store: VectorStore = await self.handler._vector_stores_retrieve(self.vector_id)
        self.assertTrue(isinstance(store, VectorStore))

    @unittest.skip('Side Effects')
    async def test_vector_store_update(self):
        config = {
            "name": "Default Datastore"
        }
        result = await self.handler._vector_stores_update(self.vector_id, config)
        self.assertEqual(result.name, "Default Datastore")

    async def test_vector_store_files(self):
        result = self.handler.files
        pass


if __name__ == '__main__':
    unittest.main()
