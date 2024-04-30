import asyncio
import json
import logging
import os
import sys

from openai.pagination import AsyncPage
from openai.types import FileObject
from openai.types.beta import VectorStore

from utils import files_handler
from utils.assistant_handler import assistants_list
from utils.files_handler import files_list
from utils.openai_utils import client

import asyncio
from typing import List, TypeVar, Generic, Any

T = TypeVar('T')


class AsyncPaginatorHelper(Generic[T]):
    """
    AsyncPage objects are limited to 100 results, 20 default, so we'll need pagination handling on the 'list' functions.
    """
    @staticmethod
    async def collect_all_items(paginator: AsyncPage[FileObject]) -> List[T]:
        items = []
        async for item in paginator:
            logging.info(item)
            items.append(item)
        return items


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
logging.getLogger("httpx").setLevel("WARNING")


async def vector_stores_list() -> List[VectorStore]:
    """Lists all the vector_stores for a specific assistant"""
    try:
        vector_stores: AsyncPage[FileObject] = await client.beta.vector_stores.list()
        return await AsyncPaginatorHelper.collect_all_items(vector_stores)

    except Exception as e:
        logging.error(f"Failed to list vector_stores due to an error: {e}")
        raise Exception("vector_stores_list failed") from e


async def vector_stores_create() -> VectorStore:
    try:
        return await client.beta.vector_stores.create()
    except Exception as e:
        logging.error(f"Failed to create vector_stores due to an error: {e}")
        raise Exception("vector_stores_create failed") from e


def list_client_files(client):
    """Lists all the files from the OpenAI client"""
    try:
        files = client.files.list()
        return files.data
    except Exception as e:
        logging.error(f"Failed to list client files due to an error: {e}")
        raise Exception("Failed to client list files") from e


def format_file_information(client, files):
    """Retrieves the metadata of a file from OpenAI and stores it in a dictionary"""
    file_dict = []
    for file in files:
        file = retrieve_file(client, file.id)
        file_dict.append({"id": file.id, "created_at": file.created_at, "name": file.filename})
    return file_dict


def read_json_file(file_path):
    """Loads a JSON file and returns the contents"""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON from {file_path}: {e}")
        raise Exception(f"Failed to decode JSON from {file_path}") from e


def append_to_json_file(file_path, new_data):
    """Adds information to the end of a JSON file if the item is not already present"""
    existing_data = read_json_file(file_path)

    for new_item in new_data:

        existing_index = next((i for i, item in enumerate(existing_data) if item['id'] == new_item['id']), None)

        if existing_index is not None and existing_data[existing_index] != new_item:
            existing_data[existing_index] = new_item
        elif existing_index is None:
            existing_data.append(new_item)

    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)


def retrieve_file(file_id):
    """Retrieves a specific file from OpenAI"""
    try:
        file = client.files.retrieve(file_id)
        return file
    except Exception as e:
        logging.error(f"Failed to retrieve file {file_id} due to an error: {e}")
        raise Exception(f"Failed to retrieve file {file_id}") from e


def write_and_list_file_information(assistant_id):
    """Lists the files for an assistant and writes them to a JSON"""
    try:
        files = files_list()
        if files:
            formatted_information = format_file_information(client, files)
            append_to_json_file("file_data.json", formatted_information)
            return formatted_information
    except ValueError as e:
        logging.error(e)


def get_local_files(base_path="app/public"):
    """Gets all the files from a local directory excluding png and svg files"""
    local_files = []

    for root, dirs, files in os.walk(base_path):
        for file in files:

            if file.endswith(('.pdf', '.md')):
                full_path = os.path.join(root, file)

                local_files.append({"name": file, "path": full_path})

    return local_files


def file_comparison(oai_files, local_files):
    """Compares OpenAI files to local files to check for missing/extra files"""

    # Convert data to sets
    local_file_names = set(file["name"] for file in local_files)
    oai_file_names = set(file["name"] for file in oai_files)

    # Subtract Local Files from OAI files, so we can see if we have any extra files locally.
    extra_files = local_file_names - oai_file_names
    if not extra_files:
        logging.info("No extra files!")
    else:
        for file_name in extra_files:
            logging.info(f"Extra file locally: {file_name}")

    # Subtract OAI Files from local files, so we can see if any files are missing locally.
    missing_local = oai_file_names - local_file_names
    if not missing_local:
        logging.info("No missing files!")
    else:
        for file_name in missing_local:
            logging.info(f"Missing file locally: {file_name}")


def find_duplicate_files(client):
    """Finds duplicates files in the OpenAI client"""
    try:
        files_data = files_list()

        files_by_name = {}

        for file in files_data:
            if file.filename in files_by_name:
                files_by_name[file.filename].append(file.id)
            else:
                files_by_name[file.filename] = [file.id]

        duplicates_only = {filename: ids for filename, ids in files_by_name.items() if len(ids) > 1}
        return duplicates_only
    except Exception as e:
        logging.error(f"Failed to find duplicates due to an error: {e}")
        raise Exception(f"Failed to find duplicates") from e


def output_duplicates(duplicates):
    """Lists the duplicates in a readable manner"""
    for file_name, file_ids in duplicates.items():
        logging.info(f"{file_name} has {len(file_ids)} files: {file_ids}")


def check_duplicate_files_usage(duplicates, assistant_file_map):
    """Compares files for all assistants to all files in OpenAI"""
    unused_files = []
    for file_name, file_ids in duplicates.items():
        for file_id in file_ids:
            assistants_not_using_file_id = []

            for assistant in assistant_file_map:
                if file_id not in assistant['files']:
                    assistants_not_using_file_id.append(assistant['id'])
                else:
                    assistants_not_using_file_id = []
                    break
            if len(assistants_not_using_file_id) > 0:
                unused_files.append(file_id)
                logging.info(f"Duplicate file ID '{file_id}' ({file_name}) is NOT used by any assistant.")
    return unused_files


async def list_assistants(client):
    """List all the assistants"""
    assistants = await client.beta.assistants.list()
    return assistants.data


def map_assistants(client, assistants):
    assistant_data = []
    for assistant in assistants:
        # This fixes the files for PROD not showing up.
        assistant = client.beta.assistants.retrieve(assistant.id)
        # Since we want the file ids, if they don't have any we don't need them.
        if len(assistant.file_ids) == 0:
            continue
        assistant_data.append({"id": assistant.id, "files": assistant.file_ids})
    logging.info(f'Map Assistants: {assistant_data}')
    return assistant_data


async def main():

    test_assistant_id = os.getenv('ASSISTANT_ID')

    openai_files = write_and_list_file_information(test_assistant_id)
    local_files = get_local_files("../app/public")

    logging.info(f'Local Files: {local_files}')
    logging.info(f'OAI Files: {openai_files}')

    file_comparison(local_files, openai_files)

    assistants = await assistants_list()

    assistants_with_files = map_assistants(client, assistants)

    duplicate_files = find_duplicate_files(client)
    output_duplicates(duplicate_files)

    unused_files = check_duplicate_files_usage(duplicate_files, assistants_with_files)

    logging.info(f'{len(unused_files)} unused files: {unused_files}')

    if len(sys.argv) >= 2 and sys.argv[1] == "delete":
        for file_id in unused_files:
            try:
                await files_handler.files_delete(file_id)
                logging.info(f"Successfully deleted file ID: {file_id}")
            except Exception as e:
                logging.error(f"Error deleting file ID {file_id}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
