import logging
import os
import sys

from dotenv import load_dotenv
from literalai import LiteralClient

# The username of the user you want to delete
identifier = ""

load_dotenv()
logging.basicConfig(level=logging.INFO)

LITERAL_API_KEY = os.getenv("LITERAL_API_KEY")

if LITERAL_API_KEY is not None:
    client = LiteralClient(api_key=LITERAL_API_KEY)
else:
    print("No API key provided. Exiting...")
    sys.exit(1)


async def create_user(user_identifier):
    user = await client.api.create_user(identifier=user_identifier)
    logging.info("New user created")
    return user


async def fetch_user(user_identifier):
    user = await client.api.get_user(identifier=user_identifier)
    return user


async def delete_user(user_id):
    user = await client.api.delete_user(id=user_id)
    logging.info("User Deleted")
    return user


async def main():
    user = await fetch_user(identifier)
    logging.info(user)

    if user is not None:
        deleted_user = await delete_user(user.id)
        logging.info(deleted_user)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
