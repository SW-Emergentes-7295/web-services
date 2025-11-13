from flask import Flask
from flasgger import Swagger

from ai_recognition.infrastructure.route import ai_recognition_bp

from home_configuration.infrastructure.route import home_configuration_bp
from home_configuration.interfaces.home_controller import home_controller_bp
from home_configuration.interfaces.room_controller import room_controller_bp
from home_configuration.interfaces.path_controller import path_controller_bp

from iam.infrastructure.route import iam_bp

from configuration_preferences.infrastructure.route import configuration_preferences_bp

import mysql.connector

app = Flask(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="acd134cd34",
  database="visualguide_db"
)
mycursor = mydb.cursor()
################### AQUI SE CREAN LAS TABLAS #############################
#mycursor.execute("DROP DATABASE IF EXISTS visualguide_db")
mycursor.execute("CREATE DATABASE IF NOT EXISTS visualguide_db")
#mycursor.execute("SHOW DATABASES")
#mycursor.execute("DROP TABLE homes")
mycursor.execute("CREATE TABLE IF NOT EXISTS homes (id INT AUTO_INCREMENT PRIMARY KEY, owner_id INT, date DATETIME, map VARCHAR(255))")
mycursor.execute("CREATE TABLE IF NOT EXISTS rooms (id INT AUTO_INCREMENT PRIMARY KEY, home_id INT, width FLOAT, height FLOAT, depth FLOAT)")
mycursor.execute("CREATE TABLE IF NOT EXISTS paths (id INT AUTO_INCREMENT PRIMARY KEY, home_id INT, lenght FLOAT)")
mycursor.execute("CREATE TABLE IF NOT EXISTS path_rooms (path_id INT, room_id INT, PRIMARY KEY (path_id, room_id), FOREIGN KEY (path_id) REFERENCES paths(id), FOREIGN KEY (room_id) REFERENCES rooms(id))")
mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, full_name VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL UNIQUE, phone VARCHAR(20), password_hash VARCHAR(255) NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
#######################################################################################

app.register_blueprint(ai_recognition_bp, url_prefix="/api/v1/ai-recognition")

app.register_blueprint(home_configuration_bp, url_prefix="/api/v1/home-configuration")
app.register_blueprint(home_controller_bp, url_prefix="/api/v1/home-controller")
app.register_blueprint(room_controller_bp, url_prefix="/api/v1/room-controller")
app.register_blueprint(path_controller_bp, url_prefix="/api/v1/path-controller")

app.register_blueprint(iam_bp, url_prefix="/api/v1/iam")
app.register_blueprint(configuration_preferences_bp, url_prefix="/api/v1/configuration-preferences")

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "VisualGuide API",
        "description": "API Restful for managing the VisualGuide system.",
        "version": "1.0.0",
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    }}
)

@app.route("/routes")
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return {"routes": routes}


if __name__ == "__main__":
    app.run(port=8000, debug=True)
    #app.run(host="0.0.0.0", port=8000, debug=True)