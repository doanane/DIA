from spade.agent import Agent
from behaviours.logistics_behaviours import SupplyDeliveryBehaviour, InventoryManagementBehaviour
from utils.helpers import log_relief_operation
from models.disaster_models import ResourceType
import uuid
import random

class LogisticsAgent(Agent):
    """Manages supplies and relief items"""
    
    def __init__(self, jid, password, coordinator_jid):
        super().__init__(jid, password)
        self.coordinator_jid = coordinator_jid
        self.unit_id = f"LU-{uuid.uuid4().hex[:4]}"
        self.status = "AVAILABLE"
        self.inventory = self.initialize_inventory()
        self.supplies_delivered = 0
        self.missions_completed = 0
        self.current_task = None
        
    def initialize_inventory(self):
        """Initialize warehouse inventory"""
        inventory = {}
        for resource in ResourceType:
            inventory[resource.value] = random.randint(200, 500)
        return inventory
        
    async def setup(self):
        log_relief_operation(
            self.jid,
            f"LOGISTICS-{self.unit_id}",
            f"INITIALIZED | Inventory: {self.inventory} | Ready for deployment"
        )
        
        # Supply delivery
        delivery = SupplyDeliveryBehaviour()
        self.add_behaviour(delivery)
        
        # Inventory management
        inventory = InventoryManagementBehaviour()
        self.add_behaviour(inventory)
        
        # Register with coordinator
        if self.presence:
            self.presence.approve_all = True