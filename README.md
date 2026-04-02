# HomeSOC: A Lightweight, Interactive Security Operations Center for Home Networks
HomeSOC is a high-performance, minimalist Security Information and Event Management (SIEM) solution designed specifically for residential and small-office environments. It provides real-time security visibility into unmonitored host nodes with under 1% CPU overhead.

---

## Key Features
- Autonomous Host Agents: Real-time extraction of CPU, RAM, and authentication logs (auth.log).
- Heuristic Detection Engine: Intelligent identification of brute-force attacks, clandestine cryptojacking, and reconnaissance binaries.
- Zero-Latency Dashboard: Modern, asynchronous web interface utilizing AJAX polling for "Live" security alerts.
- Optimized Persistence: High-concurrency SQL ledger utilizing Write-Ahead Logging (WAL) for non-blocking data ingestion.
- Privacy-First: Strictly localized data pipelines for total telemetry sovereignty.

---

## Technology Stack
- Backend: Python 3.10+, Flask REST API
- Database: SQLite3 (B-Tree Architecture with WAL Mode)
- Frontend: Vanilla JavaScript (ES6+), HTML5, CSS3 (Glassmorphism layout)
- Libraries: psutil (Kernel interfacing), flask-sqlalchemy (ORM), requests

---

## Deployment Configurations
HomeSOC can be deployed in two primary configurations. Ensure that you update the SERVER_URL in agent/main.py before cross-device execution.

### 1) Option A: Local Network Deployment (Isolated Lab)
Best for testing on your home Wi-Fi.
1. Server: Run python app.py. It will default to http://0.0.0.0:5000.
2. Finder: Identify your server's local IP (e.g., 192.168.1.10).
3. Agent: Set SERVER_URL = "http://192.168.1.10:5000/api/logs".

### 2) Option B: Public Cloud Deployment (PythonAnywhere)
Best for monitoring hosts across the global internet.
1. Server: Deploy the server/ folder to PythonAnywhere.
2. WSGI Setup: Configure your WSGI file to point to server/app.py.
3. Agent: Set SERVER_URL = "http://YOURUSERNAME.pythonanywhere.com/api/logs".

---

## Installation & Setup
### 1) Ingestion Server Setup (The Central Brain)
```bash
cd server
pip install -r ../requirements.txt
python app.py
```

### 2) Distributed Agent Deployment (The Sensors)
```bash
cd agent
python main.py
```
---

## Security Threat Monitoring
HomeSOC is configured to detect and alert on the following scenarios:
-Clandestine Cryptojacking: Persistent high CPU usage (>90% for 3 cycles).
-Reconnaissance Scans: Detection of forbidden binaries like nmap or wireshark.
-Authentication Anomalies: High-frequency failed SSH/Login attempts.
-Resource Exhaustion: Critical memory/RAM saturation events.
