import asyncio
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.message import Message
from models.disaster_models import DisasterSimulator
from utils.helpers import log_relief_operation

class DisasterDetectionBehaviour(PeriodicBehaviour):
    """SensorAgent: Detects disaster events and reports conditions"""
    
    async def run(self):
        # Generate simulated disaster
        disaster = DisasterSimulator.generate()
        
        # Store in agent's memory
        self.agent.detected_disasters[disaster.id] = disaster
        
        # Report to coordinator
        msg = Message(to=self.agent.coordinator_jid)
        msg.set_metadata("performative", "inform")
        msg.set_metadata("ontology", "disaster_detection")
        msg.set_metadata("language", "json")
        msg.body = disaster.to_json()
        
        await self.send(msg)
        
        # Log detection
        log_relief_operation(
            self.agent.jid,
            "SENSOR",
            f"DETECTED: {disaster.type.value.upper()} | Sev:{disaster.severity.name} | Pop:{disaster.affected_population} | Casualties:{disaster.casualties}"
        )

class EnvironmentalMonitoringBehaviour(CyclicBehaviour):
    """SensorAgent: Continuously monitor environmental conditions"""
    
    async def run(self):
        msg = await self.receive(timeout=2)
        if msg:
            log_relief_operation(
                self.agent.jid,
                "SENSOR",
                f"Received sensor query: {msg.body}"
            )