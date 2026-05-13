import random
import time
import requests
from datetime import datetime

# =========================
# SPLUNK HEC CONFIG
# =========================

HEC_URL = "YOUR_HEC_URL"
HEC_TOKEN = "YOUR_HEC_TOKEN"

HEADERS = {
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
# RAW EVENT TEMPLATES
# =========================

raw_event_templates = {
    "payments_json":
        "{readable_time} {event} "
        "payment_id={payment_id} "
        "amount={amount} "
        "status={status}",

    "auth_json":
        "{readable_time} {event} "
        "user_id={user_id} "
        "status={status}",

    "fraud_json":
        "{readable_time} {event} "
        "payment_id={payment_id} "
        "risk_score={risk_score} "
        "is_fraud={is_fraud}",
}

# =========================
# FRAUD RULES
# =========================

fraud_rules = [
    (90, "FRAUD_DETECTED"),
    (70, "HIGH_RISK"),
    (40, "MEDIUM_RISK"),
    (0, "LOW_RISK"),
]

# =========================
# HELPERS
# =========================

def get_fraud_status(risk_score):

    for threshold, status in fraud_rules:

        if risk_score >= threshold:
            return status


def send_to_splunk(event, sourcetype):

    raw_event = raw_event_templates[sourcetype].format(
        readable_time=datetime.now().strftime("%I:%M:%S%p"),
        **event
    )

    payload = {
        "event": raw_event,
        "sourcetype": sourcetype,
        "source": "python-generator",
        "index": "main"
    }

    response = requests.post(
        HEC_URL,
        headers=HEADERS,
        json=payload,
        verify=False
    )

    print(response.status_code, response.text)

# =========================
# MAIN LOOP
# =========================

while True:

    # =========================
    # PAYMENT EVENT
    # =========================

    payment_status = random.choices(
        list(payment_event_map.keys()),
        weights=[60, 10, 8, 7, 5, 4, 3, 2, 1],
        k=1
    )[0]

    payments = {
        "timestamp": datetime.now().isoformat(),
        "service": "payments-api",
        "event": payment_event_map[payment_status],
        "payment_id": f"pay_{random.randint(1000, 9999)}",
        "amount": random.randint(1, 5000),
        "status": payment_status,
    }

    # =========================
    # AUTH EVENT
    # =========================

    auth_status = random.choices(
        list(auth_event_map.keys()),
        weights=[70, 20, 5, 5],
        k=1
    )[0]

    auth = {
        "timestamp": datetime.now().isoformat(),
        "service": "auth-service",
        "event": auth_event_map[auth_status],
        "user_id": f"user_{random.randint(1000, 9999)}",
        "status": auth_status,
    }

    # =========================
    # FRAUD EVENT
    # =========================

    risk_score = random.randint(1, 100)

    fraud_status = get_fraud_status(risk_score)

    fraud = {
        "timestamp": datetime.now().isoformat(),
        "service": "fraud-detection",
        "event": fraud_event_map[fraud_status],
        "payment_id": f"pay_{random.randint(1000, 9999)}",
        "risk_score": risk_score,
        "status": fraud_status,
        "is_fraud": fraud_status == "FRAUD_DETECTED",
    }

    # =========================
    # SEND EVENTS TO SPLUNK
    # =========================

    send_to_splunk(payments, "payments_json")
    send_to_splunk(auth, "auth_json")
    send_to_splunk(fraud, "fraud_json")

    print("Logs sent to Splunk")

    time.sleep(1)