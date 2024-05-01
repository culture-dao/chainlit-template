from abc import ABC, abstractmethod
from typing import TypeVar, Type

import yaml

from utils.openai_utils import load_yaml, list_to_dict

T = TypeVar('T')


class OpenAIHandler(ABC):
    def __init__(self, config_path: str, item_type: Type[T]):
        self.config_path = config_path
        self.item_type = item_type

    async def load_config(self) -> dict:
        return load_yaml(self.config_path, self.item_type)

    @abstractmethod
    async def list_items(self):
        pass

    @abstractmethod
    async def create_item(self):
        pass

    async def sync_with_yaml(self):
        results = await self.load_config()
        if not results:
            items = await self.list_items()
            results = list_to_dict(items)
            if not results:
                results = await self.create_item()
        with open(self.config_path, 'w') as f:
            yaml.dump(results, f)
