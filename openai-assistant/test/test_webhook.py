import asyncio
from unittest import TestCase

from app.cl_events.oauth_callback import post_to_discord
from fixture import raw_user_data


class TestWebhook(TestCase):
    def test_webhook(self):
        TEST_WEBHOOK=("https://discord.com/api/webhooks/1214278085390766090"
                      "/hOsdCh799GvhcK5dadAXh_9GMaFNknx3zvAWy98V0dXvLYY7uDwZ_ja18AFhCwuqe70H")

        # Replace 'your_webhook_url' with your actual Discord webhook URL
        webhook_url = TEST_WEBHOOK
        action = 'Ran unit tests'  # This would be dynamically replaced with the user's action

        asyncio.run(post_to_discord(webhook_url, raw_user_data, action))
