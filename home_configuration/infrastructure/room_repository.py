from home_configuration.domain.room import Room
from shared.infrastructure.database import db

class RoomRepository:

    def __init__(self):
        self.mycursor = db.get_connection()

    def createRoom(self, home_id: int, width: float, height: float, depth: float):
        sql = "INSERT INTO rooms (home_id, width, height, depth) VALUES (%s, %s, %s, %s)"
        val = (home_id, width, height, depth)
        self.mycursor.execute(sql, val)
        db.commit()
        return Room(self.mycursor.lastrowid, home_id, width, height, depth)
    
    def updateRoom(self, id: int, width: float, height: float, depth: float):
        sql = "UPDATE rooms SET width = %s, height = %s, depth = %s WHERE id = %s"
        val = (width, height, depth, id)
        self.mycursor.execute(sql, val)
        db.commit()
        sql = "SELECT * FROM rooms WHERE id = %s"
        val = (id,)
        self.mycursor.execute(sql, val)
        row = self.mycursor.fetchone()
        return Room(row[0], row[1], row[2], row[3], row[4])
    
    def deleteRoom(self, id: int):
        sql = "DELETE FROM rooms WHERE id = %s"
        val = (id,)
        self.mycursor.execute(sql, val)
        db.commit()
        return True
    
    def getAllRooms(self):
        self.mycursor.execute("SELECT * FROM rooms")
        myresult = self.mycursor.fetchall()
        rooms = []
        for row in myresult:
            room = Room(row[0], row[1], row[2], row[3], row[4])
            rooms.append(room)
        return rooms
    
    def getRoomById(self, room_id: int):
        sql = "SELECT * FROM rooms WHERE id = %s"
        val = (room_id,)
        self.mycursor.execute(sql, val)
        row = self.mycursor.fetchone()
        if row:
            return Room(row[0], row[1], row[2], row[3], row[4])
        else:
            return None