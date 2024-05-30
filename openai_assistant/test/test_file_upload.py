import logging
import unittest
from typing import List

from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta import Thread
from openai.types.beta.vector_stores import VectorStoreFile

from utils.openai_utils import initialize_openai_client


class TestFileUpload(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client: AsyncOpenAI = initialize_openai_client()
        self.thread: Thread = await self.client.beta.threads.retrieve('thread_RsOW6lvsgp7hxjvb4IzIU1VL')

    async def test_file_upload(self):
        self.assertTrue(len(self.thread.tool_resources.file_search.vector_store_ids) > 0, "No vector store IDs found")
        files_list: List[VectorStoreFile] = []
        files: AsyncPaginator[
            VectorStoreFile, AsyncCursorPage[VectorStoreFile]] = await self.client.beta.vector_stores.files.list(
            self.thread.tool_resources.file_search.vector_store_ids[0])

        # Process each page in the paginator
        async for file in files:
            logging.info(f"File content: {file}")
            logging.info(f"File type: {type(file)}")
            self.assertIsInstance(file, VectorStoreFile, "File is not of type VectorStoreFile")
            files_list.append(file)

        self.assertGreater(len(files_list), 0, "No files were listed")
        latest_file: VectorStoreFile = max(files_list, key=lambda x: x.created_at)
        logging.info(f"Latest file: {latest_file}")

        self.assertIsNotNone(latest_file, "No latest file found")
        self.assertIsInstance(latest_file, VectorStoreFile, "Latest file is not of type VectorStoreFile")

        self.assertTrue(latest_file.last_error is not None)
        if latest_file.last_error is not None:
            logging.info("There was an error with the file(s) you uploaded!")


if __name__ == "__main__":
    unittest.main()
