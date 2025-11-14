from flask import Blueprint, request, jsonify
from flasgger import swag_from

from ai_recognition.infrastructure.ai.gemini_client import GeminiClient

ai_recognition_bp = Blueprint('ai_recognition', __name__)

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