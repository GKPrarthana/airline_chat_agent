import sqlite3
import os

DB_PATH = "C:/Users/Prarthana/OneDrive - STRATA NEXTGEN PTY LTD/airline_chat_agent/backend/database/airline.db"
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../database/schema.sql")

def connect():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    with connect() as conn:
        with open(SCHEMA_PATH) as f:
            conn.executescript(f.read())

def get_flights(departure, destination, date):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM flights WHERE departure=? AND destination=? AND date=?",
        (departure, destination, date)
    )
    return cursor.fetchall()

def save_booking(name, email, flight_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (name, email, flight_id) VALUES (?, ?, ?)",
        (name, email, flight_id)
    )
    conn.commit()
