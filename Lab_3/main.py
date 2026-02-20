"""
Lab 3: Goals, Events, and Reactive Behavior
Rescue Robot Simulation with Finite State Machine
"""

import time
import random
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque



class State(Enum):
    """Possible states for the rescue robot"""
    IDLE = "idle"
    SEARCHING = "searching"
    AVOIDING = "avoiding"
    RESCUING = "rescuing"
    RETURNING_HOME = "returning_home"

class Event(Enum):
    """Events that can trigger state transitions"""
    VICTIM_DETECTED = "victim_detected"
    HAZARD_DETECTED = "hazard_detected"
    HAZARD_CLEARED = "hazard_cleared"
    RESCUE_COMPLETE = "rescue_complete"
    AT_BASE = "at_base"
    SEARCH_TIMEOUT = "search_timeout"
    BATTERY_LOW = "battery_low"

@dataclass
class SensorReading:
    """Represents a sensor reading"""
    sensor_type: str  
    value: float
    location: tuple
    timestamp: float

class Goal:
    """Represents a robot goal with priority"""
    def __init__(self, name: str, priority: int, conditions: List[str]):
        self.name = name
        self.priority = priority  
        self.conditions = conditions
        self.completed = False
        self.active = False



class EventManager:
    """Manages event queue and dispatches events to subscribers"""
    
    def __init__(self):
        self.subscribers = {}
        self.event_queue = deque()
        self.running = True
    
    def subscribe(self, event_type: Event, callback):
        """Subscribe to a specific event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def publish(self, event: Event, data=None):
        """Publish an event to the queue"""
        self.event_queue.append((event, data))
        print(f"[EVENT] {event.value} published")
    
    def process_events(self):
        """Process all events in the queue"""
        while self.event_queue and self.running:
            event, data = self.event_queue.popleft()
            if event in self.subscribers:
                for callback in self.subscribers[event]:
                    callback(data)



class SensorSystem:
    """Simulates sensors that detect victims and hazards"""
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.scanning = True
        self.current_location = (0, 0)
        
    def scan_environment(self):
        """Simulate scanning the environment"""
        
        detection = random.random()
        
        if detection < 0.3:  
            victim_data = {
                'location': (
                    self.current_location[0] + random.randint(-5, 5),
                    self.current_location[1] + random.randint(-5, 5)
                ),
                'severity': random.choice(['minor', 'moderate', 'critical']),
                'id': random.randint(100, 999)
            }
            self.event_manager.publish(Event.VICTIM_DETECTED, victim_data)
            
        elif detection < 0.5:  
            hazard_data = {
                'type': random.choice(['fire', 'toxic_gas', 'structural_damage']),
                'location': self.current_location,
                'severity': random.uniform(0.5, 1.0)
            }
            self.event_manager.publish(Event.HAZARD_DETECTED, hazard_data)
    
    def update_location(self, new_location):
        """Update robot's current location"""
        self.current_location = new_location



class RobotActuators:
    """Controls robot movements and actions"""
    
    def __init__(self):
        self.position = (0, 0)
        self.battery_level = 100
        self.carrying_victim = False
        
    def move_to(self, target_location):
        """Move robot to target location"""
        distance = ((target_location[0] - self.position[0]) ** 2 + 
                   (target_location[1] - self.position[1]) ** 2) ** 0.5
        time.sleep(distance * 0.1)  
        self.position = target_location
        self.battery_level -= distance * 0.5
        print(f"[ACTUATOR] Moved to {target_location}, battery: {self.battery_level:.1f}%")
        return self.position
    
    def perform_rescue(self, victim_data):
        """Perform rescue operation"""
        print(f"[ACTUATOR] Performing rescue on victim {victim_data.get('id', 'unknown')}")
        time.sleep(2)  
        self.battery_level -= 10
        self.carrying_victim = True
        return True
    
    def return_to_base(self):
        """Return to home base"""
        print("[ACTUATOR] Returning to base")
        home = (0, 0)
        return self.move_to(home)
    
    def avoid_hazard(self, hazard_data):
        """Take evasive action from hazard"""
        print(f"[ACTUATOR] Avoiding {hazard_data.get('type', 'unknown')} hazard")
        
        escape_vector = (random.randint(-10, 10), random.randint(-10, 10))
        new_pos = (self.position[0] + escape_vector[0], 
                  self.position[1] + escape_vector[1])
        return self.move_to(new_pos)



