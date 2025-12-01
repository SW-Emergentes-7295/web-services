from dataclasses import dataclass

@dataclass
class BoundingBox:
    x: float  # Normalizado 0-1
    y: float
    width: float
    height: float
    
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }
