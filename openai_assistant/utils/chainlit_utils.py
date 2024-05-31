import logging
import os
from pathlib import Path
from typing import List

import chainlit as cl
from chainlit.element import Element
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta import Thread, FileSearchToolParam
from openai.types.beta.threads.message import Attachment
from openai.types.beta.vector_stores import VectorStoreFile

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)
assistant_id = os.environ.get("ASSISTANT_ID")

# List of allowed mime types
allowed_mime = [
    "text/csv",
    "application/pdf",
    "text/plain",
    "application/json",
    'application/octet-stream',  # TODO: "text/markdown" isn't caught by CL?
]
tool_map = [{"type": "retrieval"}]


# Check if the files uploaded are allowed
async def check_files(files: List[Element]):
    for file in files:
        if file.mime not in allowed_mime:
            return False
    return True


# Upload files to the assistant
async def upload_files(files: List[Element]):

    for file in files:
        # TODO: Use batch polling here
        await client.files.create(file=Path(file.path), purpose="assistants")  # Type: FileObject


async def process_files(files: List[Element]) -> List[Attachment]:
    attachments: List[Attachment] = []
    if len(files) > 0:
        attachments = []
        for file in files:
            logging.info(file)
            attachments.append(Attachment(file_id=file.id, tools=[FileSearchToolParam(type='file_search')]))
        files_ok = await check_files(files)

        if not files_ok:
            file_error_msg = (f"Hey, it seems you have uploaded one or more files that we do not support currently, "
                              f"please upload only : {(',').join(allowed_mime)}")
            await cl.Message(content=file_error_msg).send()  # Why does this return as author: Chatbot?
            return attachments

        await upload_files(files)

    return attachments


class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DictToObject(value))
            else:
                setattr(self, key, value)

    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in self.__dict__.items())


async def validate_upload():
    user_session_thread: Thread = cl.user_session.get("thread")
    # Thread in user session isn't updated with vector store information
    updated_thread: Thread = await client.beta.threads.retrieve(user_session_thread.id)
    logging.info(updated_thread)
    cl.user_session.set("thread", updated_thread)

    file_search = updated_thread.tool_resources.file_search
    if file_search is not None and len(file_search.vector_store_ids) > 0:
        files_list: List[VectorStoreFile] = []
        files: AsyncPaginator[
            VectorStoreFile, AsyncCursorPage[VectorStoreFile]] = await client.beta.vector_stores.files.list(
            file_search.vector_store_ids[0])

        async for file in files:
            logging.info(f"File content: {file}")
            files_list.append(file)

        latest_file: VectorStoreFile = max(files_list, key=lambda x: x.created_at)
        logging.info(f"Latest file: {latest_file}")

        if latest_file.last_error is not None:
            logging.info("The last file upload failed!")
            raise RuntimeError("There was an error with the file(s) you uploaded!")
    elif file_search is None:
        raise RuntimeError("There was an error with the file(s) you uploaded!")

