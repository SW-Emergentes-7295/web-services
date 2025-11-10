from flask import Blueprint, request, jsonify
from flasgger import swag_from
from home_configuration.application.path_command_service import PathCommandService
from home_configuration.application.path_query_service import PathQueryService
from home_configuration.infrastructure.path_repository import PathRepository
from home_configuration.infrastructure.home_repository import HomeRepository
from home_configuration.infrastructure.room_repository import RoomRepository

path_repository = PathRepository()
home_repository = HomeRepository()
room_repository = RoomRepository()
path_command_service = PathCommandService(path_repository)
path_query_service = PathQueryService(path_repository)
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
                    },
                    "rooms_ids": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        },
                        "example": [1, 2, 3]
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
    if home_repository.getHomeById(data.get("home_id")) is None:
        return jsonify({"message": f"Home with id {data.get("home_id")} doesnt exists"}), 400
    for room_id in data.get("rooms_ids", []):
        if room_repository.getRoomById(room_id) is None:
            return jsonify({"message": f"Room with id {room_id} doesnt exists"}), 400
    path = path_command_service.create_path(data.get("home_id"), data.get("lenght"), data.get("rooms_ids"))
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
    if path_query_service.get_path_by_id(id) is None:
        return jsonify({"message": "Path not found"}), 404
    path = path_command_service.update_path(id, data.get("lenght"))
    return jsonify(path.to_type_value()), 200
    

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
    if path_query_service.get_path_by_id(id) is None:
        return jsonify({"message": "Path not found"}), 404
    result = path_command_service.delete_path(id)
    return jsonify({"message": "Path deleted successfully"}), 200