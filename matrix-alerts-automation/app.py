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



async def process_matrix_alerts(channel_id):
    try:
        # current date
        now = datetime.utcnow()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        # yesterday date (UTC)
        yesterday = now - timedelta(days=1)
        y_year = yesterday.strftime("%Y")
        y_month = yesterday.strftime("%m")
        y_day = yesterday.strftime("%d")
        
        messages = await get_messages_between_async(
            channel_id=channel_id,
             start_dt=(int(y_year), int(y_month), int(y_day), 19, 0, 0),
            # start_dt=(int(year), int(month), int(day), 4, 13, 0),
            end_dt=(int(year), int(month), int(day), 19, 0, 0),
        )
        log_urls = extract_urls_matrix(messages,channel_mapping.get(channel_id))
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


async def main():
    try:
        start_time = time.time()

        # process agent_matrix channel
        process_agent_matrix_alerts = await process_matrix_alerts(channel_id=agent_matrix_channel_id)

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

        with open("customer_manual_alerts.json", "w") as f:
            json.dump(customer_agent_matrix_alerts, f, indent=4)
        with open("notell_manual_alerts.json", "w") as f:
            json.dump(notell_agent_matrix_alerts, f, indent=4)

        end = time.time() - start_time
        print(f"Total time taken to process all alerts: {end} seconds")
        return {
            "statusCode": 200,
            "body": json.dumps(f"Task completed at {end} UTC")
        }
    except Exception as e:
        logger.error(f"Error in main : {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }



if __name__ == "__main__":
    asyncio.run(main())
