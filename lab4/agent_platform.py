# agent_platform.py
import json
import time
import uuid
import socket
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

class ACLMessage:
    def __init__(self, performative: str, sender: str, receivers: List[str], content: Any = None):
        self.performative = performative
        self.sender = sender
        self.receivers = receivers
        self.content = content
        self.conversation_id = str(uuid.uuid4())
        self.reply_with = str(uuid.uuid4())
        self.in_reply_to = None
        self.language = "json"
        self.ontology = "rescue_ontology"
        self.protocol = "fipa-request"
        self.timestamp = datetime.now().isoformat()
    
    def set_reply_to(self, reply_with: str):
        self.in_reply_to = reply_with
    
    def to_json(self) -> str:
        return json.dumps({
            "performative": self.performative,
            "sender": self.sender,
            "receivers": self.receivers,
            "content": self.content,
            "conversation_id": self.conversation_id,
            "reply_with": self.reply_with,
            "in_reply_to": self.in_reply_to,
            "language": self.language,
            "ontology": self.ontology,
            "protocol": self.protocol,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        msg = cls(
            performative=data["performative"],
            sender=data["sender"],
            receivers=data["receivers"],
            content=data["content"]
        )
        msg.conversation_id = data["conversation_id"]
        msg.reply_with = data["reply_with"]
        msg.in_reply_to = data["in_reply_to"]
        msg.language = data["language"]
        msg.ontology = data["ontology"]
        msg.protocol = data["protocol"]
        msg.timestamp = data["timestamp"]
        return msg


class MessageTransportService:
    def __init__(self, host: str = "localhost", port: int = 5000):
        self.host = host
        self.port = port
        self.agents = {}
        self.message_log = []
        self.server_socket = None
        self.running = False
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.running = True
        
        print(f"Message Transport Service started on {self.host}:{self.port}")
        
        def accept_connections():
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                    thread.daemon = True
                    thread.start()
                except:
                    break
        
        thread = threading.Thread(target=accept_connections)
        thread.daemon = True
        thread.start()
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def register_agent(self, agent_name: str, host: str, port: int):
        self.agents[agent_name] = {"host": host, "port": port}
        print(f"Agent '{agent_name}' registered at {host}:{port}")
    
    def handle_client(self, client_socket: socket.socket, address):
        try:
            data = client_socket.recv(8192).decode('utf-8')
            if data:
                self.route_message(data)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def route_message(self, message_json: str):
        try:
            msg = ACLMessage.from_json(message_json)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "direction": "INCOMING",
                "message": message_json
            }
            self.message_log.append(log_entry)
            
            print(f"\n[TRANSPORT] Routing message from {msg.sender} to {msg.receivers}")
            
            for receiver in msg.receivers:
                if receiver in self.agents:
                    agent_info = self.agents[receiver]
                    self.send_to_agent(agent_info["host"], agent_info["port"], message_json)
                else:
                    print(f"[TRANSPORT] Unknown receiver: {receiver}")
        except Exception as e:
            print(f"[TRANSPORT] Error routing message: {e}")
    
    def send_to_agent(self, host: str, port: int, message_json: str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.send(message_json.encode('utf-8'))
            sock.close()
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "direction": "OUTGOING",
                "destination": f"{host}:{port}",
                "message": message_json
            }
            self.message_log.append(log_entry)
            
        except Exception as e:
            print(f"[TRANSPORT] Failed to send to {host}:{port}: {e}")


class Agent:
    def __init__(self, name: str, mts_host: str = "localhost", mts_port: int = 5000):
        self.name = name
        self.mts_host = mts_host
        self.mts_port = mts_port
        self.server_socket = None
        self.running = False
        self.message_handlers = {
            "inform": self.handle_inform,
            "request": self.handle_request,
            "agree": self.handle_agree,
            "refuse": self.handle_refuse,
            "failure": self.handle_failure
        }
        self.received_messages = []
        self.sent_messages = []
        self.knowledge_base = {}
        self.active_conversations = {}
        
    def start(self, listen_host: str = "localhost", listen_port: int = None):
        if listen_port is None:
            listen_port = 6000 + hash(self.name) % 1000
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((listen_host, listen_port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"Agent '{self.name}' listening on {listen_host}:{listen_port}")
        
        def listen_for_messages():
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    data = client_socket.recv(8192).decode('utf-8')
                    if data:
                        self.receive_message(data)
                    client_socket.close()
                except:
                    break
        
        thread = threading.Thread(target=listen_for_messages)
        thread.daemon = True
        thread.start()
        
        return listen_port
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def send_message(self, msg: ACLMessage):
        try:
            msg.sender = self.name
            
            message_json = msg.to_json()
            
            self.sent_messages.append({
                "timestamp": datetime.now().isoformat(),
                "message": message_json
            })
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.mts_host, self.mts_port))
            sock.send(message_json.encode('utf-8'))
            sock.close()
            
            print(f"[{self.name}] Sent {msg.performative} to {msg.receivers}")
            
        except Exception as e:
            print(f"[{self.name}] Failed to send message: {e}")
    
    def receive_message(self, message_json: str):
        try:
            msg = ACLMessage.from_json(message_json)
            
            self.received_messages.append({
                "timestamp": datetime.now().isoformat(),
                "message": message_json
            })
            
            print(f"[{self.name}] Received {msg.performative} from {msg.sender}")
            
            if msg.performative in self.message_handlers:
                self.message_handlers[msg.performative](msg)
            else:
                print(f"[{self.name}] No handler for performative: {msg.performative}")
                
        except Exception as e:
            print(f"[{self.name}] Error receiving message: {e}")
    
    def handle_inform(self, msg: ACLMessage):
        print(f"[{self.name}] Processing INFORM from {msg.sender}")
        print(f"[{self.name}] Content: {msg.content}")
        
        self.knowledge_base[msg.sender] = msg.content
        
        if msg.in_reply_to:
            print(f"[{self.name}] This is a reply to conversation {msg.in_reply_to}")
    
    def handle_request(self, msg: ACLMessage):
        print(f"[{self.name}] Processing REQUEST from {msg.sender}")
        print(f"[{self.name}] Request content: {msg.content}")
        
        if self.can_perform_request(msg.content):
            reply = ACLMessage(
                performative="agree",
                sender=self.name,
                receivers=[msg.sender],
                content={"status": "accepted", "request": msg.content}
            )
            reply.set_reply_to(msg.reply_with)
            self.send_message(reply)
            
            self.perform_action(msg.content)
            
            inform = ACLMessage(
                performative="inform",
                sender=self.name,
                receivers=[msg.sender],
                content={"result": "action_completed", "details": msg.content}
            )
            inform.set_reply_to(msg.reply_with)
            self.send_message(inform)
        else:
            reply = ACLMessage(
                performative="refuse",
                sender=self.name,
                receivers=[msg.sender],
                content={"status": "refused", "reason": "cannot_perform", "request": msg.content}
            )
            reply.set_reply_to(msg.reply_with)
            self.send_message(reply)
    
    def handle_agree(self, msg: ACLMessage):
        print(f"[{self.name}] Received AGREE from {msg.sender}")
        print(f"[{self.name}] Agreement content: {msg.content}")
        
        self.active_conversations[msg.conversation_id] = {
            "agent": msg.sender,
            "status": "agreed",
            "content": msg.content
        }
    
    def handle_refuse(self, msg: ACLMessage):
        print(f"[{self.name}] Received REFUSE from {msg.sender}")
        print(f"[{self.name}] Refusal content: {msg.content}")
        
        self.active_conversations[msg.conversation_id] = {
            "agent": msg.sender,
            "status": "refused",
            "content": msg.content
        }
    
    def handle_failure(self, msg: ACLMessage):
        print(f"[{self.name}] Received FAILURE from {msg.sender}")
        print(f"[{self.name}] Failure content: {msg.content}")
    
    def can_perform_request(self, request: Any) -> bool:
        return True
    
    def perform_action(self, request: Any):
        print(f"[{self.name}] Performing action: {request}")
        time.sleep(1)


