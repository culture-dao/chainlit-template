import asyncio
import logging
import unittest
from unittest.mock import patch, AsyncMock, Mock

import chainlit as cl
from openai import NotFoundError

from cl_events.on_chat_resume import on_chat_resume_logic

logging.basicConfig(level=logging.INFO)


@cl.on_chat_start
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)
def test_on_chat_resume_logic(mock_client):
    # HAPPY PATH

    # Mock the thread retrieval
    mock_client.beta.threads.retrieve.return_value = AsyncMock()
    mock_client.beta.threads.retrieve.return_value.id = "test_thread_id"

    # Define a sample thread
    cl_thread = {
        'steps': [
            {
                'type': 'run',
                'input': '{"kwargs": {"thread_id": "test_thread_id"}}'
            }
        ]
    }

    # noinspection PyTypeChecker
    result = asyncio.run(on_chat_resume_logic(cl_thread, mock_client))

    # Check that the function called the retrieve method with the correct thread ID
    mock_client.beta.threads.retrieve.assert_called_once_with("test_thread_id")

    # Check that the function returned the expected result
    unittest.TestCase().assertEqual(result.content, "Welcome back! I'm ready to assist you. How can I help you today?")

    # NO HAPPY PATH
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.request = Mock()
    mock_response.request.url = "URL('https://api.openai.com/v1/threads/thread_id')"
    args = str('Error code: 404 - {\'error\': {\'message\': "No thread found with id \'thread_id\'.", \'type\': '
               '\'invalid_request_error\', \'param\': None, \'code\': None}}', )
    error = NotFoundError(response=mock_response, body='Error message here', message=args)
    mock_client.beta.threads.retrieve.side_effect = error
    # noinspection PyTypeChecker
    asyncio.run(on_chat_resume_logic(cl_thread, mock_client))


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
