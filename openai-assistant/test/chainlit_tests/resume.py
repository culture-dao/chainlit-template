import logging

from chainlit.types import ThreadDict
from dotenv import load_dotenv
import chainlit as cl

from cl_events.on_chat_resume import on_chat_resume_logic
from test.chainlit_tests.resume_fixture import fixture, bad_fixture
from utils.openai_utils import initialize_openai_client

logging.basicConfig(level=logging.INFO)

load_dotenv(dotenv_path="../", override=True)

happy_path_thread = ThreadDict(fixture)
unhappy_path_thread = ThreadDict(bad_fixture)


@cl.on_chat_start
async def on_chat_start():
    client = initialize_openai_client("../../.env")
    await on_chat_resume_logic(happy_path_thread, client)
    await on_chat_resume_logic(unhappy_path_thread, client)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
