import time
import requests
import socket
import platform
import random
import psutil
import subprocess
import os

# Configuration
SERVER_URL = "https://riyasingh.pythonanywhere.com/api"
HEARTBEAT_INTERVAL = 10
LOG_INTERVAL = 5

# --- DEMO MODE SETTING ---
# If False, sends real metrics, network connections, and OS authentication logs.
DEMO_MODE = False

def get_system_info():
    hostname = "demo-kali-endpoint" if DEMO_MODE else socket.gethostname()
    os_info = "Kali Linux 2024.1" if DEMO_MODE else f"{platform.system()} {platform.release()}"
    return {
        "hostname": hostname,
        "ip_address": "192.168.1.55" if DEMO_MODE else "127.0.0.1",
        "os": os_info
    }

def send_heartbeat(sys_info):
    try:
        response = requests.post(f"{SERVER_URL}/heartbeat", json=sys_info)
        if response.status_code == 200:
            pass # Silent success
    except Exception as e:
        print(f"[-] Error sending heartbeat: {e}")

def generate_random_demo_logs():
    scenario = random.randint(1, 6)
    if scenario == 1:
        return [{"event_type": "system_metric", "message": "High CPU Detected", "raw_data": {"cpu_percent": random.randint(60, 99), "memory_percent": 30}}]
    elif scenario == 2:
        return [{"event_type": "system_metric", "message": "High RAM Detected", "raw_data": {"cpu_percent": 20, "memory_percent": random.randint(80, 99)}}]
    elif scenario == 3:
        return [{"event_type": "auth_log", "message": "sshd: failed password for root from 10.0.0.5", "raw_data": {}}]
    elif scenario == 4:
        return [{"event_type": "auth_log", "message": "Successful login", "raw_data": {"user": "root", "method": "ssh"}}]
    elif scenario == 5:
        return [{"event_type": "process_list", "message": "Process snapshot", "raw_data": {"processes": [{"name": "nmap", "pid": random.randint(1000, 9000)}]}}]
    elif scenario == 6:
        return [{"event_type": "process_list", "message": "Process snapshot", "raw_data": {"processes": [{"name": "xmrig", "pid": random.randint(1000, 9000)}]}}]

def get_real_metrics():
    metrics = []
    
    # 1. Core Telemetry (CPU & RAM)
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    metrics.append({"event_type": "system_metric", "message": "Metrics Snapshot", "raw_data": {"cpu_percent": cpu, "memory_percent": mem}})
    
    # 2. Process Tree
    procs = []
    for proc in psutil.process_iter(['name', 'memory_percent']):
        try:
            procs.append(proc.info)
        except:
            pass
    procs.sort(key=lambda p: p['memory_percent'] if p['memory_percent'] else 0, reverse=True)
    metrics.append({"event_type": "process_list", "message": "Top Memory Processes", "raw_data": {"processes": procs[:5]}})
    
    # 3. Active External Network Connections (Requires Admin on Windows, root/normal on Linux)
    try:
        conns = []
        for c in psutil.net_connections(kind='inet'):
            if c.status == 'ESTABLISHED' and c.raddr:
                if c.raddr.ip != '127.0.0.1':
                    conns.append({"remote_ip": c.raddr.ip, "remote_port": c.raddr.port})
        if conns:
            metrics.append({"event_type": "network_flow", "message": "Active Outbound Connections", "raw_data": {"connections": conns}})
    except Exception as e:
        # AccessDenied is thrown if psutil.net_connections() is run without root/admin privileges
        if "AccessDenied" not in str(e):
            print(f"[-] Network connection access error: {e}")
            
    # 4. OS Identity Logs (Failed Logins)
    auth_events = []
    try:
        sys_os = platform.system()
        if sys_os == "Windows":
            # Requires Windows Administrator privileges
            cmd = ['powershell', '-Command', 'Get-EventLog -LogName Security -InstanceId 4625 -Newest 3 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Message']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "Failure Reason:" in result.stdout:
                auth_events.append("System recorded failed interactive logins.")
        elif sys_os == "Linux":
            # Requires Linux root/sudo to read /var/log/auth.log
            if os.path.exists("/var/log/auth.log"):
                cmd = ['tail', '-n', '50', '/var/log/auth.log']
                result = subprocess.run(cmd, capture_output=True, text=True)
                if "Failed password" in result.stdout:
                    auth_events.append("Failed SSH/Local login detected in auth.log")
    except Exception:
        pass
        
    if auth_events:
        metrics.append({"event_type": "auth_log", "message": "Failed Authentication Activity", "raw_data": {"events": auth_events}})
        
    return metrics

def run_agent():
    print(f"Starting Home SOC Agent (WORKING MODEL, DEMO_MODE: {DEMO_MODE})...")
    print("Agent is now scanning CPU, RAM, Processes, TCP Connections, and OS Event Logs!")
    sys_info = get_system_info()
    
    last_heartbeat = 0
    
    while True:
        current_time = time.time()
        if current_time - last_heartbeat > HEARTBEAT_INTERVAL:
            send_heartbeat(sys_info)
            last_heartbeat = current_time
            
        logs = generate_random_demo_logs() if DEMO_MODE else get_real_metrics()
        
        payload = {"hostname": sys_info['hostname'], "logs": logs}
        try:
            resp = requests.post(f"{SERVER_URL}/logs", json=payload)
            if resp.status_code == 200:
                print(f"[+] Active Payload sent. Server ingested {len(logs)} telemetry blocks.")
        except Exception as e:
            pass
            
        time.sleep(LOG_INTERVAL)

if __name__ == "__main__":
    try:
        run_agent()
    except KeyboardInterrupt:
        print("\nAgent gracefully stopped.")
