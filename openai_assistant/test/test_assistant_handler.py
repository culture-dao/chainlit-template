import os
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Iterable, List

import chainlit as cl
from dotenv import load_dotenv
from openai.types import FileObject
from openai.types.beta import Assistant

from utils.chainlit_utils import DictToObject

load_dotenv('../.env', override=True)
from utils.assistant_handler import assistant_handler  # noqa: E402
TEST_ASSISTANT_ID = os.getenv('TEST_ASSISTANT_ID')
ASSISTANT_NAME = os.getenv('ASSISTANT_NAME')


class TestAssistantHandler(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.handler = assistant_handler

    async def test_load_files_integration(self):
        files = await self.handler.load_files(TEST_ASSISTANT_ID)
        assert all(isinstance(file, FileObject) for file in files.values())

    async def test_assistant_retrieve_valid(self):
        result = await self.handler._assistant_retrieve(TEST_ASSISTANT_ID)
        assert result

    async def test_assistant_retrieve_invalid(self):
        with self.assertRaises(Exception):
            await self.handler._assistant_retrieve("nonsense")

    async def test_assistant_list(self):
        assistants: List[Assistant] = await self.handler._assistants_list()
        self.assertTrue(isinstance(assistants, Iterable), "obj should be an iterable")
        self.assertTrue(all(isinstance(item, Assistant) for item in assistants),
                        "all items in files should be of type Assistant")

    @unittest.skip("Side effects")
    async def test_assistant_update(self):
        await self.handler.attach_file_search(TEST_ASSISTANT_ID)


@unittest.skip("Needs valid thread and big refactor")
class TestRuns(unittest.IsolatedAsyncioTestCase):
    thread = 'thread_39etazHnZG215hwrT3c4gF5p'

    async def asyncSetUp(self) -> None:
        self.client = client

    async def asyncTearDown(self) -> None:
        await self.client.close()

    async def test_run_retrieve(self):
        thread = await self.client.beta.threads.create()
        thread_id = thread.id
        client = self.client
        query = "What is the policy on leave?"

        # This needs optimization

        await self.client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=query
        )

        run = await self.client.beta.threads.runs.create(
            thread_id=thread.id, assistant_id='asst_GPa9ziLBlAg4gmZXCq6L5nF9'
        )
        while True:
            thread_message = None

            run = await client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )

            # Fetch the run steps
            run_steps = await client.beta.threads.runs.steps.list(
                thread_id=thread_id, run_id=run.id, order="asc"
            )

            for step in run_steps.data:
                # Fetch step details
                run_step = await client.beta.threads.runs.steps.retrieve(
                    thread_id=thread_id, run_id=run.id, step_id=step.id
                )
                step_details = run_step.step_details
                print(step_details)
                # Update step content in the Chainlit UI
                if step_details.type == "message_creation":
                    thread_message = await client.beta.threads.messages.retrieve(
                        message_id=step_details.message_creation.message_id,
                        thread_id=thread_id,
                    )
                    print(thread_message)

                if step_details.type == "tool_calls":
                    for tool_call in step_details.tool_calls:
                        if isinstance(tool_call, dict):
                            tool_call = DictToObject(tool_call)

                        if tool_call.type == "retrieval":
                            print("Retrieving information")

                if (
                        run.status == "requires_action"
                        and run.required_action.type == "submit_tool_outputs"
                ):
                    await self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=[],
                    )

            await cl.sleep(5)

            if run.status == "completed" and thread_message.content is None:
                thread_message.content = "An error occurred, please try again later or contact support"
                print(thread_message)

            if run.status in ["cancelled", "failed", "completed", "expired"]:
                break

    async def test_retrieve_messages(self):
        messages = await self.client.beta.threads.messages.list(TestRuns.thread)
        self.assertTrue(messages)

    async def test_retrieve_run(self):
        run_id = 'run_tz5Q6XIQyN6ZSkb5PIwEw6Tg'
        thread_id = TestRuns.thread
        run = await self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

        # Fetch the run steps
        run_steps = await self.client.beta.threads.runs.steps.list(
            thread_id=thread_id, run_id=run.id, order="asc"
        )
        self.assertTrue(run_steps)
