import asyncio
import json
import random
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from models.disaster_models import ResourceType
from utils.helpers import log_relief_operation

class SupplyDeliveryBehaviour(CyclicBehaviour):
    """LogisticsAgent: Manages supplies and relief items"""
    
    async def run(self):
        msg = await self.receive(timeout=0.5)
        
        if msg and msg.get_metadata("ontology") == "supply_assignment":
            task = json.loads(msg.body)
            
            self.agent.status = "DEPLOYED"
            self.agent.current_task = task
            
            log_relief_operation(
                self.agent.jid,
                f"LOGISTICS-{self.agent.unit_id}",
                f"DEPLOYED to {task['disaster_id']} | Supplies: {task['required_supplies']}"
            )
            
            # Check available inventory
            delivered_supplies = {}
            for supply_type, required_qty in task['required_supplies'].items():
                if supply_type in self.agent.inventory:
                    available = self.agent.inventory[supply_type]
                    deliver_qty = min(required_qty, available)
                    self.agent.inventory[supply_type] -= deliver_qty
                    delivered_supplies[supply_type] = deliver_qty
                else:
                    delivered_supplies[supply_type] = 0
            
            # Simulate transport time
            transport_time = 2 + (len(task['required_supplies']) * 0.5)
            await asyncio.sleep(transport_time)
            
            self.agent.supplies_delivered += sum(delivered_supplies.values())
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
                "task_type": "supply",
                "agent_id": str(self.agent.jid),
                "unit_id": self.agent.unit_id,
                "supplies_delivered": delivered_supplies,
                "inventory_remaining": self.agent.inventory
            })
            await self.send(report)
            
            log_relief_operation(
                self.agent.jid,
                f"LOGISTICS-{self.agent.unit_id}",
                f"DELIVERY COMPLETE | Delivered: {delivered_supplies} | Inventory: {self.agent.inventory}"
            )

class InventoryManagementBehaviour(CyclicBehaviour):
    """LogisticsAgent: Manage and replenish inventory"""
    
    async def run(self):
        await asyncio.sleep(15)
        
        # Auto-replenish low inventory
        for resource in ResourceType:
            resource_value = resource.value
            if resource_value in self.agent.inventory:
                if self.agent.inventory[resource_value] < 100:
                    replenish = random.randint(50, 200)
                    self.agent.inventory[resource_value] += replenish
                    log_relief_operation(
                        self.agent.jid,
                        f"LOGISTICS-{self.agent.unit_id}",
                        f"INVENTORY REPLENISHED: {resource_value} +{replenish} | New stock: {self.agent.inventory[resource_value]}"
                    )
        
        # Report inventory status
        log_relief_operation(
            self.agent.jid,
            f"LOGISTICS-{self.agent.unit_id}",
            f"INVENTORY STATUS: {self.agent.inventory}"
        )