import os
from unittest import TestCase

from dotenv import load_dotenv

from utils.mailchimp import MailchimpHelper

load_dotenv()

MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = os.getenv('MAILCHIMP_LIST_ID')
MAILCHIMP_REGION = os.getenv('MAILCHIMP_REGION')


raw_user_data = {'id': '1234567890', 'email': 'testuser@nowhere.com', 'verified_email': True,
                 'name': 'Test User', 'given_name': 'Test', 'family_name': 'Users', 'picture': '',
                 'locale': 'en'}


class TestMailchimpHelper(TestCase):
    def test_mailchimp(self):

        client = MailchimpHelper(
            MAILCHIMP_API_KEY,
            MAILCHIMP_LIST_ID,
            MAILCHIMP_REGION
        )

        response = client.add_user_to_mailchimp_list(raw_user_data)
        self.assertEqual(response, None)
