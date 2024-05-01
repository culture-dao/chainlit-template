from abc import ABC, abstractmethod
from typing import TypeVar, Type

import yaml

from utils.openai_utils import load_yaml, list_to_dict

T = TypeVar('T')


class OpenAIHandler(ABC):
    def __init__(self, config_path: str, item_type: Type[T]):
        self.config_path = config_path
        self.item_type = item_type
        self.objects: dict[str, item_type] = {}
        self.map: dict[str, dict]

    async def init(self):
        self.objects = await self.load_config()
        if not self.objects:
            self.objects = await self.list()
            if not self.objects:
                self.objects = await self.create(config={})
            with open(self.config_path, 'w') as f:
                yaml.dump(list_to_dict(self.objects), f)
        return self

    def find_by_name(self, name: str):
        return self.objects[name]

    async def load_config(self) -> dict:
        return load_yaml(self.config_path, self.item_type)

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
