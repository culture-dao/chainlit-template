import asyncio
import json
import logging
import os
import sys

import yaml
from openai.pagination import AsyncPage
from openai.types import FileObject
from openai.types.beta import VectorStore, Assistant

from utils import files_handler, assistant_handler
from utils.openai_utils import client, AsyncPaginatorHelper, load_yaml

from typing import List

VECTOR_STORES_CONFIG_PATH = 'vector_stores.yaml'


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
logging.getLogger("httpx").setLevel("WARNING")


async def vector_stores_create() -> VectorStore:
    try:
        return await client.beta.vector_stores.create()
    except Exception as e:
        logging.error(f"Failed to create vector_stores due to an error: {e}")
        raise Exception("vector_stores_create failed") from e


async def vector_stores_list() -> List[VectorStore]:
    """Lists all the vector_stores for a specific assistant"""
    try:
        vector_stores: AsyncPage[VectorStore] = await client.beta.vector_stores.list()
        return await AsyncPaginatorHelper.collect_all_items(vector_stores)

    except Exception as e:
        logging.error(f"Failed to list vector_stores due to an error: {e}")
        raise Exception("vector_stores_list failed") from e


async def vector_stores_retrieve(vector_store_id: str) -> VectorStore:
    try:
        return await client.beta.vector_stores.retrieve(vector_store_id)
    except Exception as e:
        logging.error(f"Failed to retrieve vector_stores due to an error: {e}")
        raise Exception("vector_stores_retrieve failed") from e


async def main():
    results = load_yaml(VECTOR_STORES_CONFIG_PATH, VectorStore)
    if not results:
        results = await vector_stores_list()
        if not results:
            results = await vector_stores_create()
        with open(VECTOR_STORES_CONFIG_PATH, 'w') as f:
            yaml.dump(results, f)

# OLD SHIT HERE


async def format_file_information(files: List[FileObject]):
    """Retrieves the metadata of a file from OpenAI and stores it in a dictionary"""
    file_dict = []

    for file in files:
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


async def write_and_list_file_information(assistant_id):
    """Lists the files for an assistant and writes them to a JSON"""
    try:
        files: List[FileObject]
        files = await files_handler.files_list()
        if files:
            formatted_information = await format_file_information(files)
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


async def find_duplicate_files():
    """Finds duplicates files in the OpenAI client"""
    try:
        files_data = await files_handler.files_list()

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
        raise Exception("Failed to find duplicates") from e


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


def map_assistants(assistants):
    # BROKEN v2 API
    assistant_data = []
    for assistant in assistants:
        # This fixes the files for PROD not showing up.
        assistant = assistant_handler.assistant_retrieve(assistant.id)

        # Broken
        if len(assistant.file_ids) == 0:
            continue
        assistant_data.append({"id": assistant.id, "files": assistant.file_ids})
    logging.info(f'Map Assistants: {assistant_data}')
    return assistant_data


async def old():
    """
    This was originally meant to sync files, but no longer works since we move to beta v2
    """
    test_assistant_id = os.getenv('ASSISTANT_ID')

    openai_files = await write_and_list_file_information(test_assistant_id)
    local_files = get_local_files("../app/public")

    logging.info(f'Local Files: {local_files}')
    logging.info(f'OAI Files: {openai_files}')

    file_comparison(local_files, openai_files)

    assistants: List[Assistant] = await assistant_handler.assistants_list()
    # Breaks down here, assistants have file stores and that's what we need to look at.
    # assistants_with_files = map_assistants(assistants)
    #
    # duplicate_files = await find_duplicate_files()
    # output_duplicates(duplicate_files)
    #
    # unused_files = check_duplicate_files_usage(duplicate_files, assistants_with_files)
    #
    # logging.info(f'{len(unused_files)} unused files: {unused_files}')
    #
    # if len(sys.argv) >= 2 and sys.argv[1] == "delete":
    #     for file_id in unused_files:
    #         try:
    #             await files_handler.files_delete(file_id)
    #             logging.info(f"Successfully deleted file ID: {file_id}")
    #         except Exception as e:
    #             logging.error(f"Error deleting file ID {file_id}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
