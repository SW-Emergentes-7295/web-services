# ai_recognition/domain/services/navigation_service.py
from typing import List
from ai_recognition.domain.models.detected_object import DetectedObject
from ai_recognition.domain.models.navigation_instruction import NavigationInstruction
from datetime import datetime

class NavigationService:
    """Servicio para generar instrucciones de navegación"""
    
    def generate_instruction(
        self,
        current_location: str,
        target_room: str,
        nearby_objects: List[DetectedObject]
    ) -> NavigationInstruction:
        """Genera instrucciones de navegación basadas en el contexto"""
        
        # Filtrar obstáculos críticos (< 1.5m)
        critical_obstacles = [obj for obj in nearby_objects if obj.distance < 1.5]
        
        # Si hay obstáculos críticos
        if critical_obstacles:
            nearest = min(critical_obstacles, key=lambda x: x.distance)
            
            if nearest.distance < 0.5:
                return NavigationInstruction(
                    action="stop",
                    description=f"Detente. Hay un {nearest.label} muy cerca a {nearest.distance:.1f} metros",
                    distance=nearest.distance,
                    target_room=target_room,
                    obstacles=critical_obstacles,
                    priority="high",
                    timestamp=datetime.now()
                )
            elif nearest.position == "center":
                return NavigationInstruction(
                    action="turn_left",
                    description=f"Gira a la izquierda para evitar {nearest.label} a {nearest.distance:.1f} metros",
                    distance=nearest.distance,
                    target_room=target_room,
                    obstacles=critical_obstacles,
                    priority="high",
                    timestamp=datetime.now()
                )
        
        # Si no hay obstáculos, guiar hacia el objetivo
        room_distance = self._estimate_room_distance(current_location, target_room)
        
        return NavigationInstruction(
            action="walk_forward",
            description=f"Camina hacia adelante. La {target_room} está aproximadamente a {room_distance:.1f} metros",
            distance=room_distance,
            target_room=target_room,
            obstacles=[],
            priority="medium",
            timestamp=datetime.now()
        )
    
    def _estimate_room_distance(self, current: str, target: str) -> float:
        """Estima distancia entre habitaciones"""
        distances = {
            ('living_room', 'kitchen'): 5.0,
            ('kitchen', 'living_room'): 5.0,
            ('living_room', 'bedroom'): 8.0,
            ('bedroom', 'living_room'): 8.0,
            ('bedroom', 'bathroom'): 3.0,
            ('bathroom', 'bedroom'): 3.0,
            ('kitchen', 'bathroom'): 7.0,
            ('bathroom', 'kitchen'): 7.0,
        }
        return distances.get((current, target), 10.0)