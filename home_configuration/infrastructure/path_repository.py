from home_configuration.domain.path import Path
from shared.infrastructure.database import db

class PathRepository:
        
    def __init__(self):
        self.mycursor = db.get_connection()

    def createPath(self, home_id: int, lenght: float, list_rooms_ids: list):
        sql = "INSERT INTO paths (home_id, lenght) VALUES (%s, %s)"
        val = (home_id, lenght)
        self.mycursor.execute(sql, val)
        db.commit()
        id = self.mycursor.lastrowid
        #Insert rooms associated to the path
        for room_id in list_rooms_ids:
            sql = "INSERT INTO path_rooms (path_id, room_id) VALUES (%s, %s)"
            val = (id, room_id)
            self.mycursor.execute(sql, val)
        return Path(id, home_id, lenght, list_rooms_ids)
    
    def updatePath(self, id: int, lenght: float):
        sql = "UPDATE paths SET lenght = %s WHERE id = %s"
        val = (lenght, id)
        self.mycursor.execute(sql, val)
        db.commit()
        return self.getPathById(id)
    
    def deletePath(self, id: int):
        sql = "DELETE FROM paths WHERE id = %s"
        val = (id,)
        self.mycursor.execute(sql, val)
        db.commit()
        self.mycursor.execute("DELETE FROM path_rooms WHERE path_id = %s", (id,))
        return True
    
    def getAllPaths(self):
        self.mycursor.execute("SELECT * FROM paths")
        myresultPaths = self.mycursor.fetchall()
        paths = []
        for row in myresultPaths:
            self.mycursor.execute("SELECT * FROM path_rooms WHERE path_id = %s", (row[0],))
            myresultPathRooms = self.mycursor.fetchall()
            room_ids = [room_row[1] for room_row in myresultPathRooms]
            path = Path(row[0], row[1], row[2], room_ids)
            paths.append(path)
        return paths
    
    def getPathById(self, path_id: int):
        sql = "SELECT * FROM paths WHERE id = %s"
        val = (path_id,)
        self.mycursor.execute(sql, val)
        row = self.mycursor.fetchone()
        if row:
            self.mycursor.execute("SELECT * FROM path_rooms WHERE path_id = %s", (row[0],))
            myresultPathRooms = self.mycursor.fetchall()
            room_ids = [room_row[1] for room_row in myresultPathRooms]
            return Path(row[0], row[1], row[2], room_ids)
        else:
            return None