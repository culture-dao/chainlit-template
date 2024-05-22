import asyncio
import os

import yaml
from openai.pagination import AsyncCursorPage
from openai.resources import Files, AsyncFiles
from openai.types import FileObject

from utils.openai_utils import client


def load_or_create_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)
    else:
        with open(filename, 'w') as file:
            return {}


async def get_files():
    config_path = 'files.yaml'
    load_or_create_file(config_path)
    files: AsyncCursorPage[Files] = await AsyncFiles(client).list()

    obj_dict = {}
    file: FileObject
    for file in files.data:
        obj_dict[file.id] = file.to_dict()

    with open(config_path, 'w') as f:
        yaml.dump(obj_dict, f)


if __name__ == "__main__":
    asyncio.run(get_files())
    pass
