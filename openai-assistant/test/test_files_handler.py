import unittest
from typing import List, Iterable

from openai.types import FileObject

from utils import files_handler


class TestFilesHandler(unittest.IsolatedAsyncioTestCase):
    test_file_id = 'file-G9zs0TF6ARnxj8mesqvd3sWW'

    async def test_files_list(self):
        files: List[FileObject] = await files_handler.files_list()

        TestFilesHandler.test_file_id = files[0].id

        self.assertTrue(isinstance(files, Iterable), "ojb should be an iterable")
        self.assertTrue(all(isinstance(item, FileObject) for item in files),
                        "all items in files should be of type FileObject")

    async def test_file_retrieve(self):
        result = await files_handler.files_retrieve(TestFilesHandler.test_file_id)
        self.assertTrue(isinstance(result, FileObject), "ojb should be an FileObject")