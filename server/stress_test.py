import requests
import json
import time

SERVER_URL = "http://localhost:5000/api"
HOSTNAME = "demo-host"

def send_alert(alert_type, payload):
    data = {
        "hostname": HOSTNAME,
        "logs": [
            {
                "event_type": alert_type,
                "message": payload.get("message", ""),
                "raw_data": payload
            }
        ]
    }
    requests.post(f"{SERVER_URL}/logs", json=data)
    print(f"Sent {alert_type} payload.")

# Register host
requests.post(f"{SERVER_URL}/heartbeat", json={"hostname": HOSTNAME, "ip_address": "192.168.1.100", "os": "Ubuntu Linux"})

# Low: CPU Spike (Rule: > 50)
send_alert("metrics", {"cpu_percent": 85})
time.sleep(1)

# Low: RAM Spike (Rule: > 70)
send_alert("metrics", {"memory_percent": 92})
time.sleep(1)

# Medium: Failed Logins
send_alert("auth", {"message": "failed login attempt for admin"})
time.sleep(1)

# Medium: Root Access
send_alert("auth", {"raw_data": "root user logged in via ssh"})
time.sleep(1)

# High: Nmap Scan
send_alert("process_list", {"processes": [{"name": "nmap", "pid": 1234}]})
time.sleep(1)

# High: Cryptominer
send_alert("process_list", {"processes": [{"name": "xmrig", "pid": 5678}]})

print("All test alerts sent successfully.")
