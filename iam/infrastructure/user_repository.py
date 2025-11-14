# iam/infrastructure/user_repository.py
import bcrypt
from iam.domain.user import User
from iam.domain.user_repository import UserRepository

class SQLiteUserRepository(UserRepository):
    def __init__(self, db_connection):
        self.db = db_connection

    def save(self, user: User):
        cursor = self.db.cursor()
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        sql = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
        values = (user.name, user.email, user.phone, hashed_password)
        cursor.execute(sql, values)
        self.db.commit()
        user.id = cursor.lastrowid
        cursor.close()
        return user

    def find_by_email(self, email: str):
        cursor = self.db.cursor(dictionary=True)
        sql = "SELECT * FROM users WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(**row)
        return None

    def find_all(self):
        cursor = self.db.cursor(dictionary=True)
        sql = "SELECT * FROM users"
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        return [User(**row) for row in rows]

    def find_by_id(self, user_id: int):
        cursor = self.db.cursor(dictionary=True)
        sql = "SELECT * FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(**row)
        return None
