from spade.agent import Agent
from behaviours.rescue_behaviours import RescueOperationBehaviour, RescueStatusBehaviour
from utils.helpers import log_relief_operation
import uuid

class RescueAgent(Agent):
    """Performs rescue operations"""
    
    def __init__(self, jid, password, coordinator_jid):
        super().__init__(jid, password)
        self.coordinator_jid = coordinator_jid
        self.unit_id = f"RU-{uuid.uuid4().hex[:4]}"
        self.status = "AVAILABLE"
        self.people_rescued = 0
        self.missions_completed = 0
        self.current_task = None
        
    async def setup(self):
        log_relief_operation(
            self.jid,
            f"RESCUE-{self.unit_id}",
            f"INITIALIZED | Status: {self.status} | Ready for deployment"
        )
        
        # Rescue operations
        rescue = RescueOperationBehaviour()
        self.add_behaviour(rescue)
        
        # Status reporting
        status = RescueStatusBehaviour()
        self.add_behaviour(status)
        
        # Register with coordinator
        if self.presence:
            self.presence.approve_all = True