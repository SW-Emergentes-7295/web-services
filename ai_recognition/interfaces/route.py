from flask import Blueprint, request, jsonify
from flasgger import swag_from
from werkzeug.utils import secure_filename
import os
import json

from ai_recognition.infrastructure.ai.gemini_client import GeminiClient
from ai_recognition.application.detect_objects import DetectObjectsUseCase
from ai_recognition.application.generate_navigation import GenerateNavigationUseCase
from ai_recognition.application.setup_rag import SetupRAG

ai_recognition_bp = Blueprint('ai_recognition', __name__)

detect_objects_use_case = DetectObjectsUseCase()
generate_navigation_use_case = GenerateNavigationUseCase()
setup_rag_use_case = SetupRAG()

@ai_recognition_bp.route("/voice-command", methods=["POST"])
@swag_from({
    "tags": ["AI Recognition"],
    "consumes": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "example": "Turn on the lights"
                    }
                },
                "required": ["command"]
            },
            "description": "Voice command text in JSON format"
        }
    ],
    "responses": {
        200: {
            "description": "Successful command processing",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "Command processed"},
                    "command": {"type": "string", "example": "Turn on the lights"}
                }
            }
        },
        400: {"description": "Invalid input"}
    }
})
def voice_command():
    try:
        body = request.get_json()

        print(f"Received body command-voice: {body}")

        if 'command' not in body:
            return jsonify({"error": "Missing 'command' in request body"}), 400
        command = body['command']

        gemini_client = GeminiClient()
        response = gemini_client.generate_response(command)

        return {"response": response, "status": "Command processed"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@ai_recognition_bp.route("/detect-objects", methods=["POST"])
@swag_from({
    "tags": ["AI Recognition"],
    "consumes": ["multipart/form-data"],
    "parameters": [
        {
            'name': 'user_id',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'ID del usuario'
        },
        {
            "name": "image",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "Image file for object detection"
        },
        {
            "name": "image_width",
            "in": "formData",
            "type": "number",
            "required": True,
            "description": "Width of the image in pixels"
        },
        {
            "name": "image_height",
            "in": "formData",
            "type": "number",
            "required": True,
            "description": "Height of the image in pixels"
        }
    ],
    "responses": {
        200: {
            "description": "Objects detected successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "detections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "label": {"type": "string"},
                                "confidence": {"type": "number"},
                                "boundingBox": {"type": "object"},
                                "distance": {"type": "number"},
                                "position": {"type": "string"},
                                "timestamp": {"type": "string"}
                            }
                        }
                    },
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "processing_time_ms": {"type": "number"},
                            "objects_count": {"type": "integer"}
                        }
                    }
                }
            }
        }
    }
})
def detect_objects():
    try:
        import time
        start_time = time.time()
        
        # Validar que se envió una imagen
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Obtener dimensiones
        image_width = float(request.form.get('image_width', 1920))
        image_height = float(request.form.get('image_height', 1080))
        
        print(f"📸 Detecting objects - Image: {image_file.filename}, Size: {image_width}x{image_height}")
        
        # Leer imagen como bytes
        image_bytes = image_file.read()
        
        # Ejecutar caso de uso
        detected_objects = detect_objects_use_case.execute(
            image_bytes,
            image_width,
            image_height
        )

        #Determina si un usuario tiene un RAG asignado
        user_has_rag = False
        user_id = request.form.get('user_id', None)
        user_dir = os.path.abspath( os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'rag', str(user_id)))
        index_path = os.path.join(user_dir, 'index.json')

        confirmed_objects = []
        confidence_threshold = 0.5
        user_index = None
        if os.path.exists(index_path):
            user_has_rag = True
            with open(index_path, 'r') as f:
                user_index = json.load(f)

        if user_has_rag:

            #Calcula la cantidad de apariciones de cada clase
            classes = ['Cama','Estanteria','Mesa','Refrigerador','Silla','Sofa/Sillon', 'Televisor']
            class_frequency = {
                'Cama': 0,
                'Estanteria': 0,
                'Mesa': 0,
                'Refrigerador': 0,
                'Silla': 0,
                'Sofa/Sillon': 0,
                'Televisor': 0
            }

            for cls in classes:
                for result in user_index['results']:
                    if cls in result['classes']:
                        class_frequency[cls] += 1
            #print(f"Class frequency in RAG: {class_frequency}")

            #Hace el RAG por cada objeto detectado
            for obj in detected_objects:
                confidence_threshold -= class_frequency.get(obj.label, 0) * 0.05  # Ajusta el umbral según la frecuencia
                if confidence_threshold < 0.25:
                    confidence_threshold = 0.25  # Establece un umbral mínimo

                if obj.confidence > confidence_threshold:
                    confirmed_objects.append(obj)
            detections = [obj.to_dict() for obj in confirmed_objects]
        else:
            # Convertir a diccionarios sin más
            for obj in detected_objects:
                if obj.confidence > confidence_threshold:
                    confirmed_objects.append(obj)
            detections = [obj.to_dict() for obj in confirmed_objects]

        # Calcular tiempo de procesamiento
        processing_time = (time.time() - start_time) * 1000

        print(f"✅ Detected {len(detections)} objects in {processing_time:.2f}ms")
        
        return jsonify({
            "detections": detections,
            "metadata": {
                "processing_time_ms": round(processing_time, 2),
                "objects_count": len(detections)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error in detect_objects: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@ai_recognition_bp.route("/navigation/instructions", methods=["POST"])
@swag_from({
    "tags": ["AI Recognition"],
    "consumes": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "current_location": {
                        "type": "string",
                        "example": "living_room"
                    },
                    "target_room": {
                        "type": "string",
                        "example": "kitchen"
                    },
                    "nearby_objects": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["current_location", "target_room", "nearby_objects"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Navigation instructions generated",
            "schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "description": {"type": "string"},
                    "distance": {"type": "number"},
                    "targetRoom": {"type": "string"},
                    "obstacles": {"type": "array"},
                    "priority": {"type": "string"},
                    "timestamp": {"type": "string"}
                }
            }
        }
    }
})
def navigation_instructions():
    try:
        body = request.get_json()
        
        print(f"📍 Generating navigation instructions: {body.get('current_location')} -> {body.get('target_room')}")
        
        # Validar campos requeridos
        required_fields = ['current_location', 'target_room', 'nearby_objects']
        for field in required_fields:
            if field not in body:
                return jsonify({"error": f"Missing '{field}' in request body"}), 400
        
        # Ejecutar caso de uso
        instruction = generate_navigation_use_case.execute(
            current_location=body['current_location'],
            target_room=body['target_room'],
            nearby_objects=body['nearby_objects']
        )
        
        print(f"✅ Generated instruction: {instruction.action} - {instruction.description}")
        
        return jsonify(instruction.to_dict()), 200
        
    except Exception as e:
        print(f"❌ Error in navigation_instructions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    

@ai_recognition_bp.route('/setup-rag', methods=['POST'])
@swag_from({
    'tags': ['AI Recognition'],
    'summary': 'Configurar imágenes de referencia para el RAG por usuario',
    'description': 'Envía un conjunto de imágenes de referencia para un usuario específico. El sistema RAG del usuario se reinicia con cada petición.',
    'consumes': ['multipart/form-data'],
    'parameters': [{
        'name': 'user_id',
        'in': 'formData',
        'type': 'string',
        'required': True,
        'description': 'ID del usuario'
    }, {
        'name': 'image_livingroom1',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': 'Imágenes de referencia (múltiples archivos)'
    }, {
        'name': 'image_livingroom2',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': 'Imágenes de referencia (múltiples archivos)'
    }, {
        'name': 'image_bedroom1',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': 'Imágenes de referencia (múltiples archivos)'
    }, {
        'name': 'image_bedroom2',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': 'Imágenes de referencia (múltiples archivos)'
    }, {
        'name': 'image_kitchen',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': 'Imágenes de referencia (múltiples archivos)'
    }, {
        'name': 'image_dinning_room',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': 'Imágenes de referencia (múltiples archivos)'
    }, {
        'name': 'image_bathroom',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': 'Imágenes de referencia (múltiples archivos)'
    }],
    'responses': {
        200: {
            'description': 'Sistema RAG configurado',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'user_id': {'type': 'string'},
                    'images_processed': {'type': 'integer'},
                    'rag_path': {'type': 'string'},
                    'message': {'type': 'string'}
                }
            }
        }
    }
})
def setup_rag():
    images = []
    images.append(request.files.get('image_livingroom1'))
    images.append(request.files.get('image_livingroom2'))
    images.append(request.files.get('image_bedroom1'))
    images.append(request.files.get('image_bedroom2'))
    images.append(request.files.get('image_kitchen'))
    images.append(request.files.get('image_dinning_room'))
    images.append(request.files.get('image_bathroom'))

    results = setup_rag_use_case.setup(request.form['user_id'], images)
    return jsonify({
        "results": results,
        "success": True,
    }), 200