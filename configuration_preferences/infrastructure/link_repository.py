import sqlite3
from datetime import datetime
from configuration_preferences.domain.link import LinkEntity

class LinkRepository:
    def __init__(self):
        self.db_path = "visualguide.db"

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_table_if_not_exists(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blind_user_id TEXT UNIQUE NOT NULL,
                link_code TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save_or_update_link(self, blind_user_id, link_code):
        self.create_table_if_not_exists()
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO links (blind_user_id, link_code)
            VALUES (?, ?)
            ON CONFLICT(blind_user_id)
            DO UPDATE SET link_code=excluded.link_code
        """, (blind_user_id, link_code))
        conn.commit()
        conn.close()

    def get_link_by_user(self, blind_user_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT blind_user_id, link_code FROM links WHERE blind_user_id=?", (blind_user_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {"blind_user_id": row["blind_user_id"], "link_code": row["link_code"]}
        return None
    
    

class TripRepository:
    def __init__(self, db_path="visualguide.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trip_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                route TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save_trip(self, trip):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO trip_history (title, date, time, route) VALUES (?, ?, ?, ?)",
            (trip.title, trip.date, trip.time, trip.route)
        )
        conn.commit()
        conn.close()

    def get_all_trips(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, date, time, route FROM trip_history")
        rows = cursor.fetchall()
        conn.close()
        return [{"title": r[0], "date": r[1], "time": r[2], "route": r[3]} for r in rows]