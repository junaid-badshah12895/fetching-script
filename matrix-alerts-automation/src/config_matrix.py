import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

matrix_channel_id = os.getenv("MATRIX_CHANNEL_ID")
slack_token = os.getenv("SLACK_TOKEN")
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

channel_mapping = {
    matrix_channel_id: "matrix-agent-matrix-alerts"
}
