import json
import asyncio
import uuid
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

class ResponseAgent(Agent):
    def __init__(self, jid, password, command_center_jid, resource_type, capacity, simulation_mode=True):
        super().__init__(jid, password)
        self.command_center_jid = command_center_jid
        self.resource_type = resource_type
        self.capacity = capacity
        self.simulation_mode = simulation_mode
        self.current_mission = None
        self.status = "AVAILABLE"
        self.agent_type = "RESPONDER"
        self.responder_id = str(uuid.uuid4())[:8]
        
    async def setup(self):
        self.log_activity(f"RESPONSE AGENT INITIALIZED - Type: {self.resource_type}, Capacity: {self.capacity}")
        
        deployment_behaviour = self.DeploymentBehaviour()
        deployment_template = Template()
        deployment_template.set_metadata("ontology", "resource_deployment")
        self.add_behaviour(deployment_behaviour, deployment_template)
        
        status_report_behaviour = self.StatusReportBehaviour()
        self.add_behaviour(status_report_behaviour)
    
    class DeploymentBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=2)
            if msg:
                deployment_order = json.loads(msg.body)
                disaster_id = deployment_order["disaster_id"]
                
                self.agent.current_mission = {
                    "disaster_id": disaster_id,
                    "location": deployment_order["location"],
                    "action_plan": deployment_order["action_plan"],
                    "status": "DEPLOYING"
                }
                self.agent.status = "DEPLOYED"
                
                self.agent.log_activity(f"DEPLOYING TO: {disaster_id} - Location: {deployment_order['location']}")
                
                await asyncio.sleep(3)
                
                completion_msg = Message(to=self.agent.command_center_jid)
                completion_msg.set_metadata("performative", "inform")
                completion_msg.set_metadata("ontology", "mission_complete")
                completion_msg.body = json.dumps({
                    "disaster_id": disaster_id,
                    "responder_id": self.agent.responder_id,
                    "resource_type": self.agent.resource_type,
                    "casualties_treated": self.agent.capacity if self.agent.resource_type == "ambulance" else 0,
                    "fires_extinguished": 1 if self.agent.resource_type == "fire_truck" else 0,
                    "people_evacuated": self.agent.capacity if self.agent.resource_type == "evacuation_team" else 0
                })
                await self.send(completion_msg)
                
                self.agent.status = "AVAILABLE"
                self.agent.current_mission = None
                self.agent.log_activity(f"MISSION COMPLETE: {disaster_id}")
    
    class StatusReportBehaviour(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(5)
            
            status_msg = Message(to=self.agent.command_center_jid)
            status_msg.set_metadata("performative", "inform")
            status_msg.set_metadata("ontology", "responder_status")
            status_msg.body = json.dumps({
                "responder_id": self.agent.responder_id,
                "resource_type": self.agent.resource_type,
                "status": self.agent.status,
                "current_mission": self.agent.current_mission
            })
            await self.send(status_msg)
    
    def log_activity(self, message):
        with open("disaster_response_log.txt", "a") as f:
            f.write(f"[{self.get_current_timestamp()}] [{self.jid}] {message}\n")
        print(f"[{self.jid}] {message}")
    
    def get_current_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")