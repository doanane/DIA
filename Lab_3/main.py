import asyncio
import os
from agents import (
    SensorAgent,
    CommandCenterAgent,
    FireAgent,
    AmbulanceAgent,
    EvacuationAgent,
    HospitalAgent,
    TrafficAgent
)

async def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    JID = "doanane@xmpp.jp"
    PASSWORD = "S@0570263170s"
    
    print("=" * 70)
    print("           MULTI-AGENT DISASTER RESPONSE SYSTEM")
    print("=" * 70)
    print(f"\n[SYSTEM] Agent Communication Protocol: XMPP")
    print(f"[SYSTEM] Command Center JID: {JID}")
    print(f"[SYSTEM] Initializing agent network...\n")
    print("-" * 70)
    
    command_center = CommandCenterAgent(JID, PASSWORD)
    sensor = SensorAgent(JID, PASSWORD, JID)
    fire1 = FireAgent(JID, PASSWORD, JID)
    fire2 = FireAgent(JID, PASSWORD, JID)
    ambulance1 = AmbulanceAgent(JID, PASSWORD, JID)
    ambulance2 = AmbulanceAgent(JID, PASSWORD, JID)
    ambulance3 = AmbulanceAgent(JID, PASSWORD, JID)
    evacuation1 = EvacuationAgent(JID, PASSWORD, JID)
    evacuation2 = EvacuationAgent(JID, PASSWORD, JID)
    hospital = HospitalAgent(JID, PASSWORD, 150)
    traffic_north = TrafficAgent(JID, PASSWORD, "NORTH")
    traffic_south = TrafficAgent(JID, PASSWORD, "SOUTH")
    traffic_east = TrafficAgent(JID, PASSWORD, "EAST")
    traffic_west = TrafficAgent(JID, PASSWORD, "WEST")
    
    await command_center.start(auto_register=True)
    await sensor.start(auto_register=True)
    await fire1.start(auto_register=True)
    await fire2.start(auto_register=True)
    await ambulance1.start(auto_register=True)
    await ambulance2.start(auto_register=True)
    await ambulance3.start(auto_register=True)
    await evacuation1.start(auto_register=True)
    await evacuation2.start(auto_register=True)
    await hospital.start(auto_register=True)
    await traffic_north.start(auto_register=True)
    await traffic_south.start(auto_register=True)
    await traffic_east.start(auto_register=True)
    await traffic_west.start(auto_register=True)
    
    print("\n" + "=" * 70)
    print("           ✓ ALL AGENTS ONLINE - SYSTEM ACTIVE")
    print("=" * 70)
    print("\nDEPLOYED RESOURCES:")
    print("  • Sensor Network    : 1x Multi-spectral sensor array")
    print("  • Fire Response     : 2x Type-1 Fire Engines")
    print("  • Medical Response  : 3x Advanced Life Support units")
    print("  • Rescue Teams      : 2x Mass Evacuation units")
    print("  • Medical Facility  : 1x Level-1 Trauma Center (150 beds)")
    print("  • Traffic Control   : 4x Intelligent Traffic Zones")
    print("\n" + "=" * 70)
    print(">>> DISASTER MONITORING ACTIVE - Waiting for events <<<")
    print("=" * 70 + "\n")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("           SHUTTING DOWN DISASTER RESPONSE SYSTEM")
        print("=" * 70 + "\n")
        
        await command_center.stop()
        await sensor.stop()
        await fire1.stop()
        await fire2.stop()
        await ambulance1.stop()
        await ambulance2.stop()
        await ambulance3.stop()
        await evacuation1.stop()
        await evacuation2.stop()
        await hospital.stop()
        await traffic_north.stop()
        await traffic_south.stop()
        await traffic_east.stop()
        await traffic_west.stop()
        
        print("\n" + "=" * 70)
        print("           ✓ SYSTEM OFFLINE - All agents disconnected")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())