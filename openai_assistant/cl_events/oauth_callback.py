import asyncio
import logging
import os
from typing import Dict, Optional, Callable, Any

import chainlit as cl
import requests

from mailchimp import add_user_to_mailchimp_list

discord_webhook = os.environ.get("DISCORD_WEBHOOK")

logger = logging.getLogger("chainlit")


async def oauth_callback_logic(provider_id: str, token: str, raw_user_data: Dict[str, str], default_app_user: cl.User) -> \
        Optional[cl.User]:
    logger.info(f"raw_user_data: {raw_user_data}")
    logger.info(f"provider_id: {provider_id}")
    action = "Authenticated"

    # Get the current event loop
    loop = asyncio.get_event_loop()

    # Offload the Discord posting to a background task
    offload_to_background(loop, post_to_discord, discord_webhook, raw_user_data, action)

    offload_to_background(loop, add_user_to_mailchimp_list, raw_user_data)

    return default_app_user


def offload_to_background(loop: asyncio.AbstractEventLoop, func: Callable, *args: Any, **kwargs: Any) -> None:
    """
    Offload a function to run in the background on the given event loop.

    :param loop: The event loop to run the background task on.
    :param func: The function to run in the background.
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    """
    if asyncio.iscoroutinefunction(func):
        # Schedule the coroutine function directly if it's awaitable
        asyncio.run_coroutine_threadsafe(func(*args, **kwargs), loop)
    else:
        # Wrap the synchronous function in a coroutine
        async def wrapper():
            return func(*args, **kwargs)

        asyncio.run_coroutine_threadsafe(wrapper(), loop)


async def post_to_discord(webhook_url, raw_user_data, action):
    email = raw_user_data.get("email", "error")
    name = raw_user_data.get("name", "error")

    data = {
        "content": f"{name}({email}) has performed the following action: {action}",
        "username": "APP_NAME"  # TODO: make config/env var
    }

    try:
        response = requests.post(webhook_url, json=data)

        if response.status_code == 204:
            logger.info("Successfully sent message to Discord!")
        else:
            logger.error(f"Failed to send message. Status code: {response.status_code}")

    except Exception as e:
        logger.error(f"Discord webhook failure: {e}")