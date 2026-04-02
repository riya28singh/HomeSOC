import requests
import sqlite3
import time
import json

SERVER_URL = "http://localhost:5000/api"
DB_PATH = "server/soc_db.sqlite"

def send_fake_log(event_type, message, raw_data):
    payload = {
        "hostname": "test-host",
        "logs": [{
            "event_type": event_type,
            "message": message,
            "raw_data": raw_data
        }]
    }
    try:
        res = requests.post(f"{SERVER_URL}/logs", json=payload)
        print(f"Sent Log [{event_type}]: {res.status_code}")
    except Exception as e:
        print(f"Failed to send log: {e}")

def check_alert(rule_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, rule_name, description FROM alerts WHERE rule_name = ? ORDER BY id DESC LIMIT 1", (rule_name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"[PASS] Alert Found: {row[1]} - {row[2]}")
        return True
    else:
        print(f"[FAIL] Alert NOT Found for {rule_name}")
        return False

def send_heartbeat():
    payload = {
        "hostname": "test-host",
        "ip_address": "127.0.0.1",
        "os": "TestOS"
    }
    try:
        res = requests.post(f"{SERVER_URL}/heartbeat", json=payload)
        print(f"Sent Heartbeat: {res.status_code}")
    except Exception as e:
        print(f"Failed to send heartbeat: {e}")

if __name__ == "__main__":
    print("--- Verifying Detection Logic ---")
    
    # Register host first
    send_heartbeat()
    time.sleep(1)
    
    # Test 1: High CPU (Threshold > 50)
    print("\nTest 1: Sending High CPU Log (99%)")
    send_fake_log(
        "system_metric", 
        "CPU High", 
        {"cpu_percent": 99.9, "memory_percent": 40}
    )
    time.sleep(1) # Wait for processing
    check_alert("High CPU Load")

    # Test 2: Forbidden Process (nc)
    print("\nTest 2: Sending Forbidden Process Log (nc)")
    send_fake_log(
        "process_list", 
        "Process List Check", 
        {"processes": [{"name": "firefox"}, {"name": "nc"}, {"name": "code"}]}
    )
    time.sleep(1)
    check_alert("Forbidden Process")
