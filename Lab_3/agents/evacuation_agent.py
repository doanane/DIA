from spade.agent import Agent
from behaviours.response_behaviours import EvacuationResponseBehaviour
from utils.helpers import log_activity
import uuid

class EvacuationAgent(Agent):
    def __init__(self, jid, password, command_center_jid):
        super().__init__(jid, password)
        self.command_center_jid = command_center_jid
        self.unit_id = f"EVAC-{str(uuid.uuid4())[:4]}"
        self.status = "AVAILABLE"
        self.evacuated = 0
        self.missions_completed = 0
        
    async def setup(self):
        self.log(f"EVACUATION UNIT {self.unit_id} ONLINE - Mass rescue ready")
        response = EvacuationResponseBehaviour()
        self.add_behaviour(response)
        
    def log(self, message):
        log_activity(self.jid, message)