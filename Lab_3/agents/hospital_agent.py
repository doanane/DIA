from spade.agent import Agent
from behaviours.response_behaviours import HospitalTreatmentBehaviour, HospitalStatusBehaviour
from utils.helpers import log_activity

class HospitalAgent(Agent):
    def __init__(self, jid, password, capacity=150):
        super().__init__(jid, password)
        self.capacity = capacity
        self.available_beds = capacity
        self.admitted_patients = 0
        
    async def setup(self):
        self.log(f"HOSPITAL ONLINE - Level 1 Trauma Center - {self.available_beds} beds available")
        treatment = HospitalTreatmentBehaviour()
        self.add_behaviour(treatment)
        status = HospitalStatusBehaviour(period=15)
        self.add_behaviour(status)
        
    def log(self, message):
        log_activity(self.jid, message)