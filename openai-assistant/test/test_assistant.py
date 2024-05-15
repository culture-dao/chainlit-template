import unittest

from create_assistant import retrieve_assistant


class TestAssistantAsync(unittest.IsolatedAsyncioTestCase):

    async def test_retrieve_assistant_valid(self):
        result = await retrieve_assistant("asst_2lanl1dvlTkCpOofxiPrHvzr")
        assert result

    async def test_retrieve_assistant_invalid(self):
        with self.assertRaises(Exception):
            await retrieve_assistant("nonsense")

