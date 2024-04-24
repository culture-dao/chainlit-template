import json
import unittest

from openai_utils import get_file_map


class TestGetFileMap(unittest.TestCase):

    def setUp(self):
        self.test_file = '../app/assistants.json'
        with open(self.test_file, 'r') as f:
            self.test_data = json.load(f)

    def test_valid_file(self):
        result = get_file_map(self.test_file)
        self.assertEqual(result, self.test_data)

    def test_invalid_file(self):
        result = get_file_map('non_existent_file.json')
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
