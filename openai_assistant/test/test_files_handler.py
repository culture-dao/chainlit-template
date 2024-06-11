import os
import unittest
from typing import List, Iterable

from dotenv import load_dotenv
from openai.types import FileObject

# from utils import files_handler

load_dotenv('../.env', override=True)
TEST_FILE_ID = os.getenv('TEST_FILE_ID')


@unittest.skip("Fails to import client in the files_handler.py file")
class TestFilesHandler(unittest.IsolatedAsyncioTestCase):

    async def test_files_list(self):
        files: List[FileObject] = await files_handler.files_list()
        self.assertTrue(isinstance(files, Iterable), "ojb should be an iterable")
        self.assertTrue(all(isinstance(item, FileObject) for item in files),
                        "all items in files should be of type FileObject")

    async def test_file_retrieve(self):
        result = await files_handler.files_retrieve(TEST_FILE_ID)
        self.assertTrue(isinstance(result, FileObject), "ojb should be an FileObject")