class RescueAgent(Agent):
    def __init__(self, name: str, role: str, mts_host: str = "localhost", mts_port: int = 5000):
        super().__init__(name, mts_host, mts_port)
        self.role = role
        self.capabilities = {
            "coordinator": ["assign_task", "request_status", "deploy_team", "coordinate_rescue"],
            "searcher": ["search_area", "report_finding", "scan_environment"],
            "medic": ["treat_victim", "assess_condition", "request_evacuation"],
            "transporter": ["evacuate_victim", "move_to_location", "return_to_base"]
        }
        self.status = "idle"
        self.location = (0, 0)
        self.assigned_tasks = []
        
    def handle_request(self, msg: ACLMessage):
        super().handle_request(msg)
        
        if isinstance(msg.content, dict):
            action = msg.content.get("action")
            if action in self.capabilities.get(self.role, []):
                print(f"[{self.name}] This request matches my {self.role} capabilities")
    
    def handle_inform(self, msg: ACLMessage):
        super().handle_inform(msg)
        
        if isinstance(msg.content, dict):
            if msg.content.get("type") == "victim_found":
                print(f"[{self.name}] VICTIM REPORTED at {msg.content.get('location')}")
                
                if self.role == "coordinator":
                    self.coordinate_rescue(msg.content)
    
    def can_perform_request(self, request: Any) -> bool:
        if isinstance(request, dict):
            action = request.get("action")
            if action in self.capabilities.get(self.role, []):
                return True
        return False
    
    def perform_action(self, request: Any):
        if not isinstance(request, dict):
            return
            
        action = request.get("action")
        
        if action == "search_area":
            self.status = "searching"
            print(f"[{self.name}] Searching area: {request.get('area')}")
            
        elif action == "treat_victim":
            self.status = "treating"
            print(f"[{self.name}] Treating victim at {request.get('location')}")
            
        elif action == "evacuate_victim":
            self.status = "evacuating"
            print(f"[{self.name}] Evacuating victim from {request.get('location')}")
            
        elif action == "assign_task":
            self.status = "assigning"
            print(f"[{self.name}] Assigning task to {request.get('target_agent')}")
        
        time.sleep(2)
        self.status = "idle"
    
    def coordinate_rescue(self, victim_info: dict):
        print(f"[{self.name}] Coordinating rescue for victim at {victim_info.get('location')}")
        
        request = ACLMessage(
            performative="request",
            sender=self.name,
            receivers=["medic_agent"],
            content={
                "action": "treat_victim",
                "location": victim_info.get("location"),
                "victim_id": victim_info.get("victim_id"),
                "priority": victim_info.get("priority", "normal")
            }
        )
        self.send_message(request)


