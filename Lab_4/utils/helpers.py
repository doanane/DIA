from datetime import datetime
import os

def log_relief_operation(agent_jid, agent_type, message):
    """Log all relief operations to file and console"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] [{agent_type}] {message}"
    
    print(log_entry)
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Write to daily log file
    date_str = datetime.now().strftime("%Y%m%d")
    with open(f"logs/relief_operations_{date_str}.log", "a") as f:
        f.write(log_entry + "\n")

def calculate_priority_score(disaster):
    """Calculate priority score for task assignment"""
    severity_weight = disaster.severity.value * 25
    population_weight = min(disaster.affected_population / 100, 50)
    casualty_weight = disaster.casualties * 0.5
    damage_weight = disaster.damaged_buildings * 0.1
    
    return severity_weight + population_weight + casualty_weight + damage_weight