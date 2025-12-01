# ai_recognition/application/detect_objects.py
from typing import List
from datetime import datetime
import uuid

from ai_recognition.infrastructure.ai.yolo_client import YOLOClient
from ai_recognition.application.distance_calculator import DistanceCalculator
from ai_recognition.domain.models.detected_object import DetectedObject, BoundingBox

class DetectObjectsUseCase:
    """Caso de uso para detectar objetos con datos espaciales"""
    
    def __init__(self):
        self.yolo_client = YOLOClient()
        self.distance_calculator = DistanceCalculator()
    
    def execute(
        self, 
        image_bytes: bytes,
        image_width: float,
        image_height: float
    ) -> List[DetectedObject]:
        """
        Detecta objetos en la imagen y calcula datos espaciales
        """
        # Detectar objetos con YOLO
        detections = self.yolo_client.detect_objects(image_bytes)
        
        detected_objects = []
        for detection in detections:
            label = detection['label']
            confidence = detection['confidence']
            bbox_pixels = detection['bbox']  # [x1, y1, x2, y2]
            
            # Normalizar bounding box
            x_norm = bbox_pixels[0] / image_width
            y_norm = bbox_pixels[1] / image_height
            width_norm = (bbox_pixels[2] - bbox_pixels[0]) / image_width
            height_norm = (bbox_pixels[3] - bbox_pixels[1]) / image_height
            
            bounding_box = BoundingBox(
                x=x_norm,
                y=y_norm,
                width=width_norm,
                height=height_norm
            )
            
            # Calcular distancia
            bbox_height_pixels = bbox_pixels[3] - bbox_pixels[1]
            distance = self.distance_calculator.calculate_distance(
                bbox_height_pixels, 
                label
            )
            
            # Determinar posición
            center_x = x_norm + width_norm / 2
            position = self.distance_calculator.determine_position(center_x)
            
            # Crear objeto detectado
            detected_obj = DetectedObject(
                id=f"{label}_{uuid.uuid4().hex[:8]}",
                label=label,
                confidence=confidence,
                bounding_box=bounding_box,
                distance=distance,
                position=position,
                timestamp=datetime.now()
            )
            
            detected_objects.append(detected_obj)
        
        # Ordenar por distancia (más cercanos primero)
        detected_objects.sort(key=lambda x: x.distance)
        
        return detected_objects