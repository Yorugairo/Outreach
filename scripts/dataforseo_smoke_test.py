import base64
import json
import os
import sys
import urllib.request

LOGIN = os.getenv("DATAFORSEO_LOGIN")
PASSWORD = os.getenv("DATAFORSEO_PASSWORD")

if not LOGIN or not PASSWORD:
    print("Missing DATAFORSEO_LOGIN or DATAFORSEO_PASSWORD")
    sys.exit(1)

url = "https://api.dataforseo.com/v3/appendix/errors"
token = base64.b64encode(f"{LOGIN}:{PASSWORD}".encode("utf-8")).decode("ascii")
req = urllib.request.Request(
    url,
    headers={
        "Authorization": f"Basic {token}",
        "User-Agent": "Mozilla/5.0",
    },
)

with urllib.request.urlopen(req, timeout=30) as resp:
    body = resp.read().decode("utf-8", "ignore")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        print(body[:1000])
        raise

print(json.dumps({
    "status_code": payload.get("status_code"),
    "status_message": payload.get("status_message"),
    "tasks_count": payload.get("tasks_count"),
    "version": payload.get("version"),
}, indent=2))
