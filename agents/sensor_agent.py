from spade.agent import Agent
from behaviours.detection_behaviours import DisasterDetectionBehaviour, SensorAnalysisBehaviour
from utils.helpers import log_activity, get_timestamp

class SensorAgent(Agent):
    def __init__(self, jid, password, command_center_jid):
        super().__init__(jid, password)
        self.command_center_jid = command_center_jid
        
    async def setup(self):
        self.log(f"SENSOR AGENT ONLINE - Monitoring environmental sensors")
        detection = DisasterDetectionBehaviour(period=15)
        self.add_behaviour(detection)
        
    def log(self, message):
        log_activity(self.jid, message)