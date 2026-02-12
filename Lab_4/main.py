import asyncio
import os
import signal
from agents import (
    SensorAgent,
    RescueAgent,
    LogisticsAgent,
    CoordinatorAgent
)
from utils.helpers import log_relief_operation

async def main():
    # Clear terminal
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # XMPP Credentials - Your single account
    JID = "doanane@xmpp.jp"
    PASSWORD = "S@0570263170s"
    
    # Print header
    print("=" * 80)
    print("           DISASTER RESPONSE & RELIEF COORDINATION SYSTEM")
    print("                       Multi-Agent Systems Lab 4")
    print("=" * 80)
    print(f"\n[SYSTEM] XMPP Server: xmpp.jp")
    print(f"[SYSTEM] Coordinator JID: {JID}")
    print(f"[SYSTEM] Initializing decentralized agent network...\n")
    print("-" * 80)
    
    # Create Coordinator Agent (Central decision maker)
    coordinator = CoordinatorAgent(JID, PASSWORD)
    
    # Create Sensor Agents (Disaster detection)
    sensor1 = SensorAgent(JID, PASSWORD, JID)
    sensor2 = SensorAgent(JID, PASSWORD, JID)
    
    # Create Rescue Agents (Operations)
    rescue1 = RescueAgent(JID, PASSWORD, JID)
    rescue2 = RescueAgent(JID, PASSWORD, JID)
    rescue3 = RescueAgent(JID, PASSWORD, JID)
    
    # Create Logistics Agents (Supplies management)
    logistics1 = LogisticsAgent(JID, PASSWORD, JID)
    logistics2 = LogisticsAgent(JID, PASSWORD, JID)
    
    # Start all agents
    await coordinator.start(auto_register=True)
    await sensor1.start(auto_register=True)
    await sensor2.start(auto_register=True)
    await rescue1.start(auto_register=True)
    await rescue2.start(auto_register=True)
    await rescue3.start(auto_register=True)
    await logistics1.start(auto_register=True)
    await logistics2.start(auto_register=True)
    
    # Register agents with coordinator
    await coordinator.register_rescue_agent(str(rescue1.jid))
    await coordinator.register_rescue_agent(str(rescue2.jid))
    await coordinator.register_rescue_agent(str(rescue3.jid))
    await coordinator.register_logistics_agent(str(logistics1.jid))
    await coordinator.register_logistics_agent(str(logistics2.jid))
    
    print("\n" + "=" * 80)
    print("                    ✓ ALL AGENTS ONLINE")
    print("=" * 80)
    print("\nDEPLOYED RESOURCES:")
    print("  ┌─ COORDINATOR AGENT")
    print("  │   └─ Central coordination & task assignment")
    print("  ├─ SENSOR AGENTS (2)")
    print("  │   ├─ Multi-spectral disaster detection")
    print("  │   └─ Environmental monitoring")
    print("  ├─ RESCUE AGENTS (3)")
    print("  │   ├─ Search & rescue operations")
    print("  │   └─ Casualty evacuation")
    print("  └─ LOGISTICS AGENTS (2)")
    print("      ├─ Supply chain management")
    print("      └─ Relief item distribution")
    print("\n" + "=" * 80)
    print(">>> SYSTEM ACTIVE - Monitoring for disaster events <<<")
    print("=" * 80 + "\n")
    
    # Handle shutdown gracefully
    shutdown = asyncio.Event()
    
    def signal_handler():
        shutdown.set()
    
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)
    
    try:
        await shutdown.wait()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n" + "=" * 80)
        print("           SHUTTING DOWN RELIEF COORDINATION SYSTEM")
        print("=" * 80 + "\n")
        
        # Stop all agents
        await coordinator.stop()
        await sensor1.stop()
        await sensor2.stop()
        await rescue1.stop()
        await rescue2.stop()
        await rescue3.stop()
        await logistics1.stop()
        await logistics2.stop()
        
        print("\n" + "=" * 80)
        print("                 ✓ SYSTEM OFFLINE")
        print("           All agents disconnected successfully")
        print("=" * 80)
        
        # Print final statistics
        print("\nFINAL RELIEF STATISTICS:")
        print(f"  • People Rescued: {coordinator.people_rescued}")
        print(f"  • Rescue Missions: {len(coordinator.completed_rescue_tasks)}")
        print(f"  • Supply Missions: {len(coordinator.completed_supply_tasks)}")
        print(f"  • Disasters Responded: {len(coordinator.disaster_priorities)}")
        print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())