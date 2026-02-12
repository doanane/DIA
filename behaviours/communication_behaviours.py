import json
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class StatusBroadcastBehaviour(CyclicBehaviour):
    async def run(self):
        await asyncio.sleep(10)
        
        status_report = {
            "agent_id": str(self.agent.jid),
            "agent_type": self.agent.agent_type,
            "active_disasters": len(getattr(self.agent, "active_disasters", {})),
            "resources_available": len(getattr(self.agent, "available_resources", {})),
            "timestamp": self.agent.get_current_timestamp()
        }
        
        for recipient in getattr(self.agent, "coordinators", []):
            msg = Message(to=recipient)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "status_update")
            msg.body = json.dumps(status_report)
            await self.send(msg)

class EmergencyBroadcastBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=1)
        if msg:
            if msg.get_metadata("ontology") == "emergency_broadcast":
                emergency_data = json.loads(msg.body)
                
                if emergency_data.get("severity", 0) >= 3:
                    for agent in self.agent.all_agents:
                        broadcast = Message(to=agent)
                        broadcast.set_metadata("performative", "inform")
                        broadcast.set_metadata("ontology", "emergency_alert")
                        broadcast.body = msg.body
                        await self.send(broadcast)
                    
                    self.agent.log_activity(f"EMERGENCY BROADCAST: {emergency_data['disaster_id']}")