class RescueRobotFSM:
    """Finite State Machine for rescue robot behavior"""
    
    def __init__(self, event_manager: EventManager, actuators: RobotActuators):
        self.state = State.IDLE
        self.event_manager = event_manager
        self.actuators = actuators
        self.goals = self._initialize_goals()
        self.current_victim = None
        self.hazard_active = False
        
        
        self._subscribe_to_events()
        
        print(f"[FSM] Initialized in {self.state.value} state")
    
    def _initialize_goals(self) -> Dict[str, Goal]:
        """Initialize robot goals"""
        return {
            'rescue': Goal('Rescue Victims', 3, ['victim_detected']),
            'safety': Goal('Avoid Hazards', 2, ['hazard_detected']),
            'efficiency': Goal('Return to Base', 1, ['rescue_complete', 'battery_low'])
        }
    
    def _subscribe_to_events(self):
        """Subscribe to all relevant events"""
        self.event_manager.subscribe(Event.VICTIM_DETECTED, self.on_victim_detected)
        self.event_manager.subscribe(Event.HAZARD_DETECTED, self.on_hazard_detected)
        self.event_manager.subscribe(Event.HAZARD_CLEARED, self.on_hazard_cleared)
        self.event_manager.subscribe(Event.RESCUE_COMPLETE, self.on_rescue_complete)
        self.event_manager.subscribe(Event.AT_BASE, self.on_at_base)
        self.event_manager.subscribe(Event.BATTERY_LOW, self.on_battery_low)
    
    
    
    def on_victim_detected(self, data):
        """Handle victim detection event"""
        print(f"[HANDLER] Victim detected: {data}")
        self.current_victim = data
        
        if self.state == State.SEARCHING:
            self.transition_to(State.RESCUING)
        elif self.state == State.IDLE:
            self.transition_to(State.SEARCHING)
    
    def on_hazard_detected(self, data):
        """Handle hazard detection event"""
        print(f"[HANDLER] Hazard detected: {data}")
        self.hazard_active = True
        
        
        if self.state not in [State.AVOIDING, State.RETURNING_HOME]:
            self.transition_to(State.AVOIDING, hazard_data=data)
    
    def on_hazard_cleared(self, data=None):
        """Handle hazard cleared event"""
        print("[HANDLER] Hazard cleared")
        self.hazard_active = False
        self.transition_to(State.SEARCHING)
    
    def on_rescue_complete(self, data=None):
        """Handle rescue completion event"""
        print("[HANDLER] Rescue complete")
        self.transition_to(State.RETURNING_HOME)
    
    def on_at_base(self, data=None):
        """Handle reaching base event"""
        print("[HANDLER] At base")
        self.actuators.carrying_victim = False
        self.transition_to(State.IDLE)
    
    def on_battery_low(self, data=None):
        """Handle low battery event"""
        print("[HANDLER] Battery low")
        self.transition_to(State.RETURNING_HOME)
    
    
    
    def transition_to(self, new_state: State, **kwargs):
        """Handle state transition"""
        print(f"[FSM] State transition: {self.state.value} -> {new_state.value}")
        self.state = new_state
        
        
        if new_state == State.SEARCHING:
            self.enter_searching()
        elif new_state == State.RESCUING:
            self.enter_rescuing(kwargs.get('victim_data', self.current_victim))
        elif new_state == State.AVOIDING:
            self.enter_avoiding(kwargs.get('hazard_data'))
        elif new_state == State.RETURNING_HOME:
            self.enter_returning_home()
        elif new_state == State.IDLE:
            self.enter_idle()
    
    
    
    def enter_searching(self):
        """Actions to perform when entering SEARCHING state"""
        print("[STATE] Entering SEARCHING mode")
        
        for _ in range(5):  
            if self.state == State.SEARCHING:  
                print("[ROBOT] Scanning area for victims...")
                time.sleep(1)
                
                
                if random.random() < 0.4:  
                    victim_found = {
                        'location': (
                            self.actuators.position[0] + random.randint(-3, 3),
                            self.actuators.position[1] + random.randint(-3, 3)
                        ),
                        'severity': random.choice(['minor', 'moderate', 'critical']),
                        'id': random.randint(100, 999)
                    }
                    self.event_manager.publish(Event.VICTIM_DETECTED, victim_found)
                    break
    
    def enter_rescuing(self, victim_data):
        """Actions to perform when entering RESCUING state"""
        print(f"[STATE] Entering RESCUING mode for victim at {victim_data.get('location')}")
        
        
        self.actuators.move_to(victim_data.get('location', (0, 0)))
        
        
        if self.actuators.perform_rescue(victim_data):
            
            self.event_manager.publish(Event.RESCUE_COMPLETE)
    
    def enter_avoiding(self, hazard_data):
        """Actions to perform when entering AVOIDING state"""
        print(f"[STATE] Entering AVOIDING mode for {hazard_data.get('type')} hazard")
        
        
        new_pos = self.actuators.avoid_hazard(hazard_data)
        
        
        time.sleep(2)
        if random.random() < 0.7:  
            self.event_manager.publish(Event.HAZARD_CLEARED)
    
    def enter_returning_home(self):
        """Actions to perform when entering RETURNING_HOME state"""
        print("[STATE] Entering RETURNING_HOME mode")
        
        
        if self.actuators.carrying_victim:
            print("[ROBOT] Returning to base with rescued victim")
        
        
        self.actuators.return_to_base()
        self.event_manager.publish(Event.AT_BASE)
    
    def enter_idle(self):
        """Actions to perform when entering IDLE state"""
        print("[STATE] Entering IDLE mode")
        print("[ROBOT] Waiting for new tasks...")
        self.current_victim = None



