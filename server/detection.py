from db import get_db_connection
import json

def load_rules():
    conn = get_db_connection()
    if not conn:
        return []
    
    rules = []
    try:
        cursor = conn.cursor() # Dictionary cursor in sqlite3 (row_factory)
        cursor.execute("SELECT * FROM rules WHERE enabled = 1")
        # specific for my db setup:
        # sqlite row can be iterated, mysql dictionary cursor returns dicts
        # forcing dict for compatibility
        rows = cursor.fetchall()
        for row in rows:
            # Convert Row object to dict if needed (sqlite3.Row behaves like dict mostly)
            rules.append(dict(row))
    except Exception as e:
        print(f"Error loading rules: {e}")
    finally:
        conn.close()
    return rules

def evaluate_log(log_entry, rules):
    """
    Evaluates logs against rules with support for:
    - Keywords (simple string match)
    - Numeric comparisons (>, <) for metrics
    - List inclusion (contains) for processes
    """
    alerts_to_produce = []
    
    for rule in rules:
        try:
            condition = rule.get('condition_logic', '')
            match = False
            
            # 1. Parse Condition
            if condition.startswith('{'):
               try:
                   cond_data = json.loads(condition)
                   field = cond_data.get('field', 'message')
                   value = cond_data.get('value')
                   operator = cond_data.get('operator', 'contains') # Default to contains
               except json.JSONDecodeError:
                   # Fallback to keyword match if JSON is invalid
                   cond_data = {}
                   field = 'message'
                   value = condition
                   operator = 'contains'
            else:
                # Legacy simple text match
                field = 'message'
                value = condition
                operator = 'contains'

            # 2. Extract Data from Log based on Field
            log_value = None
            
            # Special handling for raw_data fields (cpu_percent, process_list)
            raw_data = {}
            if isinstance(log_entry.get('raw_data'), str):
                try:
                    raw_data = json.loads(log_entry.get('raw_data'))
                except:
                    raw_data = {}
            elif isinstance(log_entry.get('raw_data'), dict):
                raw_data = log_entry.get('raw_data')

            if field in ['cpu_percent', 'memory_percent', 'disk_percent']:
                log_value = raw_data.get(field)
            elif field == 'process_list':
                # Extract list of process names for easier searching
                procs = raw_data.get('processes', [])
                log_value = [p.get('name', '') for p in procs]
            elif field in ['message', 'event_type']:
                log_value = log_entry.get(field)
            elif field == 'raw_data':
                 # Legacy root check support
                 log_value = json.dumps(raw_data)

            # 3. Evaluate Logic
            if log_value is not None:
                if operator == '>':
                    # Numeric Greater Than
                    if isinstance(log_value, (int, float)) and isinstance(value, (int, float)):
                        if log_value > value:
                            match = True
                elif operator == '<':
                     # Numeric Less Than
                    if isinstance(log_value, (int, float)) and isinstance(value, (int, float)):
                        if log_value < value:
                            match = True
                elif operator == 'contains':
                    # String or List Contains
                    if isinstance(log_value, list):
                        # List check (e.g., process list)
                        if value in log_value:
                            match = True
                    elif isinstance(log_value, str):
                        # String check
                        if str(value).lower() in log_value.lower():
                            match = True
            
            if match:
                alerts_to_produce.append({
                    'rule': rule,
                    'trigger_log': log_entry
                })
                
        except Exception as e:
            print(f"Error evaluating rule {rule.get('name')}: {e}")
            
    return alerts_to_produce

def process_logs_for_alerts(host_id, logs):
    rules = load_rules()
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        cursor = conn.cursor()
        for log in logs:
            triggered_events = evaluate_log(log, rules)
            for event in triggered_events:
                rule = event['rule']
                raw_payload = json.dumps(event['trigger_log'])
                print(f"[!] Alert Triggered: {rule['name']} on host {host_id}")
                cursor.execute("""
                    INSERT INTO alerts (host_id, rule_name, severity, category, remediation_timeline, description, raw_payload, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'new')
                """, (host_id, rule['name'], rule['severity'], rule.get('category', 'Uncategorized'), rule.get('remediation_timeline', 'N/A'), rule['description'], raw_payload))
        
        conn.commit()
    except Exception as e:
        print(f"Error processing alerts: {e}")
    finally:
        conn.close()
