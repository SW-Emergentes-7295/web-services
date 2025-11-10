from flask import Blueprint, request, jsonify
from flasgger import swag_from
from home_configuration.application.room_command_service import RoomCommandService
from home_configuration.application.room_query_service import RoomQueryService
from home_configuration.infrastructure.room_repository import RoomRepository
from home_configuration.infrastructure.home_repository import HomeRepository

room_repository = RoomRepository()
home_repository = HomeRepository()
room_command_service = RoomCommandService(room_repository)
room_query_service = RoomQueryService(room_repository)
room_controller_bp = Blueprint('room_controller', __name__)

@room_controller_bp.route("/room", methods=["GET"])
@swag_from({
    "tags": ["Room Controller"],
    "responses": {
        200: {
            "description": "Successful retrieval all rooms",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Rooms"
                    }
                }
            }
        }
    }
})
def get_rooms():
    data = room_query_service.get_all_rooms()
    return jsonify([room.to_type_value() for room in data]), 200

@room_controller_bp.route("/room/<int:id>", methods=["GET"])
@swag_from({
    "tags": ["Room Controller"],
        "parameters":[
        {
            "name":"id",
            "in":"path",
            "type":"integer",
            "required": True,
            "description":"ID of the room to retrieve"
        }
    ],
    "responses": {
        200: {
            "description": "Successful retrieval room",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Room"
                    }
                }
            }
        }
    }
})
def get_room_by_id(id):
    room = room_query_service.get_room_by_id(id)
    if room:
        return jsonify(room.to_type_value()), 200
    else:
        return jsonify({"message": "Room not found"}), 404
    
@room_controller_bp.route("/room", methods=["POST"])
@swag_from({
    "tags": ["Room Controller"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "home_id": {"type": "integer"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "depth": {"type": "number"}
                },
                "required": ["home_id", "width", "height", "depth"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Room created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Room Created"
                    }
                }
            }
        }
    }
})
def create_room():
    data = request.get_json()
    if home_repository.getHomeById(data.get("home_id")) is None:
        return jsonify({"message": f"Home with id {data.get("home_id")} doesnt exists"}), 400
    room = room_command_service.create_room(data.get("home_id"), data.get("width"), data.get("height"), data.get("depth"))
    return jsonify(room.to_type_value()), 201

@room_controller_bp.route("/room/<int:id>", methods=["PUT"])
@swag_from({
    "tags": ["Room Controller"],
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID of the room to update"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "depth": {"type": "number"}
                },
                "required": ["width", "height", "depth"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Room updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Room Updated"
                    }
                }
            }
        }
    }
})
def update_room(id):
    data = request.get_json()
    if room_query_service.get_room_by_id(id) is None:
        return jsonify({"message": "Room not found"}), 404
    room = room_command_service.update_room(id, data.get("width"), data.get("height"), data.get("depth"))
    return jsonify(room.to_type_value()), 200
    

@room_controller_bp.route("/room/<int:id>", methods=["DELETE"])
@swag_from({
    "tags": ["Room Controller"],
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID of the room to delete"
        }
    ],
    "responses": {
        200: {
            "description": "Room deleted successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Room Deleted"
                    }
                }
            }
        }
    }
})
def delete_room(id):
    if room_query_service.get_room_by_id(id) is None:
        return jsonify({"message": "Room not found"}), 404
    result = room_command_service.delete_room(id)
    return jsonify({"message": f"Room with id: {id} deleted successfully"}), 200