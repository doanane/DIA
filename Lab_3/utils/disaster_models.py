import enum
import random
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

class DisasterType(enum.Enum):
    EARTHQUAKE = "earthquake"
    FIRE = "fire"
    FLOOD = "flood"
    CHEMICAL_SPILL = "chemical_spill"
    BUILDING_COLLAPSE = "building_collapse"

class SeverityLevel(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class DisasterEvent:
    id: str
    type: DisasterType
    severity: SeverityLevel
    location: tuple
    timestamp: str
    affected_people: int
    requires_evacuation: bool
    requires_medical: bool
    requires_firefighting: bool
    
    def to_json(self):
        return json.dumps({
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "location": self.location,
            "timestamp": self.timestamp,
            "affected_people": self.affected_people,
            "requires_evacuation": self.requires_evacuation,
            "requires_medical": self.requires_medical,
            "requires_firefighting": self.requires_firefighting
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
            affected_people=dict_data["affected_people"],
            requires_evacuation=dict_data["requires_evacuation"],
            requires_medical=dict_data["requires_medical"],
            requires_firefighting=dict_data["requires_firefighting"]
        )

@dataclass
class Resource:
    id: str
    type: str
    capacity: int
    current_load: int
    location: tuple
    available: bool
    
    def available_capacity(self):
        return self.capacity - self.current_load

class DisasterSimulator:
    @staticmethod
    def generate_disaster():
        disaster_types = list(DisasterType)
        severities = list(SeverityLevel)
        
        disaster_id = f"D{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"
        
        return DisasterEvent(
            id=disaster_id,
            type=random.choice(disaster_types),
            severity=random.choice(severities),
            location=(random.uniform(-90, 90), random.uniform(-180, 180)),
            timestamp=datetime.now().isoformat(),
            affected_people=random.randint(10, 1000),
            requires_evacuation=random.choice([True, False]),
            requires_medical=random.choice([True, False]),
            requires_firefighting=random.choice([True, False])
        )