import unittest

from openai.resources.beta.threads import Threads
from utils.openai_utils import initialize_openai_client

client = initialize_openai_client()


class TestThreads(unittest.IsolatedAsyncioTestCase):
    async def test_threads(self):
        thread_id = "thread_PPecfP37eSXH14froEsJJCSr"
        response = await client.beta.threads.retrieve(thread_id)
        print(response)
