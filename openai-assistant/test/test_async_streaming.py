import unittest

import openai
from dotenv import load_dotenv
from openai.lib.streaming import AsyncAssistantEventHandler

load_dotenv()


class EventHandler(AsyncAssistantEventHandler):
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


class TestStreaming(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.assistant_id = 'asst_GPa9ziLBlAg4gmZXCq6L5nF9'
        self.client = openai.AsyncOpenAI()
        self.thread = await self.client.beta.threads.create()

    async def testStreaming(self):
        async with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id,
                instructions="Please address the user as Jane Doe. The user has a premium account.",
                event_handler=EventHandler(),
        ) as stream:
            await stream.until_done()
