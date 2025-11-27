from flask import Blueprint, request, jsonify
from flasgger import swag_from
from werkzeug.utils import secure_filename

from ai_recognition.infrastructure.ai.gemini_client import GeminiClient
from ai_recognition.application.detect_objects import DetectObjectsUseCase
from ai_recognition.application.generate_navigation import GenerateNavigationUseCase

ai_recognition_bp = Blueprint('ai_recognition', __name__)

detect_objects_use_case = DetectObjectsUseCase()
generate_navigation_use_case = GenerateNavigationUseCase()

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
        
        # Calcular tiempo de procesamiento
        processing_time = (time.time() - start_time) * 1000
        
        # Convertir a diccionarios
        detections = [obj.to_dict() for obj in detected_objects]
        
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