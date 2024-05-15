import unittest

import chainlit as cl
import openai

from create_assistant import retrieve_assistant
from chainlit_utils import DictToObject
from utils.openai_utils import initialize_openai_client


class TestAssistantAsync(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.client = initialize_openai_client('../.env')

    async def test_retrieve_assistant_valid(self):
        result = await retrieve_assistant("asst_2lanl1dvlTkCpOofxiPrHvzr")
        assert result

    async def test_retrieve_assistant_invalid(self):
        with self.assertRaises(Exception):
            await retrieve_assistant("nonsense")

