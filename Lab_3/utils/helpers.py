from datetime import datetime

def log_activity(agent_jid, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{agent_jid}] {message}")
    
    with open("disaster_response.log", "a") as f:
        f.write(f"[{timestamp}] [{agent_jid}] {message}\n")

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")