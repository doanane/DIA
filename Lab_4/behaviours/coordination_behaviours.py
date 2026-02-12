import asyncio
import json
import uuid
import random
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from models.disaster_models import DisasterEvent, RescueTask, SupplyTask
from utils.helpers import log_relief_operation, calculate_priority_score

class DisasterAssessmentBehaviour(CyclicBehaviour):
    """CoordinatorAgent: Assess damage severity and prioritize"""
    
    async def run(self):
        msg = await self.receive(timeout=1)
        
        if msg is None:
            return
            
        if msg.get_metadata("ontology") == "disaster_detection":
            try:
                disaster = DisasterEvent.from_json(msg.body)
                
                # Store disaster
                self.agent.active_disasters[disaster.id] = disaster
                
                # Calculate priority score
                priority = calculate_priority_score(disaster)
                self.agent.disaster_priorities[disaster.id] = priority
                
                log_relief_operation(
                    self.agent.jid,
                    "COORDINATOR",
                    f"ASSESSING: {disaster.id} | Type:{disaster.type.value} | Priority:{priority:.1f}"
                )
                
                # Create tasks based on needs
                tasks_created = 0
                
                # Create rescue task if needed
                if disaster.requires_rescue:
                    rescue_task = RescueTask(
                        id=f"RT-{uuid.uuid4().hex[:6]}",
                        disaster_id=disaster.id,
                        location=disaster.location,
                        people_to_rescue=disaster.casualties + int(disaster.affected_population * 0.1),
                        severity=disaster.severity.value,
                        status="PENDING"
                    )
                    self.agent.pending_rescue_tasks[rescue_task.id] = rescue_task
                    tasks_created += 1
                    
                    log_relief_operation(
                        self.agent.jid,
                        "COORDINATOR",
                        f"TASK CREATED: Rescue {rescue_task.people_to_rescue} people at {disaster.location}"
                    )
                
                # Create supply task if needed
                if disaster.requires_supplies:
                    supply_needs = {}
                    for resource in disaster.supply_priority[:3]:
                        quantity = int(disaster.affected_population * random.uniform(0.5, 2.0))
                        supply_needs[resource.value] = quantity
                    
                    supply_task = SupplyTask(
                        id=f"ST-{uuid.uuid4().hex[:6]}",
                        disaster_id=disaster.id,
                        location=disaster.location,
                        required_supplies=supply_needs,
                        status="PENDING"
                    )
                    self.agent.pending_supply_tasks[supply_task.id] = supply_task
                    tasks_created += 1
                    
                    log_relief_operation(
                        self.agent.jid,
                        "COORDINATOR",
                        f"TASK CREATED: Deliver supplies - {supply_needs}"
                    )
                
                # Log assessment summary
                log_relief_operation(
                    self.agent.jid,
                    "COORDINATOR",
                    f"ASSESSMENT COMPLETE: {disaster.id} | Tasks created: {tasks_created} | Priority queue position: {len(self.agent.disaster_priorities)}"
                )
            except Exception as e:
                log_relief_operation(
                    self.agent.jid,
                    "COORDINATOR",
                    f"ERROR processing disaster: {str(e)}"
                )

class TaskAssignmentBehaviour(CyclicBehaviour):
    """CoordinatorAgent: Assigns tasks to available agents"""
    
    async def run(self):
        # Check for available rescue agents
        for agent_jid in self.agent.available_rescue_agents:
            if self.agent.pending_rescue_tasks:
                # Get highest priority task
                task_id = next(iter(self.agent.pending_rescue_tasks))
                task = self.agent.pending_rescue_tasks.pop(task_id)
                
                # Assign task
                task.status = "ACTIVE"
                task.assigned_to = agent_jid
                self.agent.active_rescue_tasks[task.id] = task
                
                # Remove from available pool
                self.agent.available_rescue_agents.remove(agent_jid)
                
                # Send assignment
                msg = Message(to=agent_jid)
                msg.set_metadata("performative", "request")
                msg.set_metadata("ontology", "rescue_assignment")
                msg.body = json.dumps({
                    "task_id": task.id,
                    "disaster_id": task.disaster_id,
                    "location": task.location,
                    "people_to_rescue": task.people_to_rescue,
                    "severity": task.severity
                })
                await self.send(msg)
                
                log_relief_operation(
                    self.agent.jid,
                    "COORDINATOR",
                    f"ASSIGNED: Rescue task {task.id} to {agent_jid} - {task.people_to_rescue} people"
                )
                break
        
        # Check for available logistics agents
        for agent_jid in self.agent.available_logistics_agents:
            if self.agent.pending_supply_tasks:
                task_id = next(iter(self.agent.pending_supply_tasks))
                task = self.agent.pending_supply_tasks.pop(task_id)
                
                task.status = "ACTIVE"
                task.assigned_to = agent_jid
                self.agent.active_supply_tasks[task.id] = task
                
                self.agent.available_logistics_agents.remove(agent_jid)
                
                msg = Message(to=agent_jid)
                msg.set_metadata("performative", "request")
                msg.set_metadata("ontology", "supply_assignment")
                msg.body = json.dumps({
                    "task_id": task.id,
                    "disaster_id": task.disaster_id,
                    "location": task.location,
                    "required_supplies": task.required_supplies
                })
                await self.send(msg)
                
                log_relief_operation(
                    self.agent.jid,
                    "COORDINATOR",
                    f"ASSIGNED: Supply task {task.id} to {agent_jid} - {task.required_supplies}"
                )
                break

