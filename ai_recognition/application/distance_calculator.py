# ai_recognition/domain/services/distance_calculator.py
class DistanceCalculator:
    """Calcula distancias basadas en el tamaño del objeto en la imagen"""
    
    # Alturas promedio de objetos en metros
    OBJECT_HEIGHTS = {
        'chair': 0.9,
        'table': 0.75,
        'door': 2.0,
        'person': 1.7,
        'sofa': 0.85,
        'bed': 0.6,
        'shelf': 1.8,
        'counter': 0.9,
        'cabinet': 0.9,
        'refrigerator': 1.7,
        'stove': 0.9,
        'sink': 0.4,
    }
    
    def __init__(self, focal_length: float = 800.0):
        self.focal_length = focal_length
    
    def calculate_distance(
        self, 
        bbox_height_pixels: float, 
        object_label: str
    ) -> float:
        """
        Calcula distancia usando la fórmula:
        distancia = (altura_real × focal_length) / altura_en_píxeles
        """
        real_height = self.OBJECT_HEIGHTS.get(object_label.lower(), 1.0)
        
        if bbox_height_pixels > 0:
            distance = (real_height * self.focal_length) / bbox_height_pixels
            return round(distance, 2)
        
        return 5.0  # Distancia por defecto
    
    def determine_position(self, center_x: float) -> str:
        """Determina posición del objeto (left/center/right)"""
        if center_x < 0.33:
            return "left"
        elif center_x > 0.66:
            return "right"
        else:
            return "center"