from flask import Flask
from flasgger import Swagger

from ai_recognition.infrastructure.route import ai_recognition_bp

from home_configuration.infrastructure.route import home_configuration_bp
from home_configuration.interfaces.home_controller import home_controller_bp

from iam.infrastructure.route import iam_bp

from configuration_preferences.infrastructure.route import configuration_preferences_bp

import mysql.connector

app = Flask(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="123",
  database="visualguide_db"
)
mycursor = mydb.cursor()
################### AQUI SE CREAN LAS TABLAS #############################
#mycursor.execute("CREATE DATABASE IF NOT EXISTS visualguide_db")
#mycursor.execute("SHOW DATABASES")
#mycursor.execute("DROP TABLE homes")
mycursor.execute("CREATE TABLE IF NOT EXISTS homes (id INT AUTO_INCREMENT PRIMARY KEY, owner_id INT, date DATETIME, map VARCHAR(255))")
#######################################################################################

app.register_blueprint(ai_recognition_bp, url_prefix="/api/v1/ai-recognition")

app.register_blueprint(home_configuration_bp, url_prefix="/api/v1/home-configuration")
app.register_blueprint(home_controller_bp, url_prefix="/api/v1/home-controller")

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