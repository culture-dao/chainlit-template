import unittest

from cl_events.on_chat_resume import get_thread_id

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


class TestChatResume(unittest.TestCase):

    def test_get_thread_id_invalid(self):
        with self.assertRaises(Exception):
            get_thread_id(dict(steps=[step_without_id]))

    def test_step_valid(self):
        result = get_thread_id(dict(steps=[step_with_id]))
        self.assertEqual(result, "thread_CrU3GtC9roS2Gt1VevPEWMtk")
