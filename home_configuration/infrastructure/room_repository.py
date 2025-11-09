from home_configuration.domain.room import Room
import mysql.connector

class RoomRepository:

    def __init__(self):
        self.mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",
        database="visualguide_db"
        )

    def createRoom(self, home_id: int, width: float, height: float, depth: float):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO rooms (home_id, width, height, depth) VALUES (%s, %s, %s, %s)"
        val = (home_id, width, height, depth)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return Room(mycursor.lastrowid, home_id, width, height, depth)
    
    def updateRoom(self, id: int, width: float, height: float, depth: float):
        mycursor = self.mydb.cursor()
        sql = "UPDATE rooms SET width = %s, height = %s, depth = %s WHERE id = %s"
        val = (width, height, depth, id)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return Room(id, None, width, height, depth)
    
    def deleteRoom(self, id: int):
        mycursor = self.mydb.cursor()
        sql = "DELETE FROM rooms WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return True
    
    def getAllRooms(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM rooms")
        myresult = mycursor.fetchall()
        rooms = []
        for row in myresult:
            room = Room(row[0], row[1], row[2], row[3], row[4])
            rooms.append(room)
        return rooms
    
    def getRoomById(self, room_id: int):
        mycursor = self.mydb.cursor()
        sql = "SELECT * FROM rooms WHERE id = %s"
        val = (room_id,)
        mycursor.execute(sql, val)
        row = mycursor.fetchone()
        if row:
            return Room(row[0], row[1], row[2], row[3], row[4])
        else:
            return None