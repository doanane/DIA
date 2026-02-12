import asyncio
import json
import random
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template

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

@dataclass
class DisasterEvent:
    id: str
    type: DisasterType
    severity: SeverityLevel
    location: Tuple[float, float]
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

class SensorAgent(Agent):
    def __init__(self, jid, password, command_center_jid):
        super().__init__(jid, password)
        self.command_center_jid = command_center_jid
        
    async def setup(self):
        print(f"[SENSOR] Online - Monitoring seismic and environmental sensors")
        detection_behaviour = self.DisasterDetectionBehaviour(period=12)
        self.add_behaviour(detection_behaviour)
    
    class DisasterDetectionBehaviour(PeriodicBehaviour):
        async def run(self):
            disaster_types = [DisasterType.EARTHQUAKE, DisasterType.FIRE, DisasterType.FLOOD, 
                            DisasterType.CHEMICAL_SPILL, DisasterType.BUILDING_COLLAPSE]
            severities = [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]
            
            disaster_id = f"D{datetime.now().strftime('%H%M%S')}{random.randint(10,99)}"
            disaster = DisasterEvent(
                id=disaster_id,
                type=random.choice(disaster_types),
                severity=random.choice(severities),
                location=(round(random.uniform(-90, 90), 4), round(random.uniform(-180, 180), 4)),
                timestamp=datetime.now().strftime("%H:%M:%S"),
                affected_people=random.randint(10, 500),
                requires_evacuation=random.choice([True, False]),
                requires_medical=random.choice([True, False]),
                requires_firefighting=random.choice([True, False])
            )
            
            msg = Message(to=self.agent.command_center_jid)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "disaster_detection")
            msg.body = disaster.to_json()
            await self.send(msg)
            
            severity_icons = {1: "⚪", 2: "🟡", 3: "🟠", 4: "🔴"}
            print(f"[SENSOR] ALERT: {severity_icons[disaster.severity.value]} {disaster.type.value.upper()} - {disaster.affected_people} people affected - ID: {disaster.id}")

class CommandCenterAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.active_disasters = {}
        self.completed_missions = []
        self.resources = {
            "fire_truck": {"available": 3, "deployed": 0},
            "ambulance": {"available": 4, "deployed": 0},
            "evacuation_team": {"available": 2, "deployed": 0}
        }
        self.total_people_saved = 0
        self.total_fires_extinguished = 0
        
    async def setup(self):
        print(f"[COMMAND] Online - Disaster coordination center activated")
        assessment_behaviour = self.DisasterAssessmentBehaviour()
        self.add_behaviour(assessment_behaviour)
        status_behaviour = self.StatusBroadcastBehaviour(period=10)
        self.add_behaviour(status_behaviour)
    
    class DisasterAssessmentBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.5)
            if msg and msg.get_metadata("ontology") == "disaster_detection":
                disaster = DisasterEvent.from_json(msg.body)
                
                if disaster.id not in self.agent.active_disasters:
                    self.agent.active_disasters[disaster.id] = disaster
                    
                    priority_score = disaster.severity.value * (disaster.affected_people / 100)
                    
                    print(f"[COMMAND] ASSESSING: {disaster.id} - {disaster.type.value}")
                    print(f"[COMMAND] SEVERITY: {disaster.severity.name} | AFFECTED: {disaster.affected_people} | PRIORITY: {priority_score:.1f}")
                    
                    deployment_order = {
                        "disaster_id": disaster.id,
                        "location": disaster.location,
                        "severity": disaster.severity.value,
                        "type": disaster.type.value,
                        "dispatch_fire": disaster.requires_firefighting,
                        "dispatch_medical": disaster.requires_medical,
                        "dispatch_evacuation": disaster.requires_evacuation
                    }
                    
                    broadcast_msg = Message(to=str(msg.sender))
                    broadcast_msg.set_metadata("ontology", "deployment_order")
                    broadcast_msg.body = json.dumps(deployment_order)
                    await self.send(broadcast_msg)
                    
                    print(f"[COMMAND] DEPLOYMENT ORDER ISSUED: Fire:{disaster.requires_firefighting} Medical:{disaster.requires_medical} Evac:{disaster.requires_evacuation}")
            
            elif msg and msg.get_metadata("ontology") == "mission_report":
                report = json.loads(msg.body)
                disaster_id = report["disaster_id"]
                
                if report["unit"] == "fire":
                    self.agent.total_fires_extinguished += 1
                    self.agent.resources["fire_truck"]["deployed"] += 1
                    self.agent.resources["fire_truck"]["available"] -= 1
                    print(f"[COMMAND] FIRE SUPPRESSED - Total: {self.agent.total_fires_extinguished}")
                
                elif report["unit"] == "ambulance":
                    patients = report.get("patients", 0)
                    self.agent.total_people_saved += patients
                    self.agent.resources["ambulance"]["deployed"] += 1
                    self.agent.resources["ambulance"]["available"] -= 1
                    print(f"[COMMAND] PATIENTS TREATED: {patients} - Total saved: {self.agent.total_people_saved}")
                
                elif report["unit"] == "evacuation":
                    evacuees = report.get("evacuated", 0)
                    self.agent.total_people_saved += evacuees
                    self.agent.resources["evacuation_team"]["deployed"] += 1
                    self.agent.resources["evacuation_team"]["available"] -= 1
                    print(f"[COMMAND] EVACUEES RESCUED: {evacuees} - Total saved: {self.agent.total_people_saved}")
                
                if disaster_id in self.agent.active_disasters:
                    del self.agent.active_disasters[disaster_id]
                    self.agent.completed_missions.append(disaster_id)
    
    class StatusBroadcastBehaviour(PeriodicBehaviour):
        async def run(self):
            active_count = len(self.agent.active_disasters)
            print(f"[COMMAND] STATUS: {active_count} active | FIRE: {self.agent.resources['fire_truck']['available']} | AMB: {self.agent.resources['ambulance']['available']} | EVAC: {self.agent.resources['evacuation_team']['available']} | SAVED: {self.agent.total_people_saved}")

