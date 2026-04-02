from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_db_connection
from routes import api_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/query', methods=['POST'])
def run_query():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    query = data['query']
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        # Fetch results for SELECT or PRAGMA queries
        if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('PRAGMA'):
            rows = cursor.fetchall()
            results = [dict(r) for r in rows]
            return jsonify({"results": results})
        else:
            conn.commit()
            return jsonify({"message": "Query executed successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/api/alerts')
def get_alerts():
    conn = get_db_connection()
    alerts = []
    if conn:
        try:
            cursor = conn.cursor()
            # Join with rules to get the remedy, grouping by alert ID to prevent duplicates from overlapping rules
            query = """
                SELECT a.id, a.timestamp as created_at, h.hostname, a.rule_name, a.severity, a.category, a.remediation_timeline, a.status, a.raw_payload, r.remedy 
                FROM alerts a 
                LEFT JOIN rules r ON a.rule_name = r.name 
                LEFT JOIN hosts h ON a.host_id = h.id
                GROUP BY a.id
                ORDER BY a.timestamp DESC LIMIT 50
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                alerts.append(dict(row))
        except Exception as e:
            print(f"Error fetching alerts: {e}")
        finally:
            conn.close()
    return jsonify(alerts)

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({"message": "Database connection successful!", "db_status": "connected"}), 200
    else:
        return jsonify({"message": "Database connection failed.", "db_status": "disconnected"}), 500

@app.route('/api/alerts/<int:alert_id>/handle', methods=['POST'])
def handle_alert(alert_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE alerts SET status = 'handled' WHERE id = ?", (alert_id,))
        conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
