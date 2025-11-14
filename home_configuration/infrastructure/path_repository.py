from home_configuration.domain.path import Path
import mysql.connector

class PathRepository:
        
    def __init__(self):
        self.mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",
        database="visualguide_db"
        )

    def createPath(self, home_id: int, lenght: float, list_rooms_ids: list):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO paths (home_id, lenght) VALUES (%s, %s)"
        val = (home_id, lenght)
        mycursor.execute(sql, val)
        self.mydb.commit()
        id = mycursor.lastrowid
        #Insert rooms associated to the path
        for room_id in list_rooms_ids:
            sql = "INSERT INTO path_rooms (path_id, room_id) VALUES (%s, %s)"
            val = (id, room_id)
            mycursor.execute(sql, val)
        return Path(id, home_id, lenght, list_rooms_ids)
    
    def updatePath(self, id: int, lenght: float):
        mycursor = self.mydb.cursor()
        sql = "UPDATE paths SET lenght = %s WHERE id = %s"
        val = (lenght, id)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return self.getPathById(id)
    
    def deletePath(self, id: int):
        mycursor = self.mydb.cursor()
        sql = "DELETE FROM paths WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        self.mydb.commit()
        mycursor.execute("DELETE FROM path_rooms WHERE path_id = %s", (id,))
        return True
    
    def getAllPaths(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM paths")
        myresultPaths = mycursor.fetchall()
        paths = []
        for row in myresultPaths:
            mycursor.execute("SELECT * FROM path_rooms WHERE path_id = %s", (row[0],))
            myresultPathRooms = mycursor.fetchall()
            room_ids = [room_row[1] for room_row in myresultPathRooms]
            path = Path(row[0], row[1], row[2], room_ids)
            paths.append(path)
        return paths
    
    def getPathById(self, path_id: int):
        mycursor = self.mydb.cursor()
        sql = "SELECT * FROM paths WHERE id = %s"
        val = (path_id,)
        mycursor.execute(sql, val)
        row = mycursor.fetchone()
        if row:
            mycursor.execute("SELECT * FROM path_rooms WHERE path_id = %s", (row[0],))
            myresultPathRooms = mycursor.fetchall()
            room_ids = [room_row[1] for room_row in myresultPathRooms]
            return Path(row[0], row[1], row[2], room_ids)
        else:
            return None