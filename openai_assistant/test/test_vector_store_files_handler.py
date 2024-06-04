import os
import unittest


from dotenv import load_dotenv

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
        pass