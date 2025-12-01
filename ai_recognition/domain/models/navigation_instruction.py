from dataclasses import dataclass
from datetime import datetime

@dataclass
class NavigationInstruction:
    action: str  # walk_forward, turn_left, turn_right, stop
    description: str
    distance: float
    target_room: str
    obstacles: list
    priority: str  # high, medium, low
    timestamp: datetime
    
    def to_dict(self):
        return {
            "action": self.action,
            "description": self.description,
            "distance": self.distance,
            "targetRoom": self.target_room,
            "obstacles": [obs.to_dict() if hasattr(obs, 'to_dict') else obs for obs in self.obstacles],
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat()
        }