-- Home SOC Database Schema

-- Users Table (Optional, for Admin Login later)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hosts Table (Agents phoning home)
CREATE TABLE IF NOT EXISTS hosts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    os VARCHAR(50),
    status VARCHAR(20) DEFAULT 'offline', -- 'online', 'offline', 'warning'
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Logs Table (Raw data from agents)
CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    host_id INT,
    event_type VARCHAR(50), -- 'login', 'process', 'network', 'system'
    message TEXT,
    raw_data JSON, -- Stores flexible extra details
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    host_id INT,
    rule_name VARCHAR(100),
    severity VARCHAR(20), -- 'low', 'medium', 'high'
    category VARCHAR(50),
    remediation_timeline VARCHAR(50),
    description TEXT,
    raw_payload TEXT,
    status VARCHAR(20) DEFAULT 'new', -- 'new', 'investigating', 'resolved'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE SET NULL
);

-- Rules Table (Dynamic detection rules)
CREATE TABLE IF NOT EXISTS rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    condition_logic TEXT, -- JSON or pseudo-code describing the rule
    severity VARCHAR(20) DEFAULT 'medium',
    category VARCHAR(50),
    remediation_timeline VARCHAR(50),
    remedy TEXT, -- Steps to mitigate the threat
    enabled BOOLEAN DEFAULT TRUE
);
