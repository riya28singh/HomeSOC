import requests
import json
import time

SERVER_URL = "https://riyasingh.pythonanywhere.com/api"

print("Starting Local Phishing Simulation Monitor...")
print("Waiting for a malicious email to arrive...\n")
time.sleep(2)

# Simulate the agent intercepting an incoming email client log
email_log = {
    "hostname": "Windows-User-Endpoint",
    "logs": [
        {
            "event_type": "email_receipt",
            "message": "Incoming email scan",
            "raw_data": {
                "sender": "admin@paypal-security-alert.com",
                "subject": "URGENT: Your account has been suspended",
                "body": "Click here to verify your identity: http://login-update-required.xyz",
                "spf_pass": False
            }
        }
    ]
}

print(f"Detected a new email from: {email_log['logs'][0]['raw_data']['sender']}")
print("Forwarding email metadata to HomeSOC for analysis...\n")

try:
    # Send a quick heartbeat to register the host
    requests.post(f"{SERVER_URL}/heartbeat", json={"hostname": "Windows-User-Endpoint", "ip_address": "192.168.1.100", "os": "Windows 11"})
    
    # Forward the log
    resp = requests.post(f"{SERVER_URL}/logs", json=email_log)
    if resp.status_code == 200:
        print("[+] Spear Phishing payload sent successfully! Check your dashboard.")
    else:
        print(f"[-] Failed to send payload. Status code: {resp.status_code}")
except Exception as e:
    print(f"[-] Connection Error: {e}\nIs the HomeSOC server running?")
