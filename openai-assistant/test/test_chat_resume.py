import unittest

from openai.types.beta import Thread

from utils.openai_utils import initialize_openai_client

step_without_id = {
    "createdAt": "2024-03-28T16:22:22.629Z",
    "threadId": "85053762-ba5d-49e7-81bd-c72abb134c96",
    "parentId": "9adcabb4-081f-48c0-90e4-e6501cf2557b",
    "feedback": None,
    "start": "2024-03-28T12:22:21.000Z",
    "end": "2024-03-28T12:22:25.000Z",
    "type": "tool",
    "name": "retrieval",
    "generation": None,
    "input": "Retrieving information",
    "output": "Retrieved information",
    "showInput": None,
    "disableFeedback": True,
    "indent": None,
    "language": None,
    "isError": False,
    "waitForAnswer": None,
}

step_with_id = {
    "createdAt": "2024-05-16T15:41:50.529Z",
    "id": "63c36aad-2322-49bd-a713-e0eec77cc331",
    "threadId": "d5074bf8-729b-4fbd-a783-ee6d2ab310ef",
    "parentId": None,
    "feedback": None,
    "start": "2024-05-16T15:41:51.098Z",
    "end": "2024-05-16T15:42:15.089Z",
    "type": "run",
    "name": "AFGE V.S.",
    "generation": None,
    "input": '{\n    "args": [],\n    "kwargs": {\n        "thread_id": "thread_CrU3GtC9roS2Gt1VevPEWMtk",\n        '
             '"human_query": "what is the policy on annual leave?",\n        "file_ids": []\n    }\n}',
    "output": "",
    "showInput": False,
    "disableFeedback": True,
    "indent": None,
    "language": None,
    "isError": False,
    "waitForAnswer": None,
}


class TestChatResume(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = initialize_openai_client()

    async def test_try_step(self):
        from cl_events.on_chat_resume import try_step
        result = await try_step(step_without_id, self.client)
        self.assertEqual(None, result)

    @unittest.skip("step_with_id needs valid thread")
    async def test_step_valid(self):
        from cl_events.on_chat_resume import try_step
        result = await try_step(step_with_id, self.client)
        self.assertEqual(Thread, type(result))
