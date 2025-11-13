# iam/infrastructure/mysql_user_repository.py
import mysql.connector
from mysql.connector import Error
from iam.domain.user import User
from iam.domain.user_repository import UserRepository


class MySQLUserRepository(UserRepository):
    def __init__(self, connection):
        self.connection = connection

    def save(self, user: User):
        """Guarda un usuario en la tabla users"""
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            values = (user.username, user.email, user.password)
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            print("✅ Usuario guardado correctamente")
        except Error as e:
            print(f"❌ Error al guardar el usuario: {e}")

    def find_by_email(self, email: str) -> User | None:
        """Busca un usuario por su email"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id, username, email, password FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return User(
                    id=result["id"],
                    username=result["username"],
                    email=result["email"],
                    password=result["password"]
                )
            return None
        except Error as e:
            print(f"❌ Error al buscar el usuario: {e}")
            return None