class FireResponseAgent(Agent):
    def __init__(self, jid, password, command_center_jid, unit_id):
        super().__init__(jid, password)
        self.command_center_jid = command_center_jid
        self.unit_id = unit_id
        self.status = "STANDBY"
        self.missions_completed = 0
        
    async def setup(self):
        print(f"[FIRE-{self.unit_id}] Online - Type 1 Fire Engine ready")
        behaviour = self.FireBehaviour()
        self.add_behaviour(behaviour)
        status_behaviour = self.StatusReportBehaviour(period=8)
        self.add_behaviour(status_behaviour)
    
    class FireBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.5)
            if msg and msg.get_metadata("ontology") == "deployment_order":
                order = json.loads(msg.body)
                if order.get("dispatch_fire"):
                    self.agent.status = "DEPLOYED"
                    print(f"[FIRE-{self.agent.unit_id}] RESPONDING to {order['disaster_id']} - {order['type']}")
                    print(f"[FIRE-{self.agent.unit_id}] Location: {order['location']}")
                    
                    await asyncio.sleep(2)
                    
                    self.agent.status = "STANDBY"
                    self.agent.missions_completed += 1
                    
                    report = Message(to=self.agent.command_center_jid)
                    report.set_metadata("ontology", "mission_report")
                    report.body = json.dumps({
                        "disaster_id": order["disaster_id"],
                        "unit": "fire",
                        "unit_id": self.agent.unit_id,
                        "status": "COMPLETE"
                    })
                    await self.send(report)
                    
                    print(f"[FIRE-{self.agent.unit_id}] MISSION COMPLETE - Fire contained")
    
    class StatusReportBehaviour(PeriodicBehaviour):
        async def run(self):
            pass

class AmbulanceAgent(Agent):
    def __init__(self, jid, password, command_center_jid, unit_id):
        super().__init__(jid, password)
        self.command_center_jid = command_center_jid
        self.unit_id = unit_id
        self.status = "STANDBY"
        self.patients_treated = 0
        self.missions_completed = 0
        
    async def setup(self):
        print(f"[AMB-{self.unit_id}] Online - Advanced Life Support unit ready")
        behaviour = self.MedicalBehaviour()
        self.add_behaviour(behaviour)
        status_behaviour = self.StatusReportBehaviour(period=8)
        self.add_behaviour(status_behaviour)
    
    class MedicalBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.5)
            if msg and msg.get_metadata("ontology") == "deployment_order":
                order = json.loads(msg.body)
                if order.get("dispatch_medical"):
                    self.agent.status = "DEPLOYED"
                    patients = random.randint(5, 25)
                    
                    print(f"[AMB-{self.agent.unit_id}] RESPONDING to {order['disaster_id']}")
                    print(f"[AMB-{self.agent.unit_id}] Treating {patients} patients at scene")
                    
                    await asyncio.sleep(2)
                    
                    self.agent.patients_treated += patients
                    self.agent.missions_completed += 1
                    self.agent.status = "STANDBY"
                    
                    report = Message(to=self.agent.command_center_jid)
                    report.set_metadata("ontology", "mission_report")
                    report.body = json.dumps({
                        "disaster_id": order["disaster_id"],
                        "unit": "ambulance",
                        "unit_id": self.agent.unit_id,
                        "patients": patients,
                        "total_treated": self.agent.patients_treated
                    })
                    await self.send(report)
                    
                    print(f"[AMB-{self.agent.unit_id}] TRANSPORTED {patients} patients to hospital")
    
    class StatusReportBehaviour(PeriodicBehaviour):
        async def run(self):
            pass

