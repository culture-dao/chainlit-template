import unittest

import chainlit as cl
import openai
from dotenv import load_dotenv

from utils.create_assistant import retrieve_assistant
from chainlit_utils import DictToObject

load_dotenv()


class TestAssistant(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.client = openai.AsyncClient()

    async def test_retrieve_assistant_valid(self):
        result = await retrieve_assistant("asst_GPa9ziLBlAg4gmZXCq6L5nF9")
        assert result

    async def test_retrieve_assistant_invalid(self):
        with self.assertRaises(Exception):
            await retrieve_assistant("nonsense")


class TestRuns(unittest.IsolatedAsyncioTestCase):
    thread = 'thread_39etazHnZG215hwrT3c4gF5p'

    async def asyncSetUp(self) -> None:
        self.client = openai.AsyncClient()

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

            if run.status is "completed" and thread_message.content is None:
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
