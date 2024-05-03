from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Type

import yaml

from utils.openai_utils import load_yaml, list_to_dict

T = TypeVar('T')


class OpenAIHandler(ABC):
    def __init__(self, config_path: str, item_type: Type[T]):

        # Get the directory of the current script file
        current_dir = Path(__file__).resolve().parent
        # Join this directory with the relative path to the config file
        self.config_path = current_dir / config_path
        self.item_type = item_type
        self.objects: dict[str, item_type] = {}
        self.remotes: list[item_type] = []

    async def init(self):
        # Load config, load remotes
        self.objects = await self.load_config()
        self.remotes = await self.list()
        # If config is empty, load from remotes,
        if not self.objects:
            # Unless there are no remotes, then create the default config
            if not self.remotes:
                # This will return an obj, add it to remotes
                self.remotes.append(await self.create(config={}))
            self.objects = list_to_dict(self.remotes)
        # Make sure our remote objects get written back to file
        await self.sync_with_remote()
        return self

    def find_by_name(self, name: str):
        return self.objects[name]

    async def load_config(self) -> dict:
        return load_yaml(str(self.config_path), self.item_type)

    def update_config(self):
        with open(self.config_path, 'w') as f:
            yaml.dump(self.objects, f)

    async def sync_with_remote(self):

        for remote_object in self.remotes:
            local_object = self.objects.get(remote_object.name)

            if not local_object or local_object != remote_object:
                self.objects[remote_object.name] = remote_object
                self.update_config()

    @abstractmethod
    async def list(self):
        pass

    @abstractmethod
    async def create(self, config):
        pass

    @abstractmethod
    async def retrieve(self, item_id):
        pass

    @abstractmethod
    async def update(self, item_id):
        pass
