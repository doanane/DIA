import asyncio
import json
import random
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from utils.helpers import log_relief_operation

class RescueOperationBehaviour(CyclicBehaviour):
    """RescueAgent: Performs rescue operations"""
    
    async def run(self):
        msg = await self.receive(timeout=0.5)
        
        if msg and msg.get_metadata("ontology") == "rescue_assignment":
            task = json.loads(msg.body)
            
            self.agent.status = "DEPLOYED"
            self.agent.current_task = task
            
            log_relief_operation(
                self.agent.jid,
                f"RESCUE-{self.agent.unit_id}",
                f"DEPLOYED to {task['disaster_id']} | Location: {task['location']} | People to rescue: {task['people_to_rescue']}"
            )
            
            # Simulate rescue operation time based on severity and people count
            operation_time = 2 + (task['severity'] * 0.5) + (task['people_to_rescue'] / 50)
            await asyncio.sleep(min(operation_time, 5))
            
            # Calculate rescue success rate (higher severity = more difficult)
            success_rate = 0.9 - (task['severity'] * 0.1)
            people_rescued = int(task['people_to_rescue'] * random.uniform(success_rate - 0.1, success_rate))
            
            self.agent.people_rescued += people_rescued
            self.agent.missions_completed += 1
            self.agent.status = "AVAILABLE"
            self.agent.current_task = None
            
            # Report completion
            report = Message(to=self.agent.coordinator_jid)
            report.set_metadata("performative", "inform")
            report.set_metadata("ontology", "task_complete")
            report.body = json.dumps({
                "task_id": task['task_id'],
                "disaster_id": task['disaster_id'],
                "task_type": "rescue",
                "agent_id": str(self.agent.jid),
                "unit_id": self.agent.unit_id,
                "people_rescued": people_rescued,
                "total_rescued": self.agent.people_rescued
            })
            await self.send(report)
            
            log_relief_operation(
                self.agent.jid,
                f"RESCUE-{self.agent.unit_id}",
                f"MISSION COMPLETE | Rescued: {people_rescued} | Total: {self.agent.people_rescued} | Missions: {self.agent.missions_completed}"
            )

class RescueStatusBehaviour(CyclicBehaviour):
    """RescueAgent: Report status to coordinator"""
    
    async def run(self):
        await asyncio.sleep(10)
        
        status_msg = Message(to=self.agent.coordinator_jid)
        status_msg.set_metadata("performative", "inform")
        status_msg.set_metadata("ontology", "agent_status")
        status_msg.body = json.dumps({
            "agent_type": "rescue",
            "agent_jid": str(self.agent.jid),
            "unit_id": self.agent.unit_id,
            "status": self.agent.status,
            "people_rescued": self.agent.people_rescued,
            "missions_completed": self.agent.missions_completed
        })
        await self.send(status_msg)