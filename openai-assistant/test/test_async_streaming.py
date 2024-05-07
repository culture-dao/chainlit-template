import unittest
import logging
from typing import Dict

import openai
from dotenv import load_dotenv
from openai.lib.streaming import AsyncAssistantEventHandler
from openai.types.beta.threads import Run, Text, TextDelta, Message
from openai.types.beta.threads.runs import RunStep
from openai.types.beta.threads import MessageDelta, Message
from typing_extensions import override
from unittest.mock import MagicMock, patch, AsyncMock

import chainlit as cl

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventHandler(AsyncAssistantEventHandler):

    def __init__(self):
        super().__init__()
        self.event_map = {}  # for debugging
        self.run: Run | None = None
        self.run_step: RunStep | None = None
        self.message_content: str | None = None
        self.message_references: Dict[str, cl.Message] = {}
        self.message: cl.Message | None = None

    @override
    async def on_text_created(self, text: Text) -> str:
        self.message_content = text.value
        print("\nassistant > ", end="", flush=True)
        return self.message_content

    @override
    async def on_message_created(self, message: Message) -> None:
        self.message = cl.Message(content='')
        await self.message.send()

    @override
    async def on_text_delta(self, delta: TextDelta, snapshot: Text):
        print(delta.value, end="", flush=True)
        self.message.content = delta.value
        await self.message.update()

    @override
    async def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    async def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    @override
    async def on_run_step_done(self, run):
        logging.info(self.event_map)
        logging.info(self.message)

    @override
    async def on_event(self, event):
        event_type = type(event).__name__
        if event_type in self.event_map:
            self.event_map[event_type] += 1
        else:
            self.event_map[event_type] = 1


class TestStreaming(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.assistant_id = 'asst_GPa9ziLBlAg4gmZXCq6L5nF9'
        self.client = openai.AsyncOpenAI()
        self.thread = None

    @patch('chainlit.Message', new_callable=MagicMock)
    async def testStreaming(self, mock_message):
        mock_message.return_value.send = AsyncMock()
        mock_message.return_value.update = AsyncMock()

        self.thread = await self.client.beta.threads.create()
        async with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id,
                instructions="Please address the user as Jane Doe. The user has a premium account.",
                event_handler=EventHandler(),
        ) as stream:
            await stream.until_done()


class TestEventHandler(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.assistant_id = 'asst_GPa9ziLBlAg4gmZXCq6L5nF9'
        self.client = openai.AsyncOpenAI()

    @patch('chainlit.Message', new_callable=MagicMock)
    async def testMessgeDelta(self, mock_message):
        mock_message.return_value.send = AsyncMock()
        mock_message.return_value.update = AsyncMock()

        e = EventHandler()
        m = Message.model_construct(text="The")
        await e.on_message_created(m)

        mock_message.assert_called_with(content='')  # Constructor
        mock_message.return_value.send.assert_called_once()

        delta = TextDelta(value="The")
        text: Text = Text(value='The', annotations=[])

        await e.on_text_delta(delta, text)
        self.assertEqual(e.message.content, "The")
        mock_message.return_value.update.assert_called_once()
