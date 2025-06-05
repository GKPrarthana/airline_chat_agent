from services.db_service import initialize_db, connect

initialize_db()

conn = connect()
cursor = conn.cursor()

sample_flights = [
    ("LK", "LA", "2025-06-10", "LK101", "10:00 AM"),
    ("LK", "NY", "2025-06-10", "LK102", "12:00 PM"),
    ("LA", "LK", "2025-06-15", "LA201", "3:00 PM")
]

cursor.executemany(
    "INSERT INTO flights (departure, destination, date, flight_number, time) VALUES (?, ?, ?, ?, ?)",
    sample_flights
)
conn.commit()
print("Sample flights inserted.")
