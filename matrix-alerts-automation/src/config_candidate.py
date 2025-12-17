import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

candidate_matrix_channel_id = os.getenv("CANDIDATE_MATRIX_CHANNEL_ID")
slack_token = os.getenv("SLACK_TOKEN")
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

channel_mapping = {
    candidate_matrix_channel_id: "matrix-candidate-alerts"
}
