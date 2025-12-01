# ai_recognition/domain/entities/detected_object.py
from dataclasses import dataclass
from datetime import datetime

from ai_recognition.domain.models.bounding_box import BoundingBox

@dataclass
class DetectedObject:
    id: str
    label: str
    confidence: float
    bounding_box: BoundingBox
    distance: float
    position: str  # left, center, right
    timestamp: datetime
    
    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "confidence": self.confidence,
            "boundingBox": self.bounding_box.to_dict(),
            "distance": self.distance,
            "position": self.position,
            "timestamp": self.timestamp.isoformat()
        }

