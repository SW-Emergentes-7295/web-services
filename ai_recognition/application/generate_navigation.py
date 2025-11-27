# ai_recognition/application/generate_navigation.py
from typing import List
from ai_recognition.domain.models.detected_object import DetectedObject
from ai_recognition.domain.models.bounding_box import BoundingBox
from ai_recognition.domain.models.navigation_instruction import NavigationInstruction
from ai_recognition.application.navigation_service import NavigationService
import datetime

class GenerateNavigationUseCase:
    """Caso de uso para generar instrucciones de navegación"""
    
    def __init__(self):
        self.navigation_service = NavigationService()
    
    def execute(
        self,
        current_location: str,
        target_room: str,
        nearby_objects: List[dict]
    ) -> NavigationInstruction:
        """
        Genera instrucciones de navegación
        """
        # Convertir diccionarios a objetos DetectedObject
        detected_objects = []
        for obj_dict in nearby_objects:
            bbox_dict = obj_dict.get('boundingBox', {})
            bounding_box = BoundingBox(
                x=bbox_dict.get('x', 0),
                y=bbox_dict.get('y', 0),
                width=bbox_dict.get('width', 0),
                height=bbox_dict.get('height', 0)
            )
            
            detected_obj = DetectedObject(
                id=obj_dict.get('id', ''),
                label=obj_dict.get('label', ''),
                confidence=obj_dict.get('confidence', 0),
                bounding_box=bounding_box,
                distance=obj_dict.get('distance', 5.0),
                position=obj_dict.get('position', 'center'),
                timestamp=datetime.fromisoformat(obj_dict.get('timestamp', datetime.now().isoformat()))
            )
            detected_objects.append(detected_obj)
        
        # Generar instrucción
        return self.navigation_service.generate_instruction(
            current_location,
            target_room,
            detected_objects
        )