import unittest
from unittest.mock import MagicMock

from openai_utils import initialize_openai_client
from utils.file_handler import (
    list_assistant_files,
    file_comparison,
    list_client_files,
    list_assistants,
    check_duplicate_files_usage
)


class TestFileHandler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.assistant_id = "fake_assistant_id"
        self.client = MagicMock()

    async def test_list_assistant_files(self):
        self.client.beta.assistants.files.list.return_value = MagicMock(data=[{"id": "file_1"}, {"id": "file_2"}])
        files = list_assistant_files(self.client, self.assistant_id)
        self.assertEqual(len(files), 2, "Should return two files")

    async def test_list_client_files(self):
        self.client.files.list.return_value = MagicMock(data=[{"filename": "file1.txt"}, {"filename": "file2.txt"}])
        files = list_client_files(self.client)
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


class TestBuggyAssistantFiles(unittest.TestCase):

    def test_buggy_files(self):
        test_assistant_id = "asst_UdBAhFZsmVSJCJ8THgCpA1tK"
        client = initialize_openai_client()
        assistants = list_assistants(client)
        my_assistant = [assistant for assistant in assistants if assistant.id == test_assistant_id][0]
        self.assertEqual(my_assistant.file_ids, [], "")

        retrieved_assistant = client.beta.assistants.retrieve(test_assistant_id)
        self.assertGreater(retrieved_assistant.file_ids, [])


if __name__ == '__main__':
    unittest.main()
