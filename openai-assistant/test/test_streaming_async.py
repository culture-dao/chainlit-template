"""
This is the testing framework for the new OAI async event handler.

We mock out the CL calls here, that final integration test is test/chainlit_tests/streaming.py
"""

import logging
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

import openai
from dotenv import load_dotenv
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads import MessageDelta, Message
from openai.types.beta.threads import Text, TextDelta, MessageDeltaEvent, TextDeltaBlock, TextContentBlock
from openai.types.beta.threads.runs import FileSearchToolCall

from utils.event_handler import EventHandler
from utils.openai_utils import get_playground_url, initialize_openai_client

load_dotenv(dotenv_path='../', override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestStreaming(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.assistant_id = 'asst_2lanl1dvlTkCpOofxiPrHvzr'
        self.client = initialize_openai_client()
        self.thread = None

    @patch('chainlit.Message', new_callable=MagicMock)
    async def testStreamingMocked(self, mock_message):
        mock_message.id = '1234'
        mock_message.return_value.send = AsyncMock()
        mock_message.return_value.update = AsyncMock()
        self.thread = await self.client.beta.threads.create()
        logger.info(get_playground_url(self.assistant_id, self.thread.id))
        async with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id,
                instructions="Please address the user as Jane Doe. The user has a premium account.",
                event_handler=EventHandler(),
        ) as stream:
            await stream.until_done()

    @patch('chainlit.Message', new_callable=MagicMock)
    async def testMessageDelta(self, mock_cl_message):
        mock_cl_message.return_value.send = AsyncMock()
        mock_cl_message.return_value.update = AsyncMock()
        e = EventHandler()
        m = Message.model_construct(text="The", id="123")
        await e.on_message_created(m)

        mock_cl_message.assert_called_with(content='')  # Constructor
        mock_cl_message.return_value.send.assert_called_once()

        # Make sure message is set on message creation
        self.assertIsNotNone(e.message)

        delta: MessageDelta = MessageDelta(
            content=[TextDeltaBlock(
                index=0,
                type="text",
                text=TextDelta(value="The")
            )],
            role="assistant"
        )

        text_block: TextContentBlock = TextContentBlock(type='text', text=Text(value="The", annotations=[]))

        message: Message = Message(
            id="123",
            assistant_id=self.assistant_id,
            content=[text_block],
            object="thread.message",
            role="assistant",
            created_at=1657898745,
            thread_id="456",
            status='in_progress'
        )

        e.current_event = ThreadMessageDelta(
            data=MessageDeltaEvent(id="123", delta=MessageDelta(value="The"), object="thread.message.delta"),
            event="thread.message.delta")

        await e.on_message_delta(delta, message)
        self.assertEqual(e.message.content, "The")

        mock_cl_message.return_value.update.assert_called_once()

    @patch('chainlit.Step', new_callable=MagicMock)
    async def test_process_file_search_tool_call(self, mock_cl_step):
        e = EventHandler()
        tool_call = FileSearchToolCall(
            id='1234',
            file_search={},
            type='file_search'
        )
        await e.on_tool_call_created(tool_call)
