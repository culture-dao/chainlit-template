import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import chainlit as cl
from chainlit.element import Element
from openai import AsyncOpenAI
from openai.types.beta.threads.runs import RunStep
from openai.types.beta.threads.runs.tool_calls_step_details import ToolCall
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
async def upload_files(files: List[Element]) -> List[VectorStoreFile]:
    default_data_store = 'vs_ZpE5J5qh5KMRMrwXkzsAxobM'
    file_ids = []
    for file in files:
        # TODO: Use batch polling here
        uploaded_file: VectorStoreFile = await (client.beta.vector_stores.files.upload_and_poll(
            vector_store_id=default_data_store,
            file=Path(file.path))
                                                )
        file_ids.append(uploaded_file)
    return file_ids


async def process_files(files: List[Element]) -> List[VectorStoreFile]:
    # Upload files if any and get file_ids
    file_ids = []
    if len(files) > 0:
        files_ok = await check_files(files)

        if not files_ok:
            file_error_msg = f"Hey, it seems you have uploaded one or more files that we do not support currently, please upload only : {(',').join(allowed_mime)}"
            await cl.Message(content=file_error_msg).send()  # Why does this return as author: Chatbot?
            return file_ids

        file_ids: List[VectorStoreFile] = await upload_files(files)

    return file_ids


class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DictToObject(value))
            else:
                setattr(self, key, value)

    def __str__(self):
        return "\n".join(f"{key}: {value}" for key, value in self.__dict__.items())