def setup_message_transport():
    mts = MessageTransportService(host="localhost", port=5000)
    mts.start()
    time.sleep(1)
    return mts


def run_agent_communication_demo():
    print("=" * 70)
    print("FIPA-ACL AGENT COMMUNICATION SYSTEM - LAB 4")
    print("=" * 70)
    
    mts = setup_message_transport()
    
    coordinator = RescueAgent("coordinator_agent", "coordinator")
    searcher = RescueAgent("searcher_agent", "searcher")
    medic = RescueAgent("medic_agent", "medic")
    transporter = RescueAgent("transporter_agent", "transporter")
    
    coord_port = coordinator.start(listen_port=6001)
    search_port = searcher.start(listen_port=6002)
    medic_port = medic.start(listen_port=6003)
    trans_port = transporter.start(listen_port=6004)
    
    time.sleep(1)
    
    mts.register_agent("coordinator_agent", "localhost", 6001)
    mts.register_agent("searcher_agent", "localhost", 6002)
    mts.register_agent("medic_agent", "localhost", 6003)
    mts.register_agent("transporter_agent", "localhost", 6004)
    
    time.sleep(2)
    
    print("\n" + "=" * 70)
    print("SCENARIO 1: REQUEST PERFORMATIVE")
    print("=" * 70)
    
    request_msg = ACLMessage(
        performative="request",
        sender="coordinator_agent",
        receivers=["searcher_agent"],
        content={
            "action": "search_area",
            "area": "sector_7",
            "priority": "high",
            "grid_size": "10x10"
        }
    )
    coordinator.send_message(request_msg)
    
    time.sleep(3)
    
    print("\n" + "=" * 70)
    print("SCENARIO 2: INFORM PERFORMATIVE")
    print("=" * 70)
    
    inform_msg = ACLMessage(
        performative="inform",
        sender="searcher_agent",
        receivers=["coordinator_agent"],
        content={
            "type": "victim_found",
            "location": [23, 45],
            "victim_id": "V001",
            "condition": "conscious",
            "priority": "critical",
            "timestamp": datetime.now().isoformat()
        }
    )
    searcher.send_message(inform_msg)
    
    time.sleep(3)
    
    print("\n" + "=" * 70)
    print("SCENARIO 3: COORDINATED RESPONSE")
    print("=" * 70)
    
    request_msg = ACLMessage(
        performative="request",
        sender="coordinator_agent",
        receivers=["medic_agent", "transporter_agent"],
        content={
            "action": "deploy_team",
            "location": [23, 45],
            "victim_id": "V001",
            "mission": "rescue_operation"
        }
    )
    coordinator.send_message(request_msg)
    
    time.sleep(3)
    
    print("\n" + "=" * 70)
    print("SCENARIO 4: MULTI-AGENT COORDINATION")
    print("=" * 70)
    
    for i in range(3):
        victim_report = ACLMessage(
            performative="inform",
            sender="searcher_agent",
            receivers=["coordinator_agent"],
            content={
                "type": "victim_found",
                "location": [10 + i*5, 20 + i*5],
                "victim_id": f"V00{i+2}",
                "condition": "injured",
                "priority": "normal"
            }
        )
        searcher.send_message(victim_report)
        time.sleep(1)
    
    time.sleep(5)
    
    print("\n" + "=" * 70)
    print("SCENARIO 5: REFUSE PERFORMATIVE")
    print("=" * 70)
    
    invalid_request = ACLMessage(
        performative="request",
        sender="coordinator_agent",
        receivers=["medic_agent"],
        content={
            "action": "fly_helicopter",
            "reason": "aerial_support"
        }
    )
    coordinator.send_message(invalid_request)
    
    time.sleep(3)
    
    print("\n" + "=" * 70)
    print("AGENT COMMUNICATION SUMMARY")
    print("=" * 70)
    
    agents = [coordinator, searcher, medic, transporter]
    
    for agent in agents:
        print(f"\nAgent: {agent.name} (Role: {agent.role})")
        print(f"  Messages Sent: {len(agent.sent_messages)}")
        print(f"  Messages Received: {len(agent.received_messages)}")
        print(f"  Current Status: {agent.status}")
        print(f"  Knowledge Base Entries: {len(agent.knowledge_base)}")
    
    print("\n" + "=" * 70)
    print("MESSAGE TRANSPORT SERVICE LOG")
    print("=" * 70)
    
    for i, entry in enumerate(mts.message_log[-10:]):
        try:
            msg = ACLMessage.from_json(entry["message"])
            print(f"{i+1}. {entry['direction']:8} | {msg.performative:7} | {msg.sender:15} -> {msg.receivers}")
        except:
            pass
    
    return mts, agents


