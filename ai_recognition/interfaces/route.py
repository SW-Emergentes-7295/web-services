from flask import Blueprint, request, jsonify
from flasgger import swag_from
from werkzeug.utils import secure_filename
import os
import json
import time

from ai_recognition.infrastructure.ai.gemini_client import GeminiClient
from ai_recognition.application.detect_objects import DetectObjectsUseCase
from ai_recognition.application.generate_navigation import GenerateNavigationUseCase
from ai_recognition.application.setup_rag import SetupRAG

ai_recognition_bp = Blueprint('ai_recognition', __name__)

detect_objects_use_case = DetectObjectsUseCase()
generate_navigation_use_case = GenerateNavigationUseCase()
setup_rag_use_case = SetupRAG()

# Cliente de Gemini global para mantener historial
gemini_client = GeminiClient()


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
    """Endpoint simple para comandos de voz sin contexto espacial (legacy)"""
    try:
        body = request.get_json()

        print(f"Received body command-voice: {body}")

        if 'command' not in body:
            return jsonify({"error": "Missing 'command' in request body"}), 400
        
        command = body['command']

        response = gemini_client.generate_response(command)

        return {"response": response, "status": "Command processed"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_recognition_bp.route("/assistant/process", methods=["POST"])
@swag_from({
    "tags": ["AI Recognition - Assistant"],
    "summary": "Procesa comandos con contexto espacial completo",
    "consumes": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "user_command": {"type": "string", "example": "Llévame a la cocina"},
                    "spatial_context": {
                        "type": "object",
                        "properties": {
                            "detected_objects": {"type": "array"},
                            "current_location": {"type": "string"},
                            "target_room": {"type": "string"}
                        }
                    },
                    "conversation_history": {"type": "array"},
                    "session_id": {"type": "string", "example": "user_123"}
                },
                "required": ["user_command", "spatial_context"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Comando procesado con IA",
            "schema": {
                "type": "object",
                "properties": {
                    "response_text": {"type": "string"},
                    "action": {"type": "string"},
                    "navigation_step": {"type": "object"},
                    "priority": {"type": "string"},
                    "should_speak_immediately": {"type": "boolean"},
                    "target_room": {"type": "string"}
                }
            }
        }
    }
})
def assistant_process():
    """
    Nuevo endpoint principal para el asistente visual con IA
    Utiliza few-shot prompting con Gemini
    """
    try:
        body = request.get_json()
        
        # Extraer datos
        user_command = body.get('user_command', '')
        spatial_context = body.get('spatial_context', {})
        conversation_history = body.get('conversation_history', [])
        session_id = body.get('session_id', 'default')
        
        detected_objects = spatial_context.get('detected_objects', [])
        current_location = spatial_context.get('current_location', 'unknown')
        target_room = spatial_context.get('target_room')
        
        print(f"🎤 [Assistant] Processing command: {user_command}")
        print(f"📍 [Assistant] Location: {current_location} -> {target_room}")
        print(f"🔍 [Assistant] Objects detected: {len(detected_objects)}")
        
        # Generar respuesta con Gemini usando contexto completo
        result = gemini_client.generate_visual_assistant_response(
            user_command=user_command,
            detected_objects=detected_objects,
            current_location=current_location,
            target_room=target_room,
            conversation_history=conversation_history,
            session_id=session_id
        )
        
        print(f"✅ [Assistant] Response: {result.get('response_text', '')[:100]}...")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in assistant_process: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "response_text": "Lo siento, tuve un problema procesando tu comando.",
            "action": "inform",
            "priority": "low",
            "should_speak_immediately": True,
            "error": str(e)
        }), 500


