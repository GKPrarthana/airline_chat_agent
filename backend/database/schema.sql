-- Flights table
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    departure TEXT,
    destination TEXT,
    date TEXT,
    flight_number TEXT,
    time TEXT
);

-- Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    flight_id INTEGER,
    FOREIGN KEY (flight_id) REFERENCES flights(id)
);

