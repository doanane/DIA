import asyncio
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.message import Message
from models.disaster_models import DisasterSimulator

class DisasterDetectionBehaviour(PeriodicBehaviour):
    async def run(self):
        disaster = DisasterSimulator.generate()
        
        msg = Message(to=self.agent.command_center_jid)
        msg.set_metadata("performative", "inform")
        msg.set_metadata("ontology", "disaster_detection")
        msg.body = disaster.to_json()
        
        await self.send(msg)
        self.agent.log(f"DETECTED: {disaster.type.value} - {disaster.severity.name} - {disaster.affected_people} people")

class SensorAnalysisBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=1)
        if msg:
            self.agent.log(f"Received sensor data: {msg.body}")