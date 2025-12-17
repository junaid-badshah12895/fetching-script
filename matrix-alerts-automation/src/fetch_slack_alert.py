import ssl
import certifi
from datetime import datetime, timezone
from slack_sdk.web.async_client import AsyncWebClient
from src.project_logging import logger
from src.config import slack_token, channel_mapping
from src.config_candidate import slack_token, channel_mapping
from src.config_matrix import slack_token, channel_mapping

ssl_context = ssl.create_default_context(cafile=certifi.where())
client = AsyncWebClient(token=slack_token, ssl=ssl_context)


async def get_messages_between(channel_id, start_dt, end_dt):
    """
    Fetch all Slack messages between two datetime tuples.
    
    start_dt / end_dt should be in format:
        (year, month, day, hour, minute, second, 0, 0, 0)
    """
    all_messages = []
    cursor = None
    try:
        print(f"Fetching messages from {start_dt} to {end_dt}")
        start_ts = str(datetime(*start_dt).replace(tzinfo=timezone.utc).timestamp())
        end_ts = str(datetime(*end_dt).replace(tzinfo=timezone.utc).timestamp())
        print(f"**Fetching messages from {start_ts} to {end_ts}")

        while True:
            response = await client.conversations_history(
                channel=channel_id,
                oldest=start_ts,
                latest=end_ts,
                inclusive=True,
                limit=200,  # max per call
                cursor=cursor
            )
            
            all_messages.extend(response["messages"])
            
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        print(f"Total alerts fetched for {channel_mapping.get(channel_id)} : {len(all_messages)}")
        return all_messages
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return all_messages


async def get_messages_between_async(channel_id, start_dt, end_dt):
    return await get_messages_between(channel_id, start_dt, end_dt)

