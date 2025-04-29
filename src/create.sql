-- Database Code in SQLite format --

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CREATE DATABASE setap_sqlite_db;
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Creating the database tables --

CREATE TABLE User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    phone_number TEXT,
    offence_count INTEGER CHECK (offence_count >= 0) DEFAULT 0,
    warning_type TEXT CHECK (warning_type IN ('none', 'minor', 'major')) DEFAULT 'none',
    role TEXT NOT NULL CHECK (role IN ('admin', 'user')) DEFAULT 'user'
);

CREATE TABLE Authentication (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES User(user_id),
    timestamp TEXT NOT NULL
);

CREATE TABLE Building (
    building_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_name TEXT NOT NULL,
    address_1 TEXT NOT NULL,
    address_2 TEXT,
    opening_time TEXT NOT NULL,
    closing_time TEXT NOT NULL CHECK (closing_time > opening_time)
);

CREATE TABLE Room (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id INTEGER NOT NULL REFERENCES Building(building_id),
    room_type TEXT NOT NULL CHECK (room_type IN ('study room', 'lecture room', 'computing room', 'lab')),
    room_capacity INTEGER NOT NULL CHECK (room_capacity > 0),
    room_availability_status TEXT NOT NULL CHECK (room_availability_status IN ('available', 'unavailable')) DEFAULT 'available'
);

CREATE TABLE Facility (
    facility_id INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_quantity INTEGER NOT NULL,
    facility_availability_status TEXT NOT NULL CHECK (facility_availability_status IN ('available', 'unavailable')) DEFAULT 'available'
);
-- this table needs an additional attribute to show the facility type for the get_room_facilities() to work. Till this is sorted, the ftn will return facility_id for now. Will update this later.

CREATE TABLE Booking (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id INTEGER NOT NULL REFERENCES Building(building_id),
    room_id INTEGER NOT NULL REFERENCES Room(room_id),
    start_time TEXT NOT NULL,
    duration TEXT NOT NULL, 
    access_code TEXT NOT NULL
);

CREATE TABLE Notification (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES Booking(booking_id),
    notification_type TEXT NOT NULL CHECK (notification_type IN ('Email', 'SMS')) DEFAULT 'Email'
);

CREATE TABLE User_Booking (
    user_id INTEGER NOT NULL REFERENCES User(user_id),
    booking_id INTEGER NOT NULL REFERENCES Booking(booking_id),
    PRIMARY KEY (user_id, booking_id)
);

CREATE TABLE User_Notification (
    user_id INTEGER NOT NULL REFERENCES User(user_id),
    notification_id INTEGER NOT NULL REFERENCES Notification(notification_id),
    PRIMARY KEY (user_id, notification_id)
);

CREATE TABLE Room_Facility (
    room_id INTEGER NOT NULL REFERENCES Room(room_id),
    facility_id INTEGER NOT NULL REFERENCES Facility(facility_id),
    PRIMARY KEY (room_id, facility_id)
);

