class TaskCompletionBehaviour(CyclicBehaviour):
    """CoordinatorAgent: Process completed tasks"""
    
    async def run(self):
        msg = await self.receive(timeout=1)
        
        if msg is None:
            return
            
        if msg.get_metadata("ontology") == "task_complete":
            try:
                report = json.loads(msg.body)
                task_id = report["task_id"]
                agent_jid = str(msg.sender)
                
                if report["task_type"] == "rescue":
                    if task_id in self.agent.active_rescue_tasks:
                        task = self.agent.active_rescue_tasks.pop(task_id)
                        self.agent.completed_rescue_tasks[task_id] = task
                        self.agent.people_rescued += report.get("people_rescued", 0)
                        self.agent.available_rescue_agents.append(agent_jid)
                        
                        log_relief_operation(
                            self.agent.jid,
                            "COORDINATOR",
                            f"RESCUE COMPLETE: {task_id} | Rescued: {report.get('people_rescued',0)} | Total rescued: {self.agent.people_rescued}"
                        )
                
                elif report["task_type"] == "supply":
                    if task_id in self.agent.active_supply_tasks:
                        task = self.agent.active_supply_tasks.pop(task_id)
                        self.agent.completed_supply_tasks[task_id] = task
                        self.agent.available_logistics_agents.append(agent_jid)
                        
                        log_relief_operation(
                            self.agent.jid,
                            "COORDINATOR",
                            f"SUPPLY COMPLETE: {task_id} | Supplies delivered"
                        )
                
                # Check if disaster response is complete
                disaster_id = report.get("disaster_id")
                if disaster_id in self.agent.active_disasters:
                    disaster = self.agent.active_disasters[disaster_id]
                    related_tasks = []
                    
                    for task in self.agent.completed_rescue_tasks.values():
                        if task.disaster_id == disaster_id:
                            related_tasks.append(task)
                    
                    for task in self.agent.completed_supply_tasks.values():
                        if task.disaster_id == disaster_id:
                            related_tasks.append(task)
                    
                    # If all tasks completed, close disaster
                    expected_tasks = 0
                    if disaster.requires_rescue:
                        expected_tasks += 1
                    if disaster.requires_supplies:
                        expected_tasks += 1
                    
                    if len(related_tasks) >= expected_tasks:
                        log_relief_operation(
                            self.agent.jid,
                            "COORDINATOR",
                            f"DISASTER RESPONSE COMPLETE: {disaster_id} | Total rescued: {self.agent.people_rescued}"
                        )
                        del self.agent.active_disasters[disaster_id]
            except Exception as e:
                log_relief_operation(
                    self.agent.jid,
                    "COORDINATOR",
                    f"ERROR processing task completion: {str(e)}"
                )

class StatusBroadcastBehaviour(PeriodicBehaviour):
    """CoordinatorAgent: Broadcast system status"""
    
    async def run(self):
        log_relief_operation(
            self.agent.jid,
            "COORDINATOR",
            f"STATUS: Disasters:{len(self.agent.active_disasters)} | Rescue Tasks:{len(self.agent.active_rescue_tasks)} | Supply Tasks:{len(self.agent.active_supply_tasks)} | Rescued:{self.agent.people_rescued} | Available Rescue:{len(self.agent.available_rescue_agents)} | Available Logistics:{len(self.agent.available_logistics_agents)}"
        )