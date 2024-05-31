import os
import unittest
from typing import List, Iterable

from dotenv import load_dotenv
from openai._types import FileTypes
from openai.types import FileObject

load_dotenv('../.env', override=True)

from utils.files_handler import files_handler

TEST_FILE_ID = os.getenv('TEST_FILE_ID')


class TestFilesHandler(unittest.IsolatedAsyncioTestCase):

    async def test_files_list(self):
        files: List[FileObject] = await files_handler._files_list()
        self.assertTrue(isinstance(files, Iterable), "ojb should be an iterable")
        self.assertTrue(all(isinstance(item, FileObject) for item in files),
                        "all items in files should be of type FileObject")

    async def test_file_retrieve(self):
        result = await files_handler._files_retrieve(TEST_FILE_ID)
        self.assertTrue(isinstance(result, FileObject), "ojb should be an FileObject")

    async def test_file_create(self):

        file_name = 'test/dummy_file.txt'
        file_content = bytes(100)
        file: FileTypes = (file_name, file_content)
        result = await files_handler.create(file)
        self.assertTrue(result.filename, file_name)
