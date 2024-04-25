import unittest

from utils.openai_utils import initialize_openai_client


class TestThreads(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.thread_id = "thread_PPecfP37eSXH14froEsJJCSr"
        self.client = initialize_openai_client()

    async def test_threads(self):

        response = await self.client.beta.threads.retrieve(self.thread_id)
        print(response)

    async def test_messages(self):
        response = await self.client.beta.threads.messages.list(self.thread_id)
        print(response)