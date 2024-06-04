import os
import unittest
from typing import List

from dotenv import load_dotenv
from openai.types.beta.vector_stores import VectorStoreFile

load_dotenv('../.env', override=True)
from utils.vector_store_files_handler import vector_store_files_handler  # noqa: E402
TEST_VECTORSTORE_ID = os.getenv('TEST_VECTORSTORE_ID')
TEST_FILE_ID = os.getenv('TEST_FILE_ID')


class TestVectorStoresFileHandler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.vector_id = TEST_VECTORSTORE_ID
        self.file_id = TEST_FILE_ID
        self.handler = vector_store_files_handler

    async def test_list(self):
        files = await self.handler.list(TEST_VECTORSTORE_ID)
        self.assertIsInstance(files[0], VectorStoreFile)

    async def test_init(self):
        await self.handler.init()

