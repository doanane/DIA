from spade.agent import Agent
from behaviours.detection_behaviours import DisasterDetectionBehaviour, EnvironmentalMonitoringBehaviour
from utils.helpers import log_relief_operation

class SensorAgent(Agent):
    """Detects disaster events and reports environmental conditions"""
    
    def __init__(self, jid, password, coordinator_jid):
        super().__init__(jid, password)
        self.coordinator_jid = coordinator_jid
        self.detected_disasters = {}
        self.sensor_id = str(jid).split("@")[0]  # Extract local part before @
        
    async def setup(self):
        log_relief_operation(
            self.jid,
            "SENSOR",
            f"INITIALIZED | ID: {self.sensor_id} | Monitoring active"
        )
        
        # Detect disasters every 12 seconds
        detection = DisasterDetectionBehaviour(period=12)
        self.add_behaviour(detection)
        
        # Monitor environmental queries
        monitoring = EnvironmentalMonitoringBehaviour()
        self.add_behaviour(monitoring)