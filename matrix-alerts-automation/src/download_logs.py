import json
import boto3
from src.project_logging import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.config import Config

config = Config(
    max_pool_connections=100 
)

s3 = boto3.client("s3", region_name="us-east-2", config=config) 


def download_logs(s3_key):
    try:
        bucket_name = "cyberguard-failure-logs"
        s3_key = s3_key.replace("https://cyberguard-failure-logs.s3.amazonaws.com/", "")

        response = s3.get_object(Bucket=bucket_name, Key=s3_key)
        data = response["Body"].read()

        return json.loads(data)
    except Exception as e:
        logger.error(f"Error downloading {s3_key}: {e}")
        return {}


def download_logs_parallel(s3_keys, max_workers=10):
    results = []
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_key = {executor.submit(download_logs, key): key for key in s3_keys}
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    print(f"Error in download_logs_parallel - key - {key}: {e}")
        return results
    except Exception as e:
        logger.error(f"Error in download_logs_parallel: {e}")  
        return results


def extract_urls_matrix(messages,channel_name):
    """
    Extract URLs from Slack message blocks

    Args:
        messages (list): List of Slack message dicts.

    Returns:
        list: List of URLs
    """
    urls = []
    try:
        for msg in messages:
            blocks = msg.get("blocks", [])
            log_url = None
            if blocks:
                for block in blocks:

                    #  Find the URL from the Click Me button
                    if block.get("type") == "section" and "accessory" in block:
                        accessory = block["accessory"]
                        if accessory.get("type") == "button" and "url" in accessory:
                            log_url = accessory.get("url", "")
                            urls.append(log_url)
        print(f"Total URLs extracted for {channel_name}: {len(urls)}")
    except Exception as e:
        logger.error(f"Error extracting URLs for {channel_name} : {e}")
    return urls

