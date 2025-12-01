import mysql.connector

class DatabaseConnection:
    
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
        )

        cursor = self.mydb.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS visualguide_db")

        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="visualguide_db",
        )

    def get_database(self):
        return self.mydb

    def get_connection(self):
        return self.mydb.cursor()
    
    def close_connection(self):
        self.mydb.close()

    def commit(self):
        self.mydb.commit()

    def create_schemas(self):
        cursor = self.mydb.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS homes (id INT AUTO_INCREMENT PRIMARY KEY, owner_id INT, date DATETIME, map VARCHAR(255))")
        cursor.execute("CREATE TABLE IF NOT EXISTS rooms (id INT AUTO_INCREMENT PRIMARY KEY, home_id INT, width FLOAT, height FLOAT, depth FLOAT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS paths (id INT AUTO_INCREMENT PRIMARY KEY, home_id INT, lenght FLOAT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS path_rooms (path_id INT, room_id INT, PRIMARY KEY (path_id, room_id), FOREIGN KEY (path_id) REFERENCES paths(id), FOREIGN KEY (room_id) REFERENCES rooms(id))")
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL UNIQUE, phone VARCHAR(20), password VARCHAR(255) NOT NULL)")
        cursor.close()

db = DatabaseConnection()