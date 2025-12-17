import json
import time
import asyncio
from datetime import datetime, timedelta
from rich import print
from src.config import (
    agent_matrix_channel_id,
    channel_mapping
)
from src.project_logging import logger
from src.fetch_slack_alert import get_messages_between_async
from src.separate_logs import seprate_customers_and_internal_alerts
from src.download_logs import (
    extract_urls_matrix,
    download_logs_parallel,
)

# ============================================
# CONFIGURE YOUR DATE AND TIME HERE (UTC TIME)
# ============================================
# Default: Yesterday 19:00:00 to Today 19:00:00 (UTC)
# Adjust these values as needed
USE_DEFAULT_DATES = False  # Set to True to use yesterday-to-today, False to use custom dates below

# Custom date/time configuration (only used if USE_DEFAULT_DATES = False)
START_DATE = "2025-12-14"  # Format: YYYY-MM-DD
START_TIME = "04:00:00"    # Format: HH:MM:SS (UTC)

END_DATE = "2025-12-15"    # Format: YYYY-MM-DD
END_TIME = "04:00:00"      # Format: HH:MM:SS (UTC)
# ============================================


async def process_matrix_alerts(channel_id, start_datetime, end_datetime):
    try:
        messages = await get_messages_between_async(
            channel_id=channel_id,
            start_dt=start_datetime,
            end_dt=end_datetime,
        )
        log_urls = extract_urls_matrix(messages, channel_mapping.get(channel_id))
        logs_list = []
        batch_size = 10
        for i in range(0, len(log_urls), batch_size):
            batch = log_urls[i : i + batch_size]
            results = download_logs_parallel(batch, batch_size)
            logs_list.extend(results)
        
        print(f"Total logs downloaded for {channel_mapping.get(channel_id)} : {len(logs_list)}")
        return logs_list
    except Exception as e:
        logger.error(f"Error processing {channel_mapping.get(channel_id)} alerts: {e}")
        return []


def get_datetime_tuples():
    """Convert configured dates/times to datetime tuples"""
    if USE_DEFAULT_DATES:
        # Use the same logic as app.py: yesterday 19:00:00 to today 19:00:00 (UTC)
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        
        start_dt_obj = yesterday.replace(hour=19, minute=0, second=0, microsecond=0)
        end_dt_obj = now.replace(hour=19, minute=0, second=0, microsecond=0)
    else:
        # Use custom configured dates/times
        start_dt_obj = datetime.strptime(f"{START_DATE} {START_TIME}", "%Y-%m-%d %H:%M:%S")
        end_dt_obj = datetime.strptime(f"{END_DATE} {END_TIME}", "%Y-%m-%d %H:%M:%S")
    
    # Convert to tuples (year, month, day, hour, minute, second)
    start_tuple = (
        start_dt_obj.year, start_dt_obj.month, start_dt_obj.day,
        start_dt_obj.hour, start_dt_obj.minute, start_dt_obj.second
    )
    end_tuple = (
        end_dt_obj.year, end_dt_obj.month, end_dt_obj.day,
        end_dt_obj.hour, end_dt_obj.minute, end_dt_obj.second
    )
    
    return start_tuple, end_tuple, start_dt_obj, end_dt_obj


async def main():
    try:
        start_time = time.time()
        
        # Get configured date/time
        start_tuple, end_tuple, start_dt, end_dt = get_datetime_tuples()
        
        print(f"Processing alerts from {start_dt} to {end_dt} (UTC)")
        
        # Process agent_matrix channel with configured date/time
        process_agent_matrix_alerts = await process_matrix_alerts(
            channel_id=agent_matrix_channel_id,
            start_datetime=start_tuple,
            end_datetime=end_tuple
        )

        # Separate customer and internal alerts
        separate_agent_matrix = await seprate_customers_and_internal_alerts(process_agent_matrix_alerts)

        customer_agent_matrix_alerts = separate_agent_matrix.get("customer_alerts", [])
        notell_agent_matrix_alerts = separate_agent_matrix.get("internal_alerts", [])

        customer_alerts_count = {
            "Overall Customer agent_matrix Alerts": len(customer_agent_matrix_alerts),
        }
        notell_alerts_count = {
            "Overall Notell agent_matrix Alerts": len(notell_agent_matrix_alerts),
        }

        print("Customer Alerts Count:", customer_alerts_count)
        print("Notell Alerts Count:", notell_alerts_count)

        with open("customer_agent_manual_alerts.json", "w") as f:
            json.dump(customer_agent_matrix_alerts, f, indent=4)
        with open("notell_agent_manual_alerts.json", "w") as f:
            json.dump(notell_agent_matrix_alerts, f, indent=4)

        end = time.time() - start_time
        print(f"Total time taken to process all alerts: {end} seconds")
        return {
            "statusCode": 200,
            "body": json.dumps(f"Task completed in {end} seconds")
        }
    except Exception as e:
        logger.error(f"Error in main : {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


if __name__ == "__main__":
    asyncio.run(main())