class EvacuationAgent(Agent):
    def __init__(self, jid, password, command_center_jid, unit_id):
        super().__init__(jid, password)
        self.command_center_jid = command_center_jid
        self.unit_id = unit_id
        self.status = "STANDBY"
        self.evacuated = 0
        self.missions_completed = 0
        
    async def setup(self):
        print(f"[EVAC-{self.unit_id}] Online - Mass evacuation unit ready")
        behaviour = self.EvacuationBehaviour()
        self.add_behaviour(behaviour)
        status_behaviour = self.StatusReportBehaviour(period=8)
        self.add_behaviour(status_behaviour)
    
    class EvacuationBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.5)
            if msg and msg.get_metadata("ontology") == "deployment_order":
                order = json.loads(msg.body)
                if order.get("dispatch_evacuation"):
                    self.agent.status = "DEPLOYED"
                    evacuees = random.randint(10, 60)
                    
                    print(f"[EVAC-{self.agent.unit_id}] RESPONDING to {order['disaster_id']}")
                    print(f"[EVAC-{self.agent.unit_id}] Evacuating {evacuees} people from danger zone")
                    
                    await asyncio.sleep(2)
                    
                    self.agent.evacuated += evacuees
                    self.agent.missions_completed += 1
                    self.agent.status = "STANDBY"
                    
                    report = Message(to=self.agent.command_center_jid)
                    report.set_metadata("ontology", "mission_report")
                    report.body = json.dumps({
                        "disaster_id": order["disaster_id"],
                        "unit": "evacuation",
                        "unit_id": self.agent.unit_id,
                        "evacuated": evacuees,
                        "total_evacuated": self.agent.evacuated
                    })
                    await self.send(report)
                    
                    print(f"[EVAC-{self.agent.unit_id}] SAFE ZONE - {evacuees} people rescued")
    
    class StatusReportBehaviour(PeriodicBehaviour):
        async def run(self):
            pass

class HospitalAgent(Agent):
    def __init__(self, jid, password, capacity=150):
        super().__init__(jid, password)
        self.capacity = capacity
        self.available_beds = capacity
        self.admitted_patients = 0
        self.discharged_patients = 0
        
    async def setup(self):
        print(f"[HOSPITAL] Online - Level 1 Trauma Center - {self.available_beds} beds available")
        behaviour = self.HospitalBehaviour()
        self.add_behaviour(behaviour)
        status_behaviour = self.StatusBroadcastBehaviour(period=12)
        self.add_behaviour(status_behaviour)
    
    class HospitalBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.5)
            if msg and msg.get_metadata("ontology") == "mission_report":
                report = json.loads(msg.body)
                if report.get("unit") == "ambulance":
                    patients = report.get("patients", 0)
                    if self.agent.available_beds >= patients:
                        self.agent.available_beds -= patients
                        self.agent.admitted_patients += patients
                        print(f"[HOSPITAL] ADMITTED {patients} patients - {self.agent.available_beds} beds remaining")
                    else:
                        print(f"[HOSPITAL] WARNING: Insufficient beds - Diverting {patients - self.agent.available_beds} patients")
                        self.agent.available_beds = 0
                        self.agent.admitted_patients += self.agent.available_beds
    
    class StatusBroadcastBehaviour(PeriodicBehaviour):
        async def run(self):
            occupancy = ((self.agent.capacity - self.agent.available_beds) / self.agent.capacity) * 100
            print(f"[HOSPITAL] STATUS: {self.agent.available_beds}/{self.agent.capacity} beds | OCCUPANCY: {occupancy:.0f}% | ADMITTED: {self.agent.admitted_patients}")

