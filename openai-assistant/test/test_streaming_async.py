"""
This is the testing framework for the new OAI async event handler.

We mock out the CL calls here, that final integration test is test/chainlit_tests/streaming.py
"""

import logging
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from chainlit.context import ChainlitContext, context_var
from chainlit.session import HTTPSession
from dotenv import load_dotenv
from openai.types.beta.assistant_stream_event import ThreadMessageDelta
from openai.types.beta.threads import MessageDelta, Message
from openai.types.beta.threads import Text, TextDelta, MessageDeltaEvent, TextDeltaBlock, TextContentBlock
from openai.types.beta.threads.runs import FileSearchToolCall

from utils.event_handler import EventHandler
from utils.openai_utils import get_playground_url, initialize_openai_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv('../.env')
TEST_ASSISTANT_ID = os.getenv('TEST_ASSISTANT_ID')


class TestStreaming(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.assistant_id = TEST_ASSISTANT_ID
        self.client = initialize_openai_client()
        self.thread = None

    async def asyncTearDown(self):
        await self.client.close()

    @unittest.skip("cl.context not found. see openai-assistant/test/chainlit_tests/streaming.py")
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
                event_handler=EventHandler(self.client),
        ) as stream:
            await stream.until_done()

    @patch('chainlit.Message', new_callable=MagicMock)
    async def testMessageDelta(self, mock_cl_message):
        mock_cl_message.return_value.send = AsyncMock()
        mock_cl_message.return_value.update = AsyncMock()
        e = EventHandler(AsyncMock())
        m = Message.model_construct(text="The", id="123")
        await e.on_message_created(m)

        mock_cl_message.assert_called_with(content='')  # Constructor
        mock_cl_message.return_value.send.assert_called_once()

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

        e._current_event = ThreadMessageDelta(
            data=MessageDeltaEvent(id="123", delta=MessageDelta(value="The"), object="thread.message.delta"),
            event="thread.message.delta")

        await e.on_message_delta(delta, message)
        self.assertEqual(e.message_references['123'].content, "The")

        mock_cl_message.return_value.update.assert_called_once()

    @unittest.skip("cl.context not found. see openai-assistant/test/chainlit_tests/streaming.py")
    @patch('chainlit.step.Step')
    async def test_process_file_search_tool_call(self, mock_step):
        # Create a mock HTTPSession
        mock_session = MagicMock(spec=HTTPSession)
        mock_session.thread_id = "test_thread_id"

        # Create a ChainlitContext with the mock session
        mock_context = ChainlitContext(session=mock_session)

        # Set the context_var to the mock context
        context_var.set(mock_context)

        # Create a mock instance of Step and configure it
        mock_step_instance = AsyncMock()
        mock_step_instance.__aenter__.return_value = mock_step_instance
        mock_step_instance.__aexit__.return_value = None
        mock_step.return_value = mock_step_instance

        # Create a mock client if required by EventHandler
        mock_client = MagicMock()
        e = EventHandler(mock_client)
        tool_call = FileSearchToolCall(
            id='1234',
            file_search={},
            type='file_search'
        )

        await e.on_tool_call_created(tool_call)

