import requests
import os
import threading


EMAIL_SERVICE_URL = os.getenv('EMAIL_SERVICE_URL', 'http://localhost:4000/send-email')


def _send_email_async(action: str, to_email: str, data: dict):
    """Internal function that actually sends the request."""
    payload = {
        'action': action,
        'to_email': to_email,
        'data': data,
    }
    try:
        response = requests.post(
            EMAIL_SERVICE_URL,
            json=payload,
            timeout=10,  # Gmail SMTP takes ~5 seconds
        )
        result = response.json()
        print(f"[Email Service] ✅ {action} → {to_email} | Status: {response.status_code}")
        return result
    except requests.exceptions.ConnectionError:
        print(f"[Email Service] ⚠️  Not running at {EMAIL_SERVICE_URL}. Skipping.")
    except requests.exceptions.Timeout:
        print(f"[Email Service] ⚠️  Timed out sending {action} to {to_email}. Skipping.")
    except Exception as e:
        print(f"[Email Service] ⚠️  Error: {e}")
    return None


def call_email_service(action: str, to_email: str, data: dict):
    """
    Fire-and-forget email via background thread.
    Never blocks the main Django request.
    """
    if not to_email:
        print(f"[Email Service] Skipping — no email for action: {action}")
        return

    thread = threading.Thread(
        target=_send_email_async,
        args=(action, to_email, data),
        daemon=True
    )
    thread.start()
    # Don't join — fire and forget, never blocks request!
