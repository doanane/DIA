import json
import random
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Optional


class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FIRE = "fire"
    FLOOD = "flood"
    CHEMICAL_SPILL = "chemical_spill"
    BUILDING_COLLAPSE = "building_collapse"


class SeverityLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ResourceType(Enum):
    FOOD = "food"
    WATER = "water"
    MEDICAL_SUPPLIES = "medical_supplies"
    BLANKETS = "blankets"
    TEMPORARY_SHELTER = "temporary_shelter"
    FUEL = "fuel"


@dataclass
class DisasterEvent:
    id: str
    type: DisasterType
    severity: SeverityLevel
    location: Tuple[float, float]
    timestamp: str
    affected_population: int
    casualties: int
    damaged_buildings: int
    requires_evacuation: bool
    requires_medical: bool
    requires_firefighting: bool
    requires_rescue: bool
    requires_supplies: bool
    supply_priority: List[ResourceType] = field(default_factory=list)
    
    def __post_init__(self):
        # Set default supply priority based on disaster type
        if not self.supply_priority:
            if self.type == DisasterType.EARTHQUAKE or self.type == DisasterType.BUILDING_COLLAPSE:
                self.supply_priority = [ResourceType.WATER, ResourceType.FOOD, ResourceType.MEDICAL_SUPPLIES, ResourceType.BLANKETS]
            elif self.type == DisasterType.FLOOD:
                self.supply_priority = [ResourceType.WATER, ResourceType.FOOD, ResourceType.BLANKETS, ResourceType.TEMPORARY_SHELTER]
            elif self.type == DisasterType.FIRE:
                self.supply_priority = [ResourceType.WATER, ResourceType.MEDICAL_SUPPLIES, ResourceType.BLANKETS, ResourceType.FUEL]
            elif self.type == DisasterType.CHEMICAL_SPILL:
                self.supply_priority = [ResourceType.MEDICAL_SUPPLIES, ResourceType.WATER, ResourceType.FOOD, ResourceType.BLANKETS]
            else:
                self.supply_priority = [ResourceType.WATER, ResourceType.FOOD, ResourceType.MEDICAL_SUPPLIES, ResourceType.BLANKETS]
    
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
            "requires_evacuation": self.requires_evacuation,
            "requires_medical": self.requires_medical,
            "requires_firefighting": self.requires_firefighting,
            "requires_rescue": self.requires_rescue,
            "requires_supplies": self.requires_supplies,
            "supply_priority": [r.value for r in self.supply_priority]
        })
    
    @classmethod
    def from_json(cls, data):
        dict_data = json.loads(data)
        supply_priority = [ResourceType(r) for r in dict_data.get("supply_priority", [])]
        return cls(
            id=dict_data["id"],
            type=DisasterType(dict_data["type"]),
            severity=SeverityLevel(dict_data["severity"]),
            location=tuple(dict_data["location"]),
            timestamp=dict_data["timestamp"],
            affected_population=dict_data["affected_population"],
            casualties=dict_data["casualties"],
            damaged_buildings=dict_data["damaged_buildings"],
            requires_evacuation=dict_data["requires_evacuation"],
            requires_medical=dict_data["requires_medical"],
            requires_firefighting=dict_data["requires_firefighting"],
            requires_rescue=dict_data.get("requires_rescue", False),
            requires_supplies=dict_data.get("requires_supplies", False),
            supply_priority=supply_priority
        )


@dataclass
class ReliefSupply:
    """Represents a relief supply item"""
    id: str
    type: ResourceType
    quantity: int
    location: Tuple[float, float]
    timestamp: str


@dataclass
class RescueTask:
    """Represents a rescue operation task"""
    id: str
    disaster_id: str
    location: Tuple[float, float]
    people_to_rescue: int
    severity: int
    status: str = "PENDING"  # PENDING, ACTIVE, COMPLETED
    assigned_to: Optional[str] = None
    task_id: str = field(default="")
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = self.id


@dataclass
class SupplyTask:
    """Represents a supply delivery task"""
    id: str
    disaster_id: str
    location: Tuple[float, float]
    required_supplies: Dict[str, int]
    status: str = "PENDING"  # PENDING, ACTIVE, COMPLETED
    assigned_to: Optional[str] = None
    task_id: str = field(default="")
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = self.id


class DisasterSimulator:
    """Generates simulated disaster events"""
    
    @staticmethod
    def generate():
        disaster_id = f"D{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
        disaster_type = random.choice(list(DisasterType))
        severity = random.choice(list(SeverityLevel))
        
        affected_population = random.randint(100, 5000)
        casualty_ratio = 0.1 if severity.value <= 2 else 0.2 if severity.value == 3 else 0.35
        casualties = int(affected_population * casualty_ratio)
        damaged_buildings = int(affected_population / random.uniform(3, 8))
        
        requires_rescue = severity.value >= 2 or casualties > 50
        requires_supplies = severity.value >= 1
        
        return DisasterEvent(
            id=disaster_id,
            type=disaster_type,
            severity=severity,
            location=(round(random.uniform(-90, 90), 4), round(random.uniform(-180, 180), 4)),
            timestamp=datetime.now().isoformat(),
            affected_population=affected_population,
            casualties=casualties,
            damaged_buildings=damaged_buildings,
            requires_evacuation=severity.value >= 3,
            requires_medical=casualties > 0,
            requires_firefighting=disaster_type == DisasterType.FIRE,
            requires_rescue=requires_rescue,
            requires_supplies=requires_supplies
        )
