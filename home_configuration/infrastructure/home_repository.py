from home_configuration.domain.home import Home
from datetime import datetime
from shared.infrastructure.database import db

class HomeRepository:
    
    def __init__(self):
        self.mycursor = db.get_connection()

    def createHouse(self, owner_id: int, date: datetime, map:str):
        sql = "INSERT INTO homes (owner_id, date, map) VALUES (%s, %s, %s)"
        val = (owner_id, date, map)
        self.mycursor.execute(sql, val)
        db.commit()
        return Home(self.mycursor.lastrowid, owner_id, date, map)
    
    def updateHome(self, id: int, owner_id: int, date: datetime, map:str):
        sql = "UPDATE homes SET owner_id = %s, date = %s, map = %s WHERE id = %s"
        val = (owner_id, date, map, id)
        self.mycursor.execute(sql, val)
        db.commit()
        sql = "SELECT * FROM homes WHERE id = %s"
        val = (id,)
        self.mycursor.execute(sql, val)
        row = self.mycursor.fetchone()
        return Home(row[0], row[1], row[2], row[3])
    
    def deleteHome(self, id: int):
        sql = "DELETE FROM homes WHERE id = %s"
        val = (id,)
        self.mycursor.execute(sql, val)
        db.commit()
        return True

    def getAllHomes(self):
        self.mycursor.execute("SELECT * FROM homes")
        myresult = self.mycursor.fetchall()
        homes = []
        print(myresult)
        for row in myresult:
            home = Home(row[0], row[1], row[2], row[3])
            homes.append(home)
        return homes
    
    def getHomeById(self, home_id: int):
        sql = "SELECT * FROM homes WHERE id = %s"
        val = (home_id,)
        self.mycursor.execute(sql, val)
        row = self.mycursor.fetchone()
        if row:
            return Home(row[0], row[1], row[2], row[3])
        else:
            return None