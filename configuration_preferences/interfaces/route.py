from flask import Blueprint, request, jsonify
from flasgger import swag_from
import random
import string

from shared.infrastructure.database import db

configuration_preferences_bp = Blueprint('configuration_preferences', __name__)

# ---------------------------------------------
#  GENERATE LINK
# ---------------------------------------------
@configuration_preferences_bp.route("/generate-link", methods=["POST"])
@swag_from({
    'tags': ['Link'],
    'description': 'Genera un código de vinculación único para el usuario ciego si no existe ya.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'blind_user_id': {'type': 'string'}
                },
                'required': ['blind_user_id']
            }
        }
    ],
    'responses': {
        200: {'description': 'Código generado exitosamente'},
        400: {'description': 'Faltan parámetros o el código ya existe'}
    }
})
def generate_link():
    data = request.get_json()
    blind_user_id = data.get("blind_user_id")

    if not blind_user_id:
        return jsonify({"error": "blind_user_id es obligatorio"}), 400

    conn = db.get_database()
    cur = conn.cursor(dictionary=True)

    # Verificar si ya tiene un link
    cur.execute("SELECT link_code FROM links WHERE blind_user_id = %s", (blind_user_id,))
    existing = cur.fetchone()

    if existing:
        cur.close()
        return jsonify({
            "message": "Ya existe un código generado para este usuario.",
            "link_code": existing["link_code"]
        }), 200

    # Generar código
    link_code = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    cur.execute(
        "INSERT INTO links (blind_user_id, link_code) VALUES (%s, %s)",
        (blind_user_id, link_code)
    )
    db.commit()
    cur.close()

    return jsonify({
        "message": "Código generado exitosamente.",
        "blind_user_id": blind_user_id,
        "link_code": link_code
    }), 200


# ---------------------------------------------
#  GET ALL LINKS
# ---------------------------------------------
@configuration_preferences_bp.route("/links", methods=["GET"])
@swag_from({
    'tags': ['Link'],
    'description': 'Obtiene todos los códigos de vinculación generados.',
    'responses': {200: {'description': 'Lista de links generados'}}
})
def get_all_links():
    conn = db.get_database()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT blind_user_id, link_code FROM links")
    rows = cur.fetchall()

    cur.close()
    return jsonify(rows), 200


# ---------------------------------------------
#  GET LINK BY USER
# ---------------------------------------------
@configuration_preferences_bp.route("/link/<blind_user_id>", methods=["GET"])
@swag_from({
    'tags': ['Link'],
    'description': 'Obtiene el código de vinculación de un usuario específico.',
    'responses': {200: {'description': 'Código encontrado'}, 404: {'description': 'No encontrado'}}
})
def get_link_by_user(blind_user_id):
    conn = db.get_database()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT link_code FROM links WHERE blind_user_id = %s", (blind_user_id,))
    row = cur.fetchone()

    cur.close()

    if not row:
        return jsonify({"error": "No existe código para este usuario"}), 404

    return jsonify({"blind_user_id": blind_user_id, "link_code": row["link_code"]}), 200


# ---------------------------------------------
#  ADD TRIP
# ---------------------------------------------
@configuration_preferences_bp.route("/trip", methods=["POST"])
@swag_from({
    'tags': ['Trip History'],
    'description': 'Registra un nuevo viaje (trip history)',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'titulo': {'type': 'string'},
                    'fecha': {'type': 'string'},
                    'hora': {'type': 'string'},
                    'lugar': {'type': 'string'}
                },
                'required': ['titulo', 'fecha', 'hora', 'lugar']
            }
        }
    ],
    'responses': {200: {'description': 'Trip agregado exitosamente'}}
})
def add_trip():
    data = request.get_json()

    conn = db.get_database()
    cur = conn.cursor()

    # Crear tabla si no existe
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trip_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            fecha VARCHAR(255) NOT NULL,
            hora VARCHAR(255) NOT NULL,
            lugar VARCHAR(255) NOT NULL
        )
    """)

    cur.execute("""
        INSERT INTO trip_history (titulo, fecha, hora, lugar)
        VALUES (%s, %s, %s, %s)
    """, (data["titulo"], data["fecha"], data["hora"], data["lugar"]))

    db.commit()
    cur.close()

    return jsonify({"message": "Nuevo trip agregado exitosamente."}), 200


# ---------------------------------------------
#  GET TRIPS
# ---------------------------------------------
@configuration_preferences_bp.route("/trips", methods=["GET"])
@swag_from({
    'tags': ['Trip History'],
    'description': 'Obtiene todos los viajes registrados (trip history).',
    'responses': {200: {'description': 'Lista de trips'}}
})
def get_trips():

    try:
        conn = db.get_database()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT titulo, fecha, hora, lugar FROM trip_history")
        rows = cur.fetchall()
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
