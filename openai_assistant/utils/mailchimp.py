import os

from chainlit.logger import logger
from dotenv import load_dotenv
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

load_dotenv()

MAILCHIMP_LIST_ID = os.getenv('MAILCHIMP_LIST_ID')
MAILCHIMP_REGION = os.getenv('MAILCHIMP_REGION')
MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')

client = Client()
client.set_config({
    "api_key": MAILCHIMP_API_KEY,
    "server": MAILCHIMP_REGION
})


def add_user_to_mailchimp_list(raw_user_data):
    email = raw_user_data.get("email", "error")
    first_name = raw_user_data.get("given_name", "User")
    last_name = raw_user_data.get("family_name", "Family")

    list_id = MAILCHIMP_LIST_ID
    member_info = {
        "email_address": email,
        "status": "subscribed",
        "merge_fields": {
            "FNAME": first_name,
            "LNAME": last_name,
        },
    }

    try:
        response = client.lists.set_list_member(list_id, email,
                                                member_info)

        logger.info("Mailchimp list: User updated successfully.")
        return response
    except ApiClientError as error:
        logger.error(f"Mailchimp list: An error occurred: {error.text}")
