import logging
import os
import sys

from dotenv import load_dotenv
from literalai import LiteralClient
from literalai.filter import Filter, threads_filterable_fields

load_dotenv('../../literal/.env')
logging.basicConfig(level=logging.INFO)

LITERAL_API_KEY = os.getenv("LITERAL_API_KEY")

if LITERAL_API_KEY is not None:
    client: LiteralClient = LiteralClient(api_key=LITERAL_API_KEY)
else:
    print("No API key provided. Exiting...")
    sys.exit(1)

# Define the filter criteria using the appropriate fields
thread_filter_criteria = {
    "createdAt": "2022-01-01T00:00:00Z"  # Ensure this field is filterable according to your API docs
}

# Correct structure for a filter
thread_filter_typed: Filter[threads_filterable_fields] = Filter(
    field="createdAt",  # Assuming 'createdAt' is a valid field based on your API's schema
    operator="gte",  # Assuming 'gte' (greater than or equal) is a valid operator in your API
    value="2022-01-01T00:00:00Z"
)

# Use the filter in the API call
threads = client.api.get_threads(filters=[thread_filter_typed])

print(threads.pageInfo)
for thread in threads.data:
    print(thread.to_dict())
