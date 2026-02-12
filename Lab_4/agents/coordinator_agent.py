from spade.agent import Agent
from spade.template import Template
from behaviours.coordination_behaviours import (
    DisasterAssessmentBehaviour,
    TaskAssignmentBehaviour,
    TaskCompletionBehaviour,
    StatusBroadcastBehaviour
)
from utils.helpers import log_relief_operation

class CoordinatorAgent(Agent):
    """Assigns tasks, sets priorities, and coordinates agents"""
    
    def __init__(self, jid, password):
        super().__init__(jid, password)
        
        # Disaster management
        self.active_disasters = {}
        self.disaster_priorities = {}
        
        # Task management
        self.pending_rescue_tasks = {}
        self.active_rescue_tasks = {}
        self.completed_rescue_tasks = {}
        
        self.pending_supply_tasks = {}
        self.active_supply_tasks = {}
        self.completed_supply_tasks = {}
        
        # Resource management
        self.available_rescue_agents = []
        self.available_logistics_agents = []
        
        # Statistics
        self.people_rescued = 0
        self.supplies_delivered = 0
        
    async def setup(self):
        log_relief_operation(
            self.jid,
            "COORDINATOR",
            "INITIALIZED | Disaster coordination center activated"
        )
        
        # Assess incoming disasters
        assessment = DisasterAssessmentBehaviour()
        self.add_behaviour(assessment)
        
        # Assign tasks to available agents
        assignment = TaskAssignmentBehaviour()
        self.add_behaviour(assignment)
        
        # Process completed tasks
        completion = TaskCompletionBehaviour()
        self.add_behaviour(completion)
        
        # Broadcast status every 15 seconds
        status = StatusBroadcastBehaviour(period=15)
        self.add_behaviour(status)
        
        # Accept all presence subscriptions
        if self.presence:
            self.presence.approve_all = True
        
    async def register_rescue_agent(self, agent_jid):
        """Register a rescue agent as available"""
        if agent_jid not in self.available_rescue_agents:
            self.available_rescue_agents.append(agent_jid)
            log_relief_operation(
                self.jid,
                "COORDINATOR",
                f"RESCUE AGENT REGISTERED: {agent_jid} | Available: {len(self.available_rescue_agents)}"
            )
    
    async def register_logistics_agent(self, agent_jid):
        """Register a logistics agent as available"""
        if agent_jid not in self.available_logistics_agents:
            self.available_logistics_agents.append(agent_jid)
            log_relief_operation(
                self.jid,
                "COORDINATOR",
                f"LOGISTICS AGENT REGISTERED: {agent_jid} | Available: {len(self.available_logistics_agents)}"
            )