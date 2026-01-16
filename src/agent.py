from typing import Optional, List
import json
import random
import re

class BaselinePurpleAgent:
    """Baseline purple agent that attempts to solve the Rooms puzzle."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset agent state for new episode."""
        self.observation_steps = 0
        self.has_committed = False
        self.known_exit: Optional[int] = None
        self.current_keys = 0
        self.rooms_inspected = [0] * 8
        self.current_room = 0

    def parse_observation(self, prompt: str) -> dict:
        """Parse observation from green agent's prompt text."""
        obs = {}
        
        # Helper to extract value safely
        def extract(pattern, text, type_conv=str):
            match = re.search(pattern, text)
            if match:
                try:
                    return type_conv(match.group(1))
                except (ValueError, SyntaxError):
                    return None
            return None

        # Extract basic state
        obs['current_room'] = extract(r"Current Room:\s*(\d+)", prompt, int)
        self.current_room = obs.get('current_room', 0)

        phase_str = extract(r"Phase:\s*(\w+)", prompt)
        if phase_str:
            obs['phase'] = phase_str
            if "Execution" in phase_str:
                self.has_committed = True

        obs['keys_held'] = extract(r"Keys Held:\s*(\d+)", prompt, int)
        if obs['keys_held'] is not None:
            self.current_keys = obs['keys_held']

        visited_str = extract(r"Rooms Visited:\s*(\[.*?\])", prompt)
        if visited_str:
            obs['rooms_visited'] = eval(visited_str)

        inspected_str = extract(r"Rooms Inspected:\s*(\[.*?\])", prompt)
        if inspected_str:
            self.rooms_inspected = eval(inspected_str)
            obs['rooms_inspected'] = self.rooms_inspected

        exit_str = extract(r"Is Exit:\s*(\[.*?\])", prompt)
        if exit_str:
            exit_list = eval(exit_str)
            for i, val in enumerate(exit_list):
                if val == 1:
                    self.known_exit = i
                    obs['exit_room'] = i

        return obs
    
    def select_action(self, prompt: str) -> dict:
        """Select next action based on observation."""
        obs = self.parse_observation(prompt)
        
        if "Step 0" in prompt and "Step 0" not in str(self.observation_steps):
             pass

        if not self.has_committed:
            self.observation_steps += 1
            if self.observation_steps > 4: 
                return {"command": "COMMIT"}
            
            if self.rooms_inspected[self.current_room] == 0:
                 pass
            
            target = random.randint(0, 7)
            if target != self.current_room:
                return {"command": "MOVE", "target_room": target}
            return {"command": "MOVE", "target_room": (self.current_room + 1) % 8}
        
        else:
            if self.known_exit is not None and self.current_room == self.known_exit:
                return {"command": "INSPECT"} 
            if self.known_exit is not None:
                return {"command": "MOVE", "target_room": self.known_exit}
            if self.rooms_inspected[self.current_room] == 0:
                return {"command": "INSPECT"}
            
            target = (self.current_room + 1) % 8
            return {"command": "MOVE", "target_room": target}
    
    def format_action(self, action: dict) -> str:
        """Format action as JSON string."""
        return json.dumps(action)