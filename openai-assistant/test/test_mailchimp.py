from unittest import TestCase

from fixture import raw_user_data
from mailchimp import add_user_to_mailchimp_list


class TestMailchimp(TestCase):
    def test_mailchimp(self):
        # Example usage
        response = add_user_to_mailchimp_list(raw_user_data)
        self.assertEqual(response, None)
