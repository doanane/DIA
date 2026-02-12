from spade.agent import Agent
from behaviours.coordination_behaviours import DisasterAssessmentBehaviour, StatusBroadcastBehaviour
from utils.helpers import log_activity

class CommandCenterAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.active_disasters = {}
        self.fire_available = 3
        self.ambulance_available = 3
        self.evacuation_available = 2
        self.fires_extinguished = 0
        self.people_saved = 0
        
    async def setup(self):
        self.log(f"COMMAND CENTER ONLINE - Disaster coordination active")
        assessment = DisasterAssessmentBehaviour()
        self.add_behaviour(assessment)
        status = StatusBroadcastBehaviour(period=10)
        self.add_behaviour(status)
        
    def log(self, message):
        log_activity(self.jid, message)