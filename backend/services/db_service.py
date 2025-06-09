import sqlite3
import os
import json

DB_PATH = "C:/Users/Prarthana/OneDrive - STRATA NEXTGEN PTY LTD/airline_chat_agent/backend/database/airline.db"
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../database/schema.sql")

def connect():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    with connect() as conn:
        with open(SCHEMA_PATH) as f:
            conn.executescript(f.read())

def get_flights(departure: str, destination: str, date: str) -> str:
    """
    Retrieves flights for a given departure, destination, and date.
    Returns a JSON string of a list of flight details.
    """
    conn = None
    try:
        conn = connect()
        cursor = conn.cursor()
        # Select specific columns that are useful for the user/LLM
        cursor.execute(
            "SELECT flight_number, time, departure, destination, date FROM flights WHERE departure=? AND destination=? AND date=?",
            (departure, destination, date)
        )
        
        rows = cursor.fetchall()
        
        if not rows:
            return json.dumps([]) # Return empty list as JSON string if no flights found
            
        column_names = [description[0] for description in cursor.description]
        
        flights_data = []
        for row in rows:
            flights_data.append(dict(zip(column_names, row)))
            
        return json.dumps(flights_data)
    except sqlite3.Error as e:
        # In a real app, you might log this error
        return json.dumps({"error": f"Database error while fetching flights: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred while fetching flights: {str(e)}"})
    finally:
        if conn:
            conn.close()

def save_booking(name: str, email: str, flight_id: str) -> str: # flight_id here is expected to be the flight_number
    """
    Saves a booking for a given passenger and flight_number.
    Returns a JSON string indicating success or failure.
    """
    conn = None
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Find the actual primary key (id) of the flight using the flight_number (passed as flight_id)
        cursor.execute("SELECT id FROM flights WHERE flight_number = ?", (flight_id,))
        flight_record = cursor.fetchone()
        
        if flight_record is None:
            return json.dumps({"status": "error", "message": f"Flight with number '{flight_id}' not found. Cannot book."})
        
        actual_flight_pk = flight_record[0] # This is the integer primary key from flights.id
        
        cursor.execute(
            "INSERT INTO bookings (name, email, flight_id) VALUES (?, ?, ?)",
            (name, email, actual_flight_pk)
        )
        conn.commit()
        booking_id = cursor.lastrowid
        return json.dumps({"status": "success", "message": f"Booking confirmed for {name} (email: {email}) on flight {flight_id}. Your booking ID is {booking_id}."})
    except sqlite3.Error as e:
        return json.dumps({"status": "error", "message": f"Database error during booking: {str(e)}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred during booking: {str(e)}"})
    finally:
        if conn:
            conn.close()
