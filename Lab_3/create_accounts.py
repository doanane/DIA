import asyncio
from spade import agent

async def create_accounts():
    accounts = [
        ("doanane.sensor@xmpp.jp", "Sensor2024!"),
        ("doanane.fire@xmpp.jp", "Fire2024!"),
        ("doanane.ambulance@xmpp.jp", "Ambulance2024!"),
        ("doanane.evacuation@xmpp.jp", "Evac2024!"),
        ("doanane.hospital@xmpp.jp", "Hospital2024!"),
        ("doanane.traffic@xmpp.jp", "Traffic2024!")
    ]
    
    for jid, password in accounts:
        try:
            temp_agent = agent.Agent(jid, password)
            await temp_agent.start(auto_register=True)
            await temp_agent.stop()
            print(f"✓ Created: {jid}")
        except Exception as e:
            print(f"✗ Failed: {jid} - {e}")

if __name__ == "__main__":
    asyncio.run(create_accounts())
    