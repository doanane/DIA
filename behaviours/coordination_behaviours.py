import asyncio
import json
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from models.disaster_models import DisasterEvent

class DisasterAssessmentBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=0.5)
        if msg and msg.get_metadata("ontology") == "disaster_detection":
            disaster = DisasterEvent.from_json(msg.body)
            
            if disaster.id not in self.agent.active_disasters:
                self.agent.active_disasters[disaster.id] = disaster
                
                priority = disaster.severity.value * (disaster.affected_people / 100)
                self.agent.log(f"ASSESSING: {disaster.id} - Priority: {priority:.1f}")
                
                order = {
                    "disaster_id": disaster.id,
                    "location": disaster.location,
                    "severity": disaster.severity.value,
                    "type": disaster.type.value,
                    "fire_required": disaster.requires_firefighting,
                    "medical_required": disaster.requires_medical,
                    "evacuation_required": disaster.requires_evacuation
                }
                
                broadcast = Message(to=str(msg.sender))
                broadcast.set_metadata("ontology", "deployment_order")
                broadcast.body = json.dumps(order)
                await self.send(broadcast)
                
                self.agent.log(f"DISPATCHED: Fire:{disaster.requires_firefighting} Medical:{disaster.requires_medical} Evac:{disaster.requires_evacuation}")
        
        elif msg and msg.get_metadata("ontology") == "mission_report":
            report = json.loads(msg.body)
            disaster_id = report["disaster_id"]
            
            if report["unit"] == "fire":
                self.agent.fires_extinguished += 1
                self.agent.log(f"FIRE CONTAINED - Total: {self.agent.fires_extinguished}")
            elif report["unit"] == "ambulance":
                self.agent.people_saved += report.get("patients", 0)
                self.agent.log(f"PATIENTS TREATED: {report.get('patients',0)} - Total saved: {self.agent.people_saved}")
            elif report["unit"] == "evacuation":
                self.agent.people_saved += report.get("evacuated", 0)
                self.agent.log(f"PEOPLE EVACUATED: {report.get('evacuated',0)} - Total saved: {self.agent.people_saved}")
            
            if disaster_id in self.agent.active_disasters:
                del self.agent.active_disasters[disaster_id]

class StatusBroadcastBehaviour(PeriodicBehaviour):
    async def run(self):
        self.agent.log(f"STATUS: {len(self.agent.active_disasters)} active | FIRE: {self.agent.fire_available} | AMB: {self.agent.ambulance_available} | EVAC: {self.agent.evacuation_available} | SAVED: {self.agent.people_saved}")