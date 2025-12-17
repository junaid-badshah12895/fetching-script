
from src.project_logging import logger

async def seprate_customers_and_internal_alerts(alerts):
    internal_ids = ["168", "157", "182", 157, 182, 168]  # Example internal company IDs
    internal_alerts = []
    customer_alerts = []
    overall_alerts = {"internal_alerts": internal_alerts, "customer_alerts": customer_alerts}
    try:
        for alert in alerts:
            try:
                company_id = alert.get("metadata", {}).get("company_id")
                if company_id in internal_ids:
                    internal_alerts.append(alert)
                else:
                    customer_alerts.append(alert)
            except Exception as e:
                print(f"Error processing alert: {e}")
        overall_alerts["internal_alerts"] = internal_alerts
        overall_alerts["customer_alerts"] = customer_alerts

        return overall_alerts
    except Exception as e:
        logger.error(f"Error counting alerts: {e}")
        return overall_alerts

