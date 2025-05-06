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
    verified INTEGER DEFAULT 0 CHECK (verified IN (0, 1)),
    phone_number TEXT,
    offence_count INTEGER CHECK (offence_count >= 0) DEFAULT 0,
    warning_type TEXT CHECK (warning_type IN ('none', 'minor', 'major')) DEFAULT 'none',
    role TEXT NOT NULL CHECK (role IN ('admin', 'user')) DEFAULT 'user'
);

CREATE TABLE EmailVerification (
    verify_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    verification_code TEXT,
    created_at INTEGER,
    FOREIGN KEY(user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Authentication (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES User(user_id),
    timestamp TEXT NOT NULL
);

CREATE TABLE Building (
    building_id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER NOT NULL REFERENCES University(university_id),
    building_name TEXT NOT NULL,
    address_1 TEXT NOT NULL,
    address_2 TEXT,
    opening_time TEXT NOT NULL,
    closing_time TEXT NOT NULL CHECK (closing_time > opening_time)
);

CREATE TABLE Room (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id INTEGER NOT NULL REFERENCES Building(building_id),
    room_name TEXT NOT NULL,
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


-- University Table
CREATE TABLE University (
    university_id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_name TEXT NOT NULL,
    address TEXT
);

-- Linking Table between User and University
CREATE TABLE User_University (
    user_id INTEGER NOT NULL REFERENCES User(user_id),
    university_id INTEGER NOT NULL REFERENCES University(university_id),
    status INTEGER DEFAULT 0 CHECK (status IN (0, 1)), -- 0 for inactive, 1 for active
    PRIMARY KEY (user_id, university_id)
);

INSERT INTO University (university_name, address)
VALUES ('University of Portsmouth', 'Winston Churchill Ave, Portsmouth PO1 2UP');
--- insert some sample data into the tables ---
INSERT INTO User (username, password, email, phone_number, offence_count, warning_type, role)
VALUES 
('up2211837@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2211837@myport.ac.uk', '07111111111', 0, 'none', 'user'),
('up2194051@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2194051@myport.ac.uk', '07222222222', 0, 'none', 'user'),
('up2195798@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2195798@myport.ac.uk', '07333333333', 0, 'none', 'user'),
('up2195798@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2195798@myport.ac.uk', '07635463633', 0, 'none', 'user'),
('up2245678@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2245678@myport.ac.uk', '07444444444', 0, 'none', 'user'),
('up2233199@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2233199@myport.ac.uk', '07555555555', 0, 'none', 'user'),
('up2208881@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2208881@myport.ac.uk', '07666666666', 0, 'none', 'user'),
('admin@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'admin@myport.ac.uk', '07000000000', 0, 'none', 'admin');

INSERT INTO EmailVerification (user_id) VALUES
(1),
(2),
(3),
(4),
(5),
(6),
(7);

INSERT INTO Building (university_id, building_name, address_1, address_2, opening_time, closing_time)
VALUES 
(1,'Engineering Building', '123 Tech Street', 'Campus A', '08:00', '18:00'),
(1,'Science Hall', '10 Quantum Road', 'Campus B', '08:00', '20:00'),
(1,'Library', '15 Book Lane', 'Campus Central', '07:30', '22:00'),
(1,'Computing Centre', '42 Silicon Ave', 'Campus C', '08:00', '21:00'),
(1,'Medical Block', '88 Health Blvd', 'Campus D', '08:00', '19:00'),
(1,'Business School', '5 Finance Drive', 'Campus E', '08:30', '18:30'),
(1,'Arts Building', '77 Creative Street', 'Campus F', '09:00', '17:00');

INSERT INTO Room (building_id, room_name, room_type, room_capacity, room_availability_status) VALUES
(1, '1.0', 'study room', 10, 'available'),
-- Science Hall (Building 2)
(2, '2.01', 'study room', 12, 'available'),
(2, '2.02', 'lecture room', 60, 'available'),
(2, '2.03', 'lab', 25, 'available'),
(2, '2.04', 'computing room', 30, 'available'),
(2, '2.05', 'lecture room', 80, 'available'),

-- Library (Building 3)
(3, '3.01', 'study room', 8, 'available'),
(3, '3.02', 'study room', 10, 'available'),
(3, '3.03', 'computing room', 20, 'available'),
(3, '3.04', 'study room', 6, 'available'),

-- Computing Centre (Building 4)
(4, '4.01', 'computing room', 35, 'available'),
(4, '4.02', 'computing room', 40, 'available'),
(4, '4.03', 'lab', 20, 'available'),
(4, '4.04', 'study room', 10, 'available'),
(4, '4.05', 'lecture room', 70, 'available'),
(4, '4.06', 'lab', 18, 'available'),

-- Medical Block (Building 5)
(5, '5.01', 'lab', 25, 'available'),
(5, '5.02', 'lab', 30, 'available'),
(5, '5.03', 'lecture room', 50, 'available'),
(5, '5.04', 'study room', 10, 'available'),
(5, '5.05', 'computing room', 16, 'available'),

-- Business School (Building 6)
(6, '6.01', 'lecture room', 100, 'available'),
(6, '6.02', 'study room', 10, 'available'),
(6, '6.03', 'lecture room', 80, 'available'),
(6, '6.04', 'computing room', 25, 'available'),
(6, '6.05', 'study room', 6, 'available'),
(6, '6.06', 'study room', 12, 'available'),

-- Arts Building (Building 7)
(7, '7.01', 'study room', 6, 'available'),
(7, '7.02', 'lecture room', 40, 'available'),
(7, '7.03', 'lab', 15, 'available'),
(7, '7.04', 'computing room', 20, 'available'),
(7, '7.05', 'study room', 10, 'available');

INSERT INTO Booking (building_id, room_id, start_time, duration, access_code)
VALUES
(1, 1, 1746084000, 1, 'ABC123'),
(1, 1, 1746175200, 2, 'DEF456'),
(1, 1, 1746255000, 1.5, 'GHI789');


INSERT INTO User_Booking (user_id, booking_id)
VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 1),
(2, 2),
(2, 3),
(3, 1),
(3, 2),
(3, 3),
(4, 1),
(4, 2),
(4, 3),
(5, 1),
(5, 2),
(5, 3),
(6, 1),
(6, 2),
(6, 3),
(7, 1),
(7, 2),
(7, 3);

INSERT INTO User_University (user_id, university_id)
VALUES 
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(8, 1);





















