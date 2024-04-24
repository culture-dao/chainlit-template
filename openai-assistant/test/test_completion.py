import asyncio
import logging
import unittest

from agency_swarm.user import User
from dotenv import load_dotenv

from chainlit_utils import *
from swarm.agent_loader import AgentLoader
from swarm.async_threads import CustomThreadAsync

load_dotenv()
logging.basicConfig(level=logging.INFO)


class TestCompletion(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key)

        # Agency-swarm initialization actions
        assistant_id = 'asst_UdBAhFZsmVSJCJ8THgCpA1tK'
        self.agent = AgentLoader(id=assistant_id)
        self.agent.init_oai()
        self.user = User()

    async def asyncTearDown(self):
        await self.client.close()

    async def get_thread_result(self, thread_id: str, human_query: str, file_ids: List[str] = []):
        coro = self.thread.get_completion(message=human_query, message_files=file_ids, yield_messages=False)
        result = await asyncio.gather(coro)
        return result[0]

    async def test_get_thread_result(self):
        self.thread = CustomThreadAsync(self.user, self.agent)
        self.thread.init_thread()
        result = await self.get_thread_result(thread_id=self.thread.id, human_query="What is 2+2?", file_ids=[])

        self.assertTrue('4' in result)


if __name__ == '__main__':
    unittest.main()
