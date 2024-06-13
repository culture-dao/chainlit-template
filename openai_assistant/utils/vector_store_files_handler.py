import logging
from typing import List

from openai.types.beta.vector_stores import VectorStoreFile, VectorStoreFileDeleted
from overrides import override

from utils.files_handler import files_handler
from utils.openai_handler import OpenAIHandler
from utils.openai_utils import AsyncPaginatorHelper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
logging.getLogger("httpx").setLevel("WARNING")

VECTOR_STORES_CONFIG_PATH = 'vector_store_files.yaml'


class VectorStoreFilesHandler(OpenAIHandler):
    def __init__(self, config_path: str):
        super().__init__(config_path, VectorStoreFile)
        self.file_handler = files_handler

    async def handle_empty_objects_and_remotes(self):
        # We don't need to create a new default here
        pass

    @override()
    async def list(self, vector_store_id=None, *args, **kwargs) -> List[VectorStoreFile]:
        if vector_store_id:
            vector_store_files = self.client.beta.vector_stores.files.list(
                vector_store_id
            )
            return await AsyncPaginatorHelper.collect_all_items(vector_store_files)
        else:
            return []

    @override()
    async def create(self, config, *args, **kwargs) -> VectorStoreFile:
        vector_store_id = config.get('vector_store_id')
        file_id = config.get('file_id')

        vector_store_file = self.client.beta.vector_stores.files.create(
            vector_store_id,
            file_id,
            *args,
            **kwargs
        )
        return vector_store_file

    @override()
    async def retrieve(self, vector_store_id, file_id, *args, **kwargs) -> VectorStoreFile:
        vector_store_file = self.client.beta.vector_stores.files.retrieve(
            vector_store_id,
            file_id,
            *args,
            **kwargs
        )
        return vector_store_file

    @override
    async def update(self, item_id, *args, **kwargs):
        pass

    async def delete(self, vector_store_id: str, file_id: str, *args, **kwargs) -> VectorStoreFileDeleted:
        deleted_vector_store_file = self.client.beta.vector_stores.files.delete(
            vector_store_id,
            file_id,
            *args,
            **kwargs
        )
        return deleted_vector_store_file

    async def resolve_files(self, file_id):
        return await self.client.files.retrieve(file_id)


vector_store_files_handler: VectorStoreFilesHandler = VectorStoreFilesHandler(VECTOR_STORES_CONFIG_PATH)
