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

    # OLD SHIT



    async def test_vectors_stores_files(self):
        files = await vector_stores_handler.vector_stores_files()
        self.assertEqual(len(files), 2, "Should return two files")

    async def test_no_missing_or_extra_files(self):
        oai_files = [{"name": "file1"}, {"name": "file2"}]
        local_files = [{"name": "file1"}, {"name": "file2"}]

        # Redirect logging output to a StringIO object for testing
        with self.assertLogs() as logs:
            file_comparison(oai_files, local_files)

        self.assertEqual(logs.output, ["INFO:root:No extra files!", "INFO:root:No missing files!"])

    async def test_missing_files(self):
        oai_files = [{"name": "file1"}, {"name": "file2"}]
        local_files = [{"name": "file1"}]

        with self.assertLogs(level='INFO') as logs:
            file_comparison(oai_files, local_files)
        self.assertIn("INFO:root:Missing file locally: file2", logs.output)
        self.assertIn("INFO:root:No extra files!", logs.output)

    async def test_extra_files(self):
        oai_files = [{"name": "file1"}]
        local_files = [{"name": "file1"}, {"name": "file2"}]

        with self.assertLogs(level='INFO') as logs:
            file_comparison(oai_files, local_files)

        self.assertIn("INFO:root:Extra file locally: file2", logs.output)
        self.assertIn("INFO:root:No missing files!", logs.output)

    def test_check_duplicate_files_usage(self):
        duplicates = {
            "file1.txt": ["id1", "id2"],
            "file2.txt": ["id3"]
        }
        assistant_file_map = [
            {"id": "assistant1", "files": ["id2"]},
            {"id": "assistant2", "files": ["id3"]}
        ]

        expected_unused_files = ["id1"]

        unused_files = check_duplicate_files_usage(duplicates, assistant_file_map)

        self.assertEqual(unused_files, expected_unused_files, "The function should identify unused file IDs correctly.")


if __name__ == '__main__':
    unittest.main()
