import random
import time
import requests
from datetime import datetime

# =========================
# SPLUNK HEC CONFIG
# =========================

HEC_URL = "YOUR_URL"
HEC_TOKEN = "YOUR_TOKEN"

headers = {
    "Authorization": f"Splunk {HEC_TOKEN}",
    "Content-Type": "application/json"
}

# =========================
# EVENT MAPS
# =========================

payment_event_map = {
    "SUCCESS": "payment_processed",
    "FAILED": "payment_failed",
    "PENDING": "payment_pending",
    "DECLINED": "payment_declined",
    "REFUNDED": "payment_refunded",
    "CANCELLED": "payment_cancelled",
    "TIMEOUT": "payment_timeout",
    "FRAUD_SUSPECTED": "payment_fraud_alert",
    "CHARGEBACK": "payment_chargeback",
}

auth_event_map = {
    "SUCCESS": "user_login",
    "FAILED": "user_login_failed",
    "LOCKED_OUT": "user_account_locked",
    "PASSWORD_EXPIRED": "user_password_expired",
}

fraud_event_map = {
    "LOW_RISK": "fraud_check_passed",
    "MEDIUM_RISK": "fraud_check_review",
    "HIGH_RISK": "fraud_check_flagged",
    "FRAUD_DETECTED": "fraud_check_blocked",
}

# =========================
# SEND TO SPLUNK
# =========================

def send_to_splunk(event, sourcetype):

    timestamp = datetime.now().strftime("%I:%M:%S%p")

    if sourcetype == "payments_json":

        raw_event = (
            f"{timestamp} "
            f"{event['event']} "
            f"payment_id={event['payment_id']} "
            f"amount={event['amount']} "
            f"status={event['status']}"
        )

    elif sourcetype == "auth_json":

        raw_event = (
            f"{timestamp} "
            f"{event['event']} "
            f"user_id={event['user_id']} "
            f"status={event['status']}"
        )

    elif sourcetype == "fraud_json":

        raw_event = (
            f"{timestamp} "
            f"{event['event']} "
            f"payment_id={event['payment_id']} "
            f"risk_score={event['risk_score']} "
            f"is_fraud={event['is_fraud']}"
        )

    payload = {
        "event": raw_event,
        "sourcetype": sourcetype,
        "source": "python-generator",
        "index": "main"
    }

    response = requests.post(
        HEC_URL,
        headers=headers,
        json=payload,
        verify=False
    )

    print(response.status_code)
    print(response.text)

# =========================
# MAIN LOOP
# =========================

while True:

    payment_status = random.choices(
        [
            "SUCCESS",
            "FAILED",
            "PENDING",
            "DECLINED",
            "REFUNDED",
            "CANCELLED",
            "TIMEOUT",
            "FRAUD_SUSPECTED",
            "CHARGEBACK",
        ],
        weights=[60, 10, 8, 7, 5, 4, 3, 2, 1],
        k=1,
    )[0]

    auth_status = random.choices(
        ["SUCCESS", "FAILED", "LOCKED_OUT", "PASSWORD_EXPIRED"],
        weights=[70, 20, 5, 5],
        k=1,
    )[0]

    payments = {
        "timestamp": datetime.now().isoformat(),
        "service": "payments-api",
        "event": payment_event_map[payment_status],
        "payment_id": f"pay_{random.randint(1000, 9999)}",
        "amount": random.randint(1, 5000),
        "status": payment_status,
    }

    auth = {
        "timestamp": datetime.now().isoformat(),
        "service": "auth-service",
        "event": auth_event_map[auth_status],
        "user_id": f"user_{random.randint(1000, 9999)}",
        "status": auth_status,
    }

    risk_score = random.randint(1, 100)

    if risk_score >= 90:
        fraud_status = "FRAUD_DETECTED"
    elif risk_score >= 70:
        fraud_status = "HIGH_RISK"
    elif risk_score >= 40:
        fraud_status = "MEDIUM_RISK"
    else:
        fraud_status = "LOW_RISK"

    fraud = {
        "timestamp": datetime.now().isoformat(),
        "service": "fraud-detection",
        "event": fraud_event_map[fraud_status],
        "payment_id": f"pay_{random.randint(1000, 9999)}",
        "risk_score": risk_score,
        "status": fraud_status,
        "is_fraud": fraud_status == "FRAUD_DETECTED",
    }

    # Send events to Splunk
    send_to_splunk(payments, "payments_json")
    send_to_splunk(auth, "auth_json")
    send_to_splunk(fraud, "fraud_json")

    print("Logs sent to Splunk")

    time.sleep(1)