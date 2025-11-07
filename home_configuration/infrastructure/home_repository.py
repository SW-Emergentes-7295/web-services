from home_configuration.domain.home import Home
from datetime import datetime
import mysql.connector

class HomeRepository:
    
    def __init__(self):
        self.mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",
        database="visualguide_db"
        )
        pass

    def createHouse(self, owner_id: int, date: datetime, map:str):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO homes (owner_id, date, map) VALUES (%s, %s, %s)"
        val = (owner_id, date, map)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return Home(mycursor.lastrowid, owner_id, date, map)