@ai_recognition_bp.route("/assistant/alert", methods=["POST"])
@swag_from({
    "tags": ["AI Recognition - Assistant"],
    "summary": "Genera alertas proactivas para objetos detectados",
    "consumes": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "object": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "distance": {"type": "number"},
                            "position": {"type": "string"}
                        }
                    },
                    "priority": {"type": "string", "example": "high"}
                },
                "required": ["object"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Alerta generada",
            "schema": {
                "type": "object",
                "properties": {
                    "alert_text": {"type": "string"},
                    "object": {"type": "object"},
                    "priority": {"type": "string"},
                    "should_speak_immediately": {"type": "boolean"}
                }
            }
        }
    }
})
def assistant_alert():
    """
    Genera alertas proactivas breves para objetos peligrosos
    """
    try:
        body = request.get_json()
        
        detected_object = body.get('object', {})
        priority = body.get('priority', 'medium')
        
        print(f"🚨 [Alert] Generating alert for: {detected_object.get('label')} at {detected_object.get('distance')}m")
        
        # Generar alerta con Gemini
        result = gemini_client.generate_proactive_alert(
            detected_object=detected_object,
            priority=priority
        )
        
        print(f"✅ [Alert] Generated: {result.get('alert_text')}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error generating alert: {str(e)}")
        
        # Fallback
        obj = body.get('object', {})
        fallback_alert = f"Atención: {obj.get('label', 'objeto')} a {obj.get('distance', 0):.1f} metros"
        
        return jsonify({
            "alert_text": fallback_alert,
            "object": obj,
            "priority": "medium",
            "should_speak_immediately": True
        }), 200