def save_message_logs(mts, agents, filename="fipa_acl_message_logs.txt"):
    with open(filename, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("FIPA-ACL MESSAGE EXCHANGE LOGS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("MESSAGE TRANSPORT SERVICE LOGS\n")
        f.write("-" * 40 + "\n")
        for i, entry in enumerate(mts.message_log):
            f.write(f"\n--- Log Entry {i+1} ---\n")
            f.write(f"Timestamp: {entry['timestamp']}\n")
            f.write(f"Direction: {entry['direction']}\n")
            if 'destination' in entry:
                f.write(f"Destination: {entry['destination']}\n")
            f.write("Message:\n")
            
            try:
                msg = ACLMessage.from_json(entry["message"])
                f.write(f"  Performative: {msg.performative}\n")
                f.write(f"  Sender: {msg.sender}\n")
                f.write(f"  Receivers: {msg.receivers}\n")
                f.write(f"  Content: {msg.content}\n")
                f.write(f"  Conversation ID: {msg.conversation_id}\n")
            except:
                f.write(f"  {entry['message']}\n")
        
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("AGENT MESSAGE HISTORIES\n")
        f.write("=" * 80 + "\n")
        
        for agent in agents:
            f.write(f"\nAGENT: {agent.name} (Role: {agent.role})\n")
            f.write("-" * 40 + "\n")
            
            f.write("\nSENT MESSAGES:\n")
            for i, sent in enumerate(agent.sent_messages):
                try:
                    msg = ACLMessage.from_json(sent["message"])
                    f.write(f"  {i+1}. [{sent['timestamp']}] {msg.performative} -> {msg.receivers}\n")
                except:
                    f.write(f"  {i+1}. {sent}\n")
            
            f.write("\nRECEIVED MESSAGES:\n")
            for i, recv in enumerate(agent.received_messages):
                try:
                    msg = ACLMessage.from_json(recv["message"])
                    f.write(f"  {i+1}. [{recv['timestamp']}] {msg.performative} from {msg.sender}\n")
                except:
                    f.write(f"  {i+1}. {recv}\n")
    
    print(f"\nMessage logs saved to {filename}")


def generate_message_statistics(agents):
    print("\n" + "=" * 70)
    print("FIPA-ACL MESSAGE STATISTICS")
    print("=" * 70)
    
    stats = {
        "inform": 0,
        "request": 0,
        "agree": 0,
        "refuse": 0,
        "failure": 0
    }
    
    for agent in agents:
        for sent in agent.sent_messages:
            try:
                msg = ACLMessage.from_json(sent["message"])
                if msg.performative in stats:
                    stats[msg.performative] += 1
            except:
                pass
    
    print(f"\nPerformative Distribution:")
    for perf, count in stats.items():
        print(f"  {perf:8}: {count}")
    
    total = sum(stats.values())
    print(f"\nTotal Messages Exchanged: {total}")


if __name__ == "__main__":
    mts = None
    agents = None
    
    try:
        mts, agents = run_agent_communication_demo()
        
        print("\n" + "=" * 70)
        print("GENERATING MESSAGE LOGS AND STATISTICS")
        print("=" * 70)
        
        if agents:
            save_message_logs(mts, agents, "fipa_acl_message_logs.txt")
            generate_message_statistics(agents)
        
        print("\n" + "=" * 70)
        print("LAB 4 COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nDeliverables generated:")
        print("1. Agent Communication Code (this file)")
        print("2. Message Logs (fipa_acl_message_logs.txt)")
        
    finally:
        if agents:
            for agent in agents:
                try:
                    agent.stop()
                except:
                    pass
        
        if mts:
            try:
                mts.stop()
            except:
                pass