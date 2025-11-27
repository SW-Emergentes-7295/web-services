# ai_recognition/infrastructure/ai/yolo_client.py
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Tuple
import os

class YOLOClient:
    """Cliente para detección de objetos con YOLO"""
    
    def __init__(self, model_path: str = "shared/model/best.pt"):
        """Inicializa el modelo YOLO"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        self.model = YOLO(model_path)
        print(f"✅ YOLO model loaded from {model_path}")
    
    def detect_objects(
        self, 
        image_bytes: bytes,
        confidence_threshold: float = 0.5
    ) -> List[dict]:
        """
        Detecta objetos en una imagen
        
        Returns:
            Lista de diccionarios con detecciones:
            [
                {
                    'label': str,
                    'confidence': float,
                    'bbox': [x1, y1, x2, y2]  # Coordenadas en píxeles
                }
            ]
        """
        # Convertir bytes a imagen
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")
        
        # Realizar detección
        results = self.model(img, conf=confidence_threshold)
        
        detections = []
        for result in results[0].boxes:
            x1, y1, x2, y2 = result.xyxy[0].tolist()
            conf = result.conf[0].item()
            cls = int(result.cls[0].item())
            label = self.model.names[cls]
            
            detections.append({
                'label': label,
                'confidence': conf,
                'bbox': [x1, y1, x2, y2]
            })
        
        return detections
    
    def get_image_dimensions(self, image_bytes: bytes) -> Tuple[int, int]:
        """Obtiene las dimensiones de la imagen"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Could not decode image")
        
        height, width = img.shape[:2]
        return width, height