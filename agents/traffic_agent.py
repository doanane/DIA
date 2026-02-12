from spade.agent import Agent
from behaviours.response_behaviours import TrafficControlBehaviour, TrafficStatusBehaviour
from utils.helpers import log_activity

class TrafficAgent(Agent):
    def __init__(self, jid, password, zone):
        super().__init__(jid, password)
        self.zone = zone
        self.status = "NORMAL"
        self.routes_cleared = 0
        
    async def setup(self):
        self.log(f"TRAFFIC CONTROL {self.zone} ONLINE - Intelligent routing active")
        control = TrafficControlBehaviour()
        self.add_behaviour(control)
        status = TrafficStatusBehaviour(period=20)
        self.add_behaviour(status)
        
    def log(self, message):
        log_activity(self.jid, message)