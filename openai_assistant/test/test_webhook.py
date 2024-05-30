import asyncio
import os
from unittest import TestCase

from cl_events.oauth_callback import post_to_discord
from fixture import raw_user_data


class TestWebhook(TestCase):
    def test_webhook(self):
        webhook_url = os.getenv('DISCORD_WEBHOOK')
        action = 'Ran unit tests'  # This would be dynamically replaced with the user's action

        asyncio.run(post_to_discord(webhook_url, raw_user_data, action))