def run_simulation():
    """Main simulation loop"""
    
    print("RESCUE ROBOT SIMULATION - LAB 3: GOALS, EVENTS, AND REACTIVE BEHAVIOR")
    
    
    
    event_manager = EventManager()
    actuators = RobotActuators()
    robot_fsm = RescueRobotFSM(event_manager, actuators)
    sensors = SensorSystem(event_manager)
    
    
    simulation_steps = 10
    current_step = 0
    
    print("\n=== SIMULATION START ===")
    
    
    while current_step < simulation_steps and actuators.battery_level > 0:
        print(f"\n--- Simulation Step {current_step + 1} ---")
        
        
        sensors.update_location(actuators.position)
        
        
        sensors.scan_environment()
        
        
        event_manager.process_events()
        
        
        if actuators.battery_level < 20 and robot_fsm.state != State.RETURNING_HOME:
            event_manager.publish(Event.BATTERY_LOW)
            event_manager.process_events()
        
        
        current_step += 1
        time.sleep(1)
    
    print("\n=== SIMULATION END ===")
    print(f"Final battery level: {actuators.battery_level:.1f}%")
    print(f"Final state: {robot_fsm.state.value}")
    print(f"Victims rescued: {'Yes' if actuators.carrying_victim else 'No'}")



def generate_execution_trace():
    """Generate a detailed execution trace of the simulation"""
    
    print("EXECUTION TRACE")
    
    
    
    import io
    import sys
    
    
    old_stdout = sys.stdout
    trace_output = io.StringIO()
    sys.stdout = trace_output
    
    
    run_simulation()
    
    
    sys.stdout = old_stdout
    
    
    trace = trace_output.getvalue()
    
    
    print(trace)
    
    
    with open('execution_trace.txt', 'w') as f:
        f.write(trace)
    
    print("\n[TRACE] Execution trace saved to 'execution_trace.txt'")



if __name__ == "__main__":
    
    run_simulation()
    
    
    generate_execution_trace()
    
    
    print("LAB 3 COMPLETED SUCCESSFULLY")
    
    print("\nDeliverables generated:")
    print("1. FSM Diagram (see above text representation)")
    print("2. Python Implementation (this file)")
    print("3. Execution Trace (execution_trace.txt)")