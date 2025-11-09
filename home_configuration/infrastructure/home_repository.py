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

    def createHouse(self, owner_id: int, date: datetime, map:str):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO homes (owner_id, date, map) VALUES (%s, %s, %s)"
        val = (owner_id, date, map)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return Home(mycursor.lastrowid, owner_id, date, map)
    
    def updateHome(self, id: int, owner_id: int, date: datetime, map:str):
        mycursor = self.mydb.cursor()
        sql = "UPDATE homes SET owner_id = %s, date = %s, map = %s WHERE id = %s"
        val = (owner_id, date, map, id)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return Home(id, owner_id, date, map)
    
    def deleteHome(self, id: int):
        mycursor = self.mydb.cursor()
        sql = "DELETE FROM homes WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return True

    def getAllHomes(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM homes")
        myresult = mycursor.fetchall()
        homes = []
        print(myresult)
        for row in myresult:
            home = Home(row[0], row[1], row[2], row[3])
            homes.append(home)
        return homes
    
    def getHomeById(self, home_id: int):
        mycursor = self.mydb.cursor()
        sql = "SELECT * FROM homes WHERE id = %s"
        val = (home_id,)
        mycursor.execute(sql, val)
        row = mycursor.fetchone()
        if row:
            return Home(row[0], row[1], row[2], row[3])
        else:
            return None