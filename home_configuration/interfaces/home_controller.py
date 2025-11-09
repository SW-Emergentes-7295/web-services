from flask import Blueprint, request, jsonify
from flasgger import swag_from
from home_configuration.application.home_command_service import HomeCommandService
from home_configuration.application.home_query_service import HomeQueryService
from home_configuration.infrastructure.home_repository import HomeRepository

home_repository = HomeRepository()
home_command_service = HomeCommandService(home_repository)
home_query_service = HomeQueryService(home_repository)
home_controller_bp = Blueprint('home_controlller', __name__)

@home_controller_bp.route("/home", methods=["GET"])
@swag_from({
    "tags": ["Home Controller"],
    "responses": {
        200: {
            "description": "Successful retrieval all homes",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Homes"
                    }
                }
            }
        }
    }

})
def get_homes():
    data = home_query_service.get_all_homes()
    return jsonify([home.to_type_value() for home in data]), 200


@home_controller_bp.route("/home/<int:id>", methods=["GET"])
@swag_from({
    "tags": ["Home Controller"],
        "parameters":[
        {
            "name":"id",
            "in":"path",
            "type":"integer",
            "required": True,
            "description":"ID of the home to retrieve"
        }
    ],
    "responses": {
        200: {
            "description": "Successful retrieval home",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Home"
                    }
                }
            }
        }
    }

})
def get_home_by_id(id):
    home = home_query_service.get_home_by_id(id)
    if home:
        return jsonify(home.to_type_value()), 200
    else:
        return jsonify({"message": "Home not found"}), 404
    

@home_controller_bp.route("/home", methods=["POST"])
@swag_from({
    "tags": ["Home Controller"],
    "parameters":[
        {
            "name":"body",
            "in":"body",
            "required": True,
            "schema":{
                "type": "object",
                "properties":{
                    "owner_id": {"type": "int", "example": 0},
                    "map": {"type": "string", "example": "1223sas"},                   
                },
                "required": ["id", "owner_id", "map"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Successful created home",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Home"
                    }
                }
            }
        }
    }

})
def create_home():
    data = request.get_json()
    home = home_command_service.create_home(data.get("owner_id"),data.get("map"))
    return jsonify(home.to_type_value()), 200


@home_controller_bp.route("/home/<int:id>", methods=["PUT"])
@swag_from({
    "tags": ["Home Controller"],
    "parameters":[
        {
            "name":"id",
            "in":"path",
            "type":"integer",
            "required": True,
            "description":"ID of the home to update"
        },
        {
            "name":"body",
            "in":"body",
            "required": True,
            "schema":{
                "type": "object",
                "properties":{
                    "owner_id": {"type": "int", "example": 0},
                    "map": {"type": "string", "example": "1223sas"},                   
                },
                "required": ["id", "owner_id", "map"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Successful updated home",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Home"
                    }
                }
            }
        }
    }

})
def update_home(id):
    data = request.get_json()
    home = home_command_service.update_home(id, data.get("owner_id"),data.get("map"))
    if home:
        return jsonify(home.to_type_value()), 200
    else:
        return jsonify({"message": "Home not found"}), 404

@home_controller_bp.route("/home/<int:id>", methods=["DELETE"])
@swag_from({
    "tags": ["Home Controller"],
    "parameters":[
        {
            "name":"id",
            "in":"path",
            "type":"integer",
            "required": True,
            "description":"ID of the home to delete"
        }
    ],
    "responses": {
        200: {
            "description": "Successful updated home",
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "example": "Home"
                    }
                }
            }
        }
    }

})
def delete_home(id):
    result = home_command_service.delete_home(id)

    if result:
        return {
            "message": f"Home with id: {id} deleted successfully"
        }
    else:
        return {
            "message": f"Error deleting home with id: {id}"
        }