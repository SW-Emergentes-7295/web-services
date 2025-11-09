from flask import Blueprint, request, jsonify
from flasgger import swag_from
from home_configuration.application.path_command_service import PathCommandService
from home_configuration.application.path_query_service import PathQueryService
from home_configuration.infrastructure.path_repository import PathRepository

pathRepository = PathRepository()
path_command_service = PathCommandService(pathRepository)
path_query_service = PathQueryService(pathRepository)
path_controller_bp = Blueprint('path_controller', __name__)

@path_controller_bp.route("/path", methods=["GET"])
@swag_from({
    "tags": ["Path Controller"],
    "responses": {
        200: {
            "description": "Successful retrieval all paths",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Paths"
                    }
                }
            }
        }
    }
})
def get_paths():
    data = path_query_service.get_all_paths()
    return jsonify([path.to_type_value() for path in data]), 200

@path_controller_bp.route("/path/<int:id>", methods=["GET"])
@swag_from({
    "tags": ["Path Controller"],
        "parameters":[
        {
            "name":"id",
            "in":"path",
            "type":"integer",
            "required": True,
            "description":"ID of the path to retrieve"
        }
    ],
    "responses": {
        200: {
            "description": "Successful retrieval path",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Path"
                    }
                }
            }
        }
    }
})
def get_path_by_id(id):
    path = path_query_service.get_path_by_id(id)
    if path:
        return jsonify(path.to_type_value()), 200
    else:
        return jsonify({"message": "Path not found"}), 404
    
@path_controller_bp.route("/path", methods=["POST"])
@swag_from({
    "tags": ["Path Controller"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "home_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "lenght": {
                        "type": "number",
                        "format": "float",
                        "example": 1.0
                    }
                },
                "required": ["home_id", "lenght"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Path created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Path Created"
                    }
                }
            }
        }
    }
})
def create_path():
    data = request.get_json()
    path = path_command_service.create_path(data.get("home_id"), data.get("lenght"))
    return jsonify(path.to_type_value()), 201

@path_controller_bp.route("/path/<int:id>", methods=["PUT"])
@swag_from({
    "tags": ["Path Controller"],
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID of the path to update"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "lenght": {
                        "type": "number",
                        "format": "float",
                        "example": 1.0
                    }
                },
                "required": ["lenght"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Path updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Path Updated"
                    }
                }
            }
        }
    }
})
def update_path(id):
    data = request.get_json()
    path = path_command_service.update_path(id, data.get("lenght"))
    if path:
        return jsonify(path.to_type_value()), 200
    else:
        return jsonify({"message": "Path not found"}), 404
    
@path_controller_bp.route("/path/<int:id>", methods=["DELETE"])
@swag_from({
    "tags": ["Path Controller"],
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID of the path to delete"
        }
    ],
    "responses": {
        200: {
            "description": "Path deleted successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Path Deleted"
                    }
                }
            }
        }
    }
})
def delete_path(id):
    result = path_command_service.delete_path(id)
    if result:
        return jsonify({"message": "Path deleted successfully"}), 200
    else:
        return jsonify({"message": "Path not found"}), 404