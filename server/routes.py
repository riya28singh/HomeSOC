from flask import Blueprint, request, jsonify
from db import get_db_connection
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    hostname = data.get('hostname')
    ip_address = data.get('ip_address')
    os_info = data.get('os')
    
    if not hostname:
        return jsonify({"error": "Hostname required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
        
    try:
        cursor = conn.cursor()
        # Check if host exists
        cursor.execute("SELECT id FROM hosts WHERE hostname = ?", (hostname,))
        host = cursor.fetchone()
        
        if host:
            # Update
            cursor.execute("""
                UPDATE hosts 
                SET ip_address = ?, os = ?, status = 'online', last_seen = CURRENT_TIMESTAMP 
                WHERE hostname = ?
            """, (ip_address, os_info, hostname))
            host_id = host['id'] # sqlite3.Row access
        else:
            # Insert
            cursor.execute("""
                INSERT INTO hosts (hostname, ip_address, os, status) 
                VALUES (?, ?, ?, 'online')
            """, (hostname, ip_address, os_info))
            host_id = cursor.lastrowid
            
        conn.commit()
        return jsonify({"status": "success", "host_id": host_id}), 200
    except Exception as e:
        print(f"Error in heartbeat: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@api_bp.route('/logs', methods=['POST'])
def ingest_logs():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    hostname = data.get('hostname')
    logs = data.get('logs') # Expecting a list of log entries
    
    if not hostname or not logs:
        return jsonify({"error": "Hostname and logs required"}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
        
    try:
        cursor = conn.cursor()
        
        # Get host_id
        cursor.execute("SELECT id FROM hosts WHERE hostname = ?", (hostname,))
        host = cursor.fetchone()
        if not host:
            return jsonify({"error": "Host not registered"}), 404
            
        host_id = host['id']
        
        for log in logs:
            event_type = log.get('event_type', 'unknown')
            message = log.get('message', '')
            raw_data = json.dumps(log.get('raw_data', {}))
            
            cursor.execute("""
                INSERT INTO logs (host_id, event_type, message, raw_data)
                VALUES (?, ?, ?, ?)
            """, (host_id, event_type, message, raw_data))
            
        conn.commit()
        
        # Trigger Detection
        from detection import process_logs_for_alerts
        # Run in main thread for simplicity now (could use thread/task queue)
        process_logs_for_alerts(host_id, logs)
        
        return jsonify({"status": "success", "logs_processed": len(logs)}), 200
    except Exception as e:
        print(f"Error in ingest_logs: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
