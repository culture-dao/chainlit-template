import logging
import os
import unittest

import literalai

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestLiteral(unittest.IsolatedAsyncioTestCase):
    async def test_literal(self):
        key = os.getenv('LITERAL_API_KEY')
        client = literalai.LiteralClient(api_key=key)
        api = client.api
        users = set()
        index = 0
        while True:
            result = await api.list_threads(after=index)

            if not result.data:
                break # Exit the loop if there are no more threads to process.

            for thread in result.data:
                if thread.user is not None:
                    logging.info(thread.user.identifier)
                    users.add(thread.user.identifier)

            if result.pageInfo.hasNextPage:
                # Update 'index' to the 'endCursor' from 'pageInfo' for the next iteration
                index = result.pageInfo.endCursor
            else:
                break  # Exit the loop if there are no more pages
        logging.info(users)


