import os
import requests
import sys

print("Step 1: Script started", flush=True)

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
print(f"Step 2: ENV loaded. Token exists: {bool(TELEGRAM_TOKEN)}", flush=True)

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
data = {'chat_id': TELEGRAM_CHAT_ID, 'text': 'PTS Test: Bot動いてる？'}
print("Step 3: Sending test message", flush=True)

try:
    r = requests.post(url, json=data, timeout=10)
    print(f"Step 4: Telegram status {r.status_code}", flush=True)
    print(f"Response: {r.text}", flush=True)
except Exception as e:
    print(f"Step 4 ERROR: {e}", flush=True)
    sys.exit(1)

print("Step 5: Done", flush=True)
