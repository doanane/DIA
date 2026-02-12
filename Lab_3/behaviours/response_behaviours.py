import asyncio
import json
import random
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message

class FireResponseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=0.5)
        if msg and msg.get_metadata("ontology") == "deployment_order":
            order = json.loads(msg.body)
            if order.get("fire_required"):
                self.agent.status = "DEPLOYED"
                self.agent.log(f"RESPONDING to {order['disaster_id']} - Location: {order['location']}")
                
                await asyncio.sleep(2)
                
                self.agent.status = "AVAILABLE"
                self.agent.missions_completed += 1
                
                report = Message(to=self.agent.command_center_jid)
                report.set_metadata("ontology", "mission_report")
                report.body = json.dumps({
                    "disaster_id": order["disaster_id"],
                    "unit": "fire",
                    "unit_id": self.agent.unit_id
                })
                await self.send(report)
                
                self.agent.log(f"MISSION COMPLETE - Fires extinguished")

class AmbulanceResponseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=0.5)
        if msg and msg.get_metadata("ontology") == "deployment_order":
            order = json.loads(msg.body)
            if order.get("medical_required"):
                self.agent.status = "DEPLOYED"
                patients = random.randint(5, 20)
                
                self.agent.log(f"RESPONDING to {order['disaster_id']} - Treating {patients} patients")
                
                await asyncio.sleep(2)
                
                self.agent.patients_treated += patients
                self.agent.missions_completed += 1
                self.agent.status = "AVAILABLE"
                
                report = Message(to=self.agent.command_center_jid)
                report.set_metadata("ontology", "mission_report")
                report.body = json.dumps({
                    "disaster_id": order["disaster_id"],
                    "unit": "ambulance",
                    "unit_id": self.agent.unit_id,
                    "patients": patients
                })
                await self.send(report)
                
                self.agent.log(f"TRANSPORTED {patients} patients to hospital")

class EvacuationResponseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=0.5)
        if msg and msg.get_metadata("ontology") == "deployment_order":
            order = json.loads(msg.body)
            if order.get("evacuation_required"):
                self.agent.status = "DEPLOYED"
                evacuees = random.randint(10, 40)
                
                self.agent.log(f"RESPONDING to {order['disaster_id']} - Evacuating {evacuees} people")
                
                await asyncio.sleep(2)
                
                self.agent.evacuated += evacuees
                self.agent.missions_completed += 1
                self.agent.status = "AVAILABLE"
                
                report = Message(to=self.agent.command_center_jid)
                report.set_metadata("ontology", "mission_report")
                report.body = json.dumps({
                    "disaster_id": order["disaster_id"],
                    "unit": "evacuation",
                    "unit_id": self.agent.unit_id,
                    "evacuated": evacuees
                })
                await self.send(report)
                
                self.agent.log(f"RESCUED {evacuees} people to safe zone")

class HospitalTreatmentBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=0.5)
        if msg and msg.get_metadata("ontology") == "mission_report":
            report = json.loads(msg.body)
            if report.get("unit") == "ambulance":
                patients = report.get("patients", 0)
                if self.agent.available_beds >= patients:
                    self.agent.available_beds -= patients
                    self.agent.admitted_patients += patients
                    self.agent.log(f"ADMITTED {patients} patients - {self.agent.available_beds} beds left")
                else:
                    self.agent.log(f"WARNING: Only {self.agent.available_beds} beds available")

class HospitalStatusBehaviour(PeriodicBehaviour):
    async def run(self):
        occupancy = ((self.agent.capacity - self.agent.available_beds) / self.agent.capacity) * 100
        self.agent.log(f"HOSPITAL STATUS: {self.agent.available_beds}/{self.agent.capacity} beds - {occupancy:.0f}% occupied")

class TrafficControlBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=0.5)
        if msg and msg.get_metadata("ontology") == "deployment_order":
            order = json.loads(msg.body)
            if order.get("evacuation_required") or order.get("fire_required") or order.get("medical_required"):
                self.agent.status = "EMERGENCY_MODE"
                self.agent.routes_cleared += 1
                self.agent.log(f"EMERGENCY CORRIDOR ACTIVATED - Zone: {self.agent.zone}")
                await asyncio.sleep(0.5)

class TrafficStatusBehaviour(PeriodicBehaviour):
    async def run(self):
        self.agent.log(f"TRAFFIC ZONE {self.agent.zone}: {self.agent.status} - Routes cleared: {self.agent.routes_cleared}")