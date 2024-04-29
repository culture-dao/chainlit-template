import asyncio
import os
import yaml

import openai
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.pagination import AsyncCursorPage
from openai.resources import Files, AsyncFiles
from openai.resources.beta.assistants import AsyncAssistants
from openai.types import FileObject
from openai.types.beta import Assistant

load_dotenv(override=True)

openai.api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI()


def load_or_create_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)
    else:
        with open(filename, 'w') as file:
            return {}


async def get_assistants():
    config_path = 'assistants.yaml'
    load_or_create_file(config_path)
    assistants: AsyncCursorPage[Assistant] = await AsyncAssistants(client).list()

    assistants_dict = {}
    assistant: Assistant
    for assistant in assistants.data:
        assistants_dict[assistant.id] = assistant.dict()

    with open(config_path, 'w') as f:
        yaml.dump(assistants_dict, f)


async def get_files():
    config_path = 'files.yaml'
    load_or_create_file(config_path)
    files: AsyncCursorPage[Files] = await AsyncFiles(client).list()

    obj_dict = {}
    file: FileObject
    for file in files.data:
        obj_dict[file.id] = file.dict()

    with open(config_path, 'w') as f:
        yaml.dump(obj_dict, f)


if __name__ == "__main__":
    asyncio.run(get_assistants())
    asyncio.run(get_files())
    pass
