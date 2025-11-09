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

    def createPath(self, home_id: int, lenght: float):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO paths (home_id, lenght) VALUES (%s, %s)"
        val = (home_id, lenght)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return Path(mycursor.lastrowid, home_id, lenght)
    
    def updatePath(self, id: int, lenght: float):
        mycursor = self.mydb.cursor()
        sql = "UPDATE paths SET lenght = %s WHERE id = %s"
        val = (lenght, id)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return Path(id, None, lenght)
    
    def deletePath(self, id: int):
        mycursor = self.mydb.cursor()
        sql = "DELETE FROM paths WHERE id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        self.mydb.commit()
        return True
    
    def getAllPaths(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT * FROM paths")
        myresult = mycursor.fetchall()
        paths = []
        for row in myresult:
            path = Path(row[0], row[1], row[2])
            paths.append(path)
        return paths
    
    def getPathById(self, path_id: int):
        mycursor = self.mydb.cursor()
        sql = "SELECT * FROM paths WHERE id = %s"
        val = (path_id,)
        mycursor.execute(sql, val)
        row = mycursor.fetchone()
        if row:
            return Path(row[0], row[1], row[2])
        else:
            return None