# Disaster Response & Relief Coordination System - Lab 4

## Problem Statement
Following disasters (floods, earthquakes, fires), emergency response must be coordinated rapidly under uncertainty, partial information, and limited resources. Centralized systems are often unavailable or overloaded.

## Solution
A decentralized multi-agent system where autonomous agents collaborate to:
- Detect disaster events
- Assess damage severity  
- Allocate rescue and response tasks
- Manage limited relief supplies

## Agent Architecture
| Agent | Responsibility |
|-------|---------------|
| SensorAgent | Detects disasters, reports conditions |
| RescueAgent | Performs rescue operations |
| LogisticsAgent | Manages supplies and relief items |
| CoordinatorAgent | Assigns tasks, sets priorities, coordinates |

## Credentials
- JID: doanane@xmpp.jp  
- Password: S@0570263170s

## Run Instructions
```bash
pip install spade
python main.py


## **`models/disaster_models.py`**
```python
import json
import random
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    FIRE = "fire"
    LANDSLIDE = "landslide"
    STORM = "storm"

class SeverityLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ResourceType(Enum):
    WATER = "water"
    FOOD = "food"
    MEDICINE = "medicine"
    BLANKETS = "blankets"
    TENTS = "tents"
    GENERATORS = "generators"

@dataclass
class DisasterEvent:
    """Represents a detected disaster"""
    id: str
    type: DisasterType
    severity: SeverityLevel
    location: Tuple[float, float]
    timestamp: str
    affected_population: int
    casualties: int
    damaged_buildings: int
    requires_rescue: bool
    requires_supplies: bool
    supply_priority: List[ResourceType]
    
    def to_json(self):
        return json.dumps({
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "location": self.location,
            "timestamp": self.timestamp,
            "affected_population": self.affected_population,
            "casualties": self.casualties,
            "damaged_buildings": self.damaged_buildings,
            "requires_rescue": self.requires_rescue,
            "requires_supplies": self.requires_supplies,
            "supply_priority": [r.value for r in self.supply_priority]
        })
    
    @classmethod
    def from_json(cls, data):
        dict_data = json.loads(data)
        return cls(
            id=dict_data["id"],
            type=DisasterType(dict_data["type"]),
            severity=SeverityLevel(dict_data["severity"]),
            location=tuple(dict_data["location"]),
            timestamp=dict_data["timestamp"],
            affected_population=dict_data["affected_population"],
            casualties=dict_data["casualties"],
            damaged_buildings=dict_data["damaged_buildings"],
            requires_rescue=dict_data["requires_rescue"],
            requires_supplies=dict_data["requires_supplies"],
            supply_priority=[ResourceType(r) for r in dict_data["supply_priority"]]
        )

@dataclass
class ReliefSupply:
    """Represents a relief item"""
    id: str
    type: ResourceType
    quantity: int
    unit: str
    location: Tuple[float, float]
    available: bool = True

@dataclass  
class RescueTask:
    """Task assigned to rescue agent"""
    id: str
    disaster_id: str
    location: Tuple[float, float]
    people_to_rescue: int
    severity: int
    status: str = "PENDING"  # PENDING, ACTIVE, COMPLETED
    assigned_to: Optional[str] = None

@dataclass
class SupplyTask:
    """Task assigned to logistics agent"""
    id: str
    disaster_id: str
    location: Tuple[float, float]
    required_supplies: Dict[str, int]
    status: str = "PENDING"
    assigned_to: Optional[str] = None

class DisasterSimulator:
    """Generates realistic disaster scenarios"""
    
    @staticmethod
    def generate():
        disaster_id = f"D{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10,99)}"
        
        disaster_types = list(DisasterType)
        disaster_type = random.choice(disaster_types)
        
        # Severity based on disaster type
        if disaster_type == DisasterType.EARTHQUAKE:
            severity = random.choices(
                list(SeverityLevel), 
                weights=[0.1, 0.2, 0.4, 0.3]
            )[0]
            affected = random.randint(500, 5000)
            casualties = int(affected * random.uniform(0.05, 0.2))
            damaged = int(affected * random.uniform(0.3, 0.7))
        elif disaster_type == DisasterType.FLOOD:
            severity = random.choices(
                list(SeverityLevel),
                weights=[0.2, 0.3, 0.3, 0.2]
            )[0]
            affected = random.randint(300, 3000)
            casualties = int(affected * random.uniform(0.02, 0.1))
            damaged = int(affected * random.uniform(0.2, 0.5))
        elif disaster_type == DisasterType.FIRE:
            severity = random.choices(
                list(SeverityLevel),
                weights=[0.3, 0.4, 0.2, 0.1]
            )[0]
            affected = random.randint(50, 500)
            casualties = int(affected * random.uniform(0.01, 0.15))
            damaged = int(affected * random.uniform(0.4, 0.8))
        else:
            severity = random.choice(list(SeverityLevel))
            affected = random.randint(100, 1000)
            casualties = int(affected * random.uniform(0.01, 0.1))
            damaged = int(affected * random.uniform(0.1, 0.4))
        
        # Determine resource needs
        requires_rescue = casualties > 20 or damaged > 50
        requires_supplies = affected > 100
        
        supply_priority = []
        if requires_supplies:
            if disaster_type == DisasterType.EARTHQUAKE:
                supply_priority = [ResourceType.TENTS, ResourceType.MEDICINE, ResourceType.WATER, ResourceType.FOOD]
            elif disaster_type == DisasterType.FLOOD:
                supply_priority = [ResourceType.WATER, ResourceType.FOOD, ResourceType.BLANKETS, ResourceType.MEDICINE]
            elif disaster_type == DisasterType.FIRE:
                supply_priority = [ResourceType.MEDICINE, ResourceType.WATER, ResourceType.BLANKETS, ResourceType.FOOD]
            else:
                supply_priority = [ResourceType.FOOD, ResourceType.WATER, ResourceType.MEDICINE, ResourceType.BLANKETS]
        
        return DisasterEvent(
            id=disaster_id,
            type=disaster_type,
            severity=severity,
            location=(round(random.uniform(-90, 90), 4), round(random.uniform(-180, 180), 4)),
            timestamp=datetime.now().strftime("%H:%M:%S"),
            affected_population=affected,
            casualties=casualties,
            damaged_buildings=damaged,
            requires_rescue=requires_rescue,
            requires_supplies=requires_supplies,
            supply_priority=supply_priority[:3]  # Top 3 priorities
        )