@ai_recognition_bp.route("/assistant/clear-history", methods=["POST"])
@swag_from({
    "tags": ["AI Recognition - Assistant"],
    "summary": "Limpia el historial de conversación",
    "consumes": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "schema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "example": "user_123"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Historial limpiado"}
    }
})
def clear_assistant_history():
    """Limpia el historial de conversación de una sesión"""
    try:
        body = request.get_json() or {}
        session_id = body.get('session_id', 'default')
        
        gemini_client.clear_history(session_id)
        
        print(f"🗑️ [Assistant] History cleared for session: {session_id}")
        
        return jsonify({
            "success": True,
            "message": "Historial limpiado"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_recognition_bp.route("/process-command", methods=["POST"])
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
                    "command": {"type": "string"},
                    "spatial_context": {"type": "object"},
                    "current_location": {"type": "string"},
                    "target_room": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Command processed with spatial context",
            "schema": {
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        }
    }
})
def process_command():
    """Endpoint legacy - redirigir a usar /assistant/process"""
    try:
        body = request.get_json()
        
        command = body.get('command', '')
        spatial_context = body.get('spatial_context', {})
        current_location = body.get('current_location', 'unknown')
        target_room = body.get('target_room')
        
        print(f"🎤 Processing command: {command}")
        print(f"📍 Location: {current_location} -> {target_room}")
        print(f"🔍 Nearby objects: {len(spatial_context.get('nearby_objects', []))}")
        
        # Construir prompt con contexto espacial
        prompt = _build_spatial_prompt(
            command=command,
            spatial_context=spatial_context,
            current_location=current_location,
            target_room=target_room
        )
        
        # Enviar a Gemini
        response = gemini_client.generate_response(prompt)
        
        print(f"✅ Response generated: {response[:100]}...")
        
        return jsonify({
            "response": response,
            "status": "success"
        }), 200
        
    except Exception as e:
        print(f"❌ Error in process_command: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def _build_spatial_prompt(command, spatial_context, current_location, target_room):
    """Construye un prompt enriquecido con contexto espacial (legacy)"""
    
    nearby_objects = spatial_context.get('nearby_objects', [])
    
    objects_desc = ""
    if nearby_objects:
        objects_desc = "Objetos detectados cercanos:\n"
        for obj in nearby_objects[:5]:
            label = obj.get('label', 'objeto')
            distance = obj.get('distance', '?')
            position = obj.get('position', 'al frente')
            objects_desc += f"- {label} a {distance}m {position}\n"
    
    prompt = f"""Eres un asistente visual para personas con discapacidad visual. Tu objetivo es ayudarles a navegar de forma segura en su hogar.

Contexto actual:
- Ubicación: {current_location}
{f'- Destino: {target_room}' if target_room else ''}

{objects_desc}

Comando del usuario: "{command}"

Instrucciones:
1. Responde en español de forma clara y concisa
2. Si hay obstáculos cercanos (< 1.5m), advierte sobre ellos primero
3. Da instrucciones de navegación paso a paso
4. Usa referencias espaciales simples (izquierda, derecha, adelante)
5. Menciona distancias aproximadas cuando sea relevante

Tu respuesta:"""

    return prompt


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
        start_time = time.time()
        
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        image_width = float(request.form.get('image_width', 1920))
        image_height = float(request.form.get('image_height', 1080))
        
        print(f"📸 Detecting objects - Image: {image_file.filename}, Size: {image_width}x{image_height}")
        
        image_bytes = image_file.read()
        
        detected_objects = detect_objects_use_case.execute(
            image_bytes,
            image_width,
            image_height
        )

        # RAG logic
        user_has_rag = False
        user_id = request.form.get('user_id', None)
        user_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'rag', str(user_id)))
        index_path = os.path.join(user_dir, 'index.json')

        confirmed_objects = []
        confidence_threshold = 0.5
        user_index = None
        
        if os.path.exists(index_path):
            user_has_rag = True
            with open(index_path, 'r') as f:
                user_index = json.load(f)

        if user_has_rag:
            classes = ['Cama','Estanteria','Mesa','Refrigerador','Silla','Sofa/Sillon', 'Televisor']
            class_frequency = {cls: 0 for cls in classes}

            for cls in classes:
                for result in user_index['results']:
                    if cls in result['classes']:
                        class_frequency[cls] += 1

            for obj in detected_objects:
                confidence_threshold -= class_frequency.get(obj.label, 0) * 0.05
                if confidence_threshold < 0.25:
                    confidence_threshold = 0.25

                if obj.confidence > confidence_threshold:
                    confirmed_objects.append(obj)
            
            detections = [obj.to_dict() for obj in confirmed_objects]
        else:
            for obj in detected_objects:
                if obj.confidence > confidence_threshold:
                    confirmed_objects.append(obj)
            detections = [obj.to_dict() for obj in confirmed_objects]

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
                    "current_location": {"type": "string", "example": "living_room"},
                    "target_room": {"type": "string", "example": "kitchen"},
                    "nearby_objects": {"type": "array", "items": {"type": "object"}}
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
    """
    Genera instrucciones de navegación usando Gemini
    """
    try:
        body = request.get_json()
        
        print(f"📍 Generating navigation: {body.get('current_location')} -> {body.get('target_room')}")
        
        required_fields = ['current_location', 'target_room', 'nearby_objects']
        for field in required_fields:
            if field not in body:
                return jsonify({"error": f"Missing '{field}' in request body"}), 400
        
        # Usar Gemini para generar instrucción inteligente
        instruction_dict = gemini_client.generate_navigation_instruction(
            current_location=body['current_location'],
            target_room=body['target_room'],
            nearby_objects=body['nearby_objects']
        )
        
        # Agregar timestamp
        from datetime import datetime
        instruction_dict['timestamp'] = datetime.now().isoformat()
        
        print(f"✅ Generated: {instruction_dict.get('action')} - {instruction_dict.get('description')}")
        
        return jsonify(instruction_dict), 200
        
    except Exception as e:
        print(f"❌ Error in navigation_instructions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@ai_recognition_bp.route('/setup-rag', methods=['POST'])
@swag_from({
    'tags': ['AI Recognition'],
    'summary': 'Configurar imágenes de referencia para el RAG por usuario',
    'description': 'Envía un conjunto de imágenes de referencia para un usuario específico.',
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
        'required': True
    }, {
        'name': 'image_livingroom2',
        'in': 'formData',
        'type': 'file',
        'required': True
    }, {
        'name': 'image_bedroom1',
        'in': 'formData',
        'type': 'file',
        'required': True
    }, {
        'name': 'image_bedroom2',
        'in': 'formData',
        'type': 'file',
        'required': True
    }, {
        'name': 'image_kitchen',
        'in': 'formData',
        'type': 'file',
        'required': True
    }, {
        'name': 'image_dinning_room',
        'in': 'formData',
        'type': 'file',
        'required': True
    }, {
        'name': 'image_bathroom',
        'in': 'formData',
        'type': 'file',
        'required': True
    }],
    'responses': {
        200: {
            'description': 'Sistema RAG configurado',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'results': {'type': 'array'}
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