class TrafficAgent(Agent):
    def __init__(self, jid, password, zone):
        super().__init__(jid, password)
        self.zone = zone
        self.status = "NORMAL"
        self.routes_cleared = 0
        
    async def setup(self):
        print(f"[TRAFFIC] Online - Zone: {self.zone} - Intelligent traffic control active")
        behaviour = self.TrafficBehaviour()
        self.add_behaviour(behaviour)
        status_behaviour = self.StatusBroadcastBehaviour(period=15)
        self.add_behaviour(status_behaviour)
    
    class TrafficBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=0.5)
            if msg and msg.get_metadata("ontology") == "deployment_order":
                order = json.loads(msg.body)
                if order.get("dispatch_evacuation") or order.get("dispatch_fire") or order.get("dispatch_medical"):
                    self.agent.status = "EMERGENCY_CORRIDOR_ACTIVE"
                    self.agent.routes_cleared += 1
                    print(f"[TRAFFIC] {self.agent.zone}: Emergency corridor activated for {order['disaster_id']}")
                    print(f"[TRAFFIC] Traffic lights reprogrammed - Response routes cleared")
                    await asyncio.sleep(0.5)
    
    class StatusBroadcastBehaviour(PeriodicBehaviour):
        async def run(self):
            print(f"[TRAFFIC] {self.agent.zone}: {self.agent.status} | Routes cleared: {self.agent.routes_cleared}")

async def main():
    JID = "doanane@xmpp.jp"
    PASSWORD = "S@0570263170s"
    
    print("=" * 70)
    print("            MULTI-AGENT DISASTER RESPONSE SYSTEM v2.0")
    print("=" * 70)
    print(f"\n[SYSTEM] Initializing with command center JID: {JID}")
    print("[SYSTEM] Establishing XMPP communication channels...")
    print("=" * 70 + "\n")
    
    command_center = CommandCenterAgent(JID, PASSWORD)
    sensor = SensorAgent(JID, PASSWORD, JID)
    fire1 = FireResponseAgent(JID, PASSWORD, JID, "FT-01")
    fire2 = FireResponseAgent(JID, PASSWORD, JID, "FT-02")
    amb1 = AmbulanceAgent(JID, PASSWORD, JID, "ALS-01")
    amb2 = AmbulanceAgent(JID, PASSWORD, JID, "ALS-02")
    evac1 = EvacuationAgent(JID, PASSWORD, JID, "MEV-01")
    evac2 = EvacuationAgent(JID, PASSWORD, JID, "MEV-02")
    hospital = HospitalAgent(JID, PASSWORD, 150)
    traffic1 = TrafficAgent(JID, PASSWORD, "NORTH")
    traffic2 = TrafficAgent(JID, PASSWORD, "SOUTH")
    
    await command_center.start(auto_register=True)
    await sensor.start(auto_register=True)
    await fire1.start(auto_register=True)
    await fire2.start(auto_register=True)
    await amb1.start(auto_register=True)
    await amb2.start(auto_register=True)
    await evac1.start(auto_register=True)
    await evac2.start(auto_register=True)
    await hospital.start(auto_register=True)
    await traffic1.start(auto_register=True)
    await traffic2.start(auto_register=True)
    
    print("\n" + "=" * 70)
    print("✓ ALL AGENTS ONLINE - DISASTER MONITORING NETWORK ACTIVE")
    print("=" * 70 + "\n")
    print("System Components:")
    print("  • SENSOR NETWORK    : 1x Seismic/Acoustic sensor array")
    print("  • FIRE RESCUE       : 2x Type-1 Fire Engines")
    print("  • EMS               : 2x Advanced Life Support units")
    print("  • RESCUE           : 2x Mass Evacuation teams")
    print("  • MEDICAL          : 1x Level-1 Trauma Center (150 beds)")
    print("  • TRAFFIC          : 2x Intelligent Traffic Zones")
    print("\n" + "=" * 70)
    print(">> SYSTEM ACTIVE - Monitoring for seismic events, fires, floods, and chemical spills <<")
    print("=" * 70 + "\n")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print(">>> INITIATING SYSTEM SHUTDOWN SEQUENCE <<<")
        print("=" * 70 + "\n")
        
        await command_center.stop()
        await sensor.stop()
        await fire1.stop()
        await fire2.stop()
        await amb1.stop()
        await amb2.stop()
        await evac1.stop()
        await evac2.stop()
        await hospital.stop()
        await traffic1.stop()
        await traffic2.stop()
        
        print("\n" + "=" * 70)
        print("✓ SYSTEM OFFLINE - All agents disconnected")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())