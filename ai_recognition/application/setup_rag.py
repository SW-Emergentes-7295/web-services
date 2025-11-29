import cv2
import os
import numpy as np
import logging
from datetime import datetime
import shutil
import json
from ai_recognition.application.detect_objects import DetectObjectsUseCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SetupRAG:

    # Rutas
    RAG_BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'rag')
    )
    detect_objects_use_case = DetectObjectsUseCase()
    
    def __init__(self):
        pass

    def reset_user_rag(self, user_id):
        # Reinicia el sistema RAG del usuario (elimina datos anteriores)
        user_dir = os.path.join(self.RAG_BASE_DIR, str(user_id))
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        os.makedirs(user_dir, exist_ok=True)
        user_images_dir = os.path.join(user_dir, 'images')
        os.makedirs(user_images_dir, exist_ok=True)
        return user_dir, user_images_dir
    
    def save_user_index(self, user_id, index_data):
        user_dir = os.path.join(self.RAG_BASE_DIR, str(user_id))
        index_path = os.path.join(user_dir, 'index.json')
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=4)

    def setup(self, user_id, images):
        user_dir, user_images_dir = self.reset_user_rag(user_id)  # Reinicia el RAG del usuario

        rag_index = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'total_images': len(images),
            'results': []
        }

        results = []

        for idx, file in enumerate(images, start=1):
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                filename = f"rag_img{idx}_{timestamp}_{file.filename}"
                filepath = os.path.join(user_images_dir, filename)

                # Leer los bytes de la imagen (FileStorage -> bytes)
                # reset pointer in case it's not at beginning
                try:
                    file.stream.seek(0)
                except Exception:
                    pass

                image_bytes = file.read()

                # If still empty, try to read from saved file or stream again
                if not image_bytes:
                    try:
                        file.stream.seek(0)
                        image_bytes = file.read()
                    except Exception:
                        pass

                if not image_bytes:
                    logger.warning("Empty file bytes for %s; skipping", filename)
                    continue

                # Guardar en disco usando los bytes leídos (evita problemas con file.save después de file.read)
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)

                # Decodificar la imagen desde los bytes
                nparr = np.frombuffer(image_bytes, dtype=np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Fallback: si imdecode falla, intentar cv2.imread del archivo guardado
                if img is None:
                    img = cv2.imread(filepath)

                if img is None:
                    logger.warning("Failed to decode image %s, skipping", filename)
                    continue

                image_height, image_width = img.shape[:2]

                # Llamada a la detección con (bytes, width, height)
                detected_objects = self.detect_objects_use_case.execute(
                    image_bytes,
                    image_width,
                    image_height
                )

                img_classes = []
                for obj in detected_objects:
                    if obj.label not in img_classes:
                        img_classes.append(obj.label)

                results.append({
                    'image_filename': filename,
                    'classes': img_classes
                })                
            except Exception as e:
                logger.exception("Error processing image %s: %s", getattr(file, 'filename', 'unknown'), e)
                continue

        rag_index['results'] = results
        self.save_user_index(user_id, rag_index)
        return results