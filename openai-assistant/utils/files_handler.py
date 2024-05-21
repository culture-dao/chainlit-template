import logging
from typing import List

from openai import NotFoundError
from openai.pagination import AsyncPage
from openai.types import FileObject, FileDeleted

from utils.openai_utils import AsyncPaginatorHelper
from utils.openai_utils import client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
logging.getLogger("httpx").setLevel("WARNING")


async def files_list() -> List[FileObject]:
    """Lists all the files in our org"""
    try:
        files: AsyncPage[FileObject] = await client.files.list()
        return await AsyncPaginatorHelper.collect_all_items(files)

    except Exception as e:
        logging.error(f"Failed to list files due to an error: {e}")
        raise Exception("Failed to list files") from e


async def files_delete(file_id):
    result: FileDeleted = await client.files.delete(file_id)
    assert result.deleted


async def files_retrieve(file_id: str) -> FileObject:
    try:
        return await client.files.retrieve(file_id)
    except NotFoundError as e:
        logging.error(f"{file_id} not found")
        raise e
