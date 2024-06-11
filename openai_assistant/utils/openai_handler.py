from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar, Type

import yaml
from openai.types.beta import VectorStore

from utils.openai_utils import load_yaml, list_to_dict, client

T = TypeVar('T')


class OpenAIHandler(ABC):
    def __init__(self, config_path: str, item_type: Type[T]):
        self.client = client

        # Get the directory of the current script file
        current_dir = Path(__file__).resolve().parent
        # Join this directory with the relative path to the config file
        self.config_path = current_dir / config_path
        self.item_type = item_type
        self.objects: dict[str, item_type] = {}
        self.remotes: list[item_type] = []

    async def init(self):
        # Load config, load remotes
        self.remotes = await self.list()
        self.objects = await self.load_config()
        await self.handle_empty_objects_and_remotes()
        # Make sure our remote objects get written back to file
        await self.sync_with_remote()
        return self

    async def load_config(self) -> dict:
        return load_yaml(str(self.config_path), self.item_type)

    async def handle_empty_objects_and_remotes(self):
        """What to do when the API returns empty?
        We're assuming a new API key, so we load our default setup
        If config is empty, load from remotes,
        This can be overriden where needed.
        """
        if not self.objects:
            # Unless there are no remotes, then create the default config
            if not self.remotes:
                # This will return an obj, add it to remotes
                self.remotes.append(await self.create(config={}))
            self.objects = list_to_dict(self.remotes)

    async def sync_with_remote(self):
        for remote_object in self.remotes:
            local_object: VectorStore = self.objects.get(remote_object.id)

            if not local_object or local_object != remote_object:
                self.objects[remote_object.id] = remote_object

            self.update_config()

    def update_config(self):
        with open(self.config_path, 'w') as f:
            _as_dicts = {remote.id: remote.model_dump() for remote in self.remotes}
            yaml.dump(_as_dicts, f)

    def find_by_name(self, name: str):
        return [obj for obj in self.objects if getattr(obj, 'name', None) == name]

    def find_by_id(self, obj_id: str):
        return self.objects[obj_id]

    @abstractmethod
    async def list(self, *args, **kwargs):
        pass

    @abstractmethod
    async def create(self, *args, **kwargs):
        pass

    @abstractmethod
    async def retrieve(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass
