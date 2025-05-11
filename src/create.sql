-- Database Code in SQLite format --

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CREATE DATABASE setap_sqlite_db;
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Creating the database tables --

CREATE TABLE User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    university_id INTEGER REFERENCES University(university_id),
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
    facility_name TEXT NOT NULL,
    facility_description TEXT
);

CREATE TABLE Booking (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id INTEGER NOT NULL REFERENCES Building(building_id),
    room_id INTEGER NOT NULL REFERENCES Room(room_id),
    start_time TEXT NOT NULL,
    duration TEXT NOT NULL, 
    access_code TEXT NOT NULL,
    share_code TEXT,
    completed INTEGER DEFAULT 0 CHECK (completed IN (0, 1))
);

CREATE TABLE Notification (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES Booking(booking_id),
    notification_type TEXT NOT NULL CHECK (notification_type IN ('Email', 'SMS')) DEFAULT 'Email'
);

CREATE TABLE User_Booking (
    user_id INTEGER NOT NULL REFERENCES User(user_id),
    booking_id INTEGER NOT NULL REFERENCES Booking(booking_id),
    shared INTEGER DEFAULT 0 CHECK (shared IN (0, 1)),
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
    facility_availability_status TEXT NOT NULL CHECK (facility_availability_status IN ('available', 'unavailable')) DEFAULT 'available',
    facility_quantity INTEGER NOT NULL DEFAULT 1,
    facility_notes TEXT,
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
INSERT INTO Facility (facility_name, facility_description)
VALUES
('Projector', 'High-definition ceiling-mounted projector'),
('Whiteboard', 'Large erasable whiteboard with markers'),
('Air Conditioning', 'Room temperature control via AC system'),
('Wi-Fi', 'Wireless internet access'),
('Computers', 'Networked PCs available for use'),
('3D Printer', 'Industrial-grade 3D printing machine'),
('Smart Board', 'Interactive digital smart board for presentations'),
('Printer', 'Laser printer for document printing'),
('HDMI Input', 'HDMI connectivity for devices'),
('Wheelchair Access', 'Facility is accessible via wheelchair ramp'),
('Lab Equipment', 'Specialized tools and instruments for experiments'),
('Sound System', 'Built-in audio system for clear sound projection'),
('Microphone', 'Wireless handheld microphone available'),
('Charging Ports', 'Power sockets and USB charging stations'),
('Video Conferencing', 'Room equipped with video conferencing setup');

INSERT INTO University (university_name, address)
VALUES ('University of Portsmouth', 'Winston Churchill Ave, Portsmouth PO1 2UP'),
('University of Southampton', 'Highfield Campus, University Rd, Southampton SO17 1BJ'),
('University of Brighton', 'Mithras House, Lewes Rd, Brighton BN2 4AT'),
('University of Kent', 'Canterbury CT2 7NZ'),
('University of Sussex', 'Falmer, Brighton BN1 9RH');
--- insert some sample data into the tables ---
INSERT INTO User (username, password, email, phone_number, offence_count, warning_type, role, university_id)
VALUES 
('up2211837@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2211837@myport.ac.uk', '07111111111', 0, 'none', 'user', 1),
('up2194051@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2194051@myport.ac.uk', '07222222222', 0, 'none', 'user', 1),
('up2195798@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2195798@myport.ac.uk', '07333333333', 0, 'none', 'user', 1),
('up2195798@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2195798@myport.ac.uk', '07635463633', 0, 'none', 'user', 1),
('up2245678@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2245678@myport.ac.uk', '07444444444', 0, 'none', 'user', 1),
('up2233199@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2233199@myport.ac.uk', '07555555555', 0, 'none', 'user', 1),
('up2208881@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'up2208881@myport.ac.uk', '07666666666', 0, 'none', 'user', 1),
('admin@myport.ac.uk', '$2b$12$HwfMvmCmyRIh0syYp3cnjeQijB3pwUAgjHKkLdaQzWdQqaY3pCe4m', 'admin@myport.ac.uk', '07000000000', 0, 'none', 'admin', 1);

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

INSERT INTO Room_Facility (room_id, facility_id) VALUES
(1, 1), (1, 2), (1, 4),
(2, 2), (2, 4), (2, 10),
(3, 2), (3, 4), (3, 9),
(4, 2), (4, 4), (4, 11),
(5, 1), (5, 2), (5, 4),
(6, 3), (6, 5), (6, 6),
(7, 2), (7, 4), (7, 14),
(8, 4), (8, 10), (8, 14),
(9, 4), (9, 3), (9, 14),
(10, 1), (10, 2), (10, 4),
(11, 2), (11, 4), (11, 9),
(12, 4), (12, 5), (12, 13),
(13, 1), (13, 2), (13, 14),
(14, 3), (14, 4), (14, 9),
(15, 2), (15, 5), (15, 11),
(16, 1), (16, 4), (16, 10),
(17, 3), (17, 4), (17, 14),
(18, 2), (18, 4), (18, 10),
(19, 2), (19, 4), (19, 11),
(20, 2), (20, 4), (20, 12),
(21, 1), (21, 2), (21, 4),
(22, 2), (22, 4), (22, 9),
(23, 4), (23, 10), (23, 14),
(24, 3), (24, 5), (24, 14),
(25, 1), (25, 2), (25, 4),
(26, 2), (26, 4), (26, 10),
(27, 2), (27, 5), (27, 11),
(28, 4), (28, 6), (28, 14),
(29, 2), (29, 4), (29, 14),
(30, 1), (30, 2), (30, 4),
(31, 3), (31, 4), (31, 10),
(32, 2), (32, 5), (32, 14),
(33, 2), (33, 4), (33, 9),
(34, 2), (34, 4), (34, 10),
(35, 2), (35, 4), (35, 14);



INSERT INTO Booking (building_id, room_id, start_time, share_code, duration, access_code)
VALUES
(2, 2, 1746082800,"123451", 1, 'A1'),
(2, 2, 1746090000,"123452", 2, 'A2'),
(2, 2, 1746104400,"123453", 1, 'A3'),
(2, 3, 1746082800,"123454", 1, 'B1'),
(2, 3, 1746090000,"123455", 2, 'B2'),
(2, 3, 1746104400,"123456", 1.5, 'B3'),
(2, 4, 1746090000,"123457", 2, 'C1'),
(2, 4, 1746104400,"123458", 1, 'C2'),
(2, 4, 1746111600,"123459", 1.5, 'C3'),
(2, 5, 1746082800,"1234510", 1.5, 'D1'),
(2, 5, 1746093600,"1234511", 2, 'D2'),
(2, 5, 1746104400,"1234512", 1, 'D3'),
(2, 6, 1746090000,"1234513", 2, 'E1'),
(2, 6, 1746104400,"1234514", 1.5, 'E2'),
(2, 6, 1746121200,"1234515", 1, 'E3'),
(2, 2, 1746174000,"1234516", 1, 'F1'),
(2, 2, 1746181200,"1234517", 2, 'F2'),
(2, 2, 1746195600,"1234518", 1.5, 'F3'),
(2, 3, 1746174000,"1234519", 1, 'G1'),
(2, 3, 1746181200,"1234520", 2, 'G2'),
(2, 3, 1746195600,"1234521", 1.5, 'G3'),
(2, 4, 1746181200,"1234522", 2, 'H1'),
(2, 4, 1746192000,"1234523", 1, 'H2'),
(2, 4, 1746202800,"1234524", 1.5, 'H3'),
(2, 5, 1746174000,"1234525", 1.5, 'I1'),
(2, 5, 1746181200,"1234526", 2, 'I2'),
(2, 5, 1746195600,"1234527", 1, 'I3'),
(2, 6, 1746181200,"1234528", 2, 'J1'),
(2, 6, 1746195600,"1234529", 1.5, 'J2'),
(2, 6, 1746202800,"1234530", 1, 'J3'),
(2, 2, 1746253800,"1234531", 1, 'K1'),
(2, 2, 1746261000,"1234532", 2, 'K2'),
(2, 2, 1746275400,"1234533", 1.5, 'K3'),
(2, 3, 1746257400,"1234534", 1, 'L1'),
(2, 3, 1746264600,"1234535",2, 'L2'),
(2, 3, 1746275400,"1234536", 1.5, 'L3'),
(2, 4, 1746261000,"1234537", 2, 'M1'),
(2, 4, 1746271800,"1234538", 1, 'M2'),
(2, 4, 1746275400,"1234539", 1.5, 'M3'),
(2, 5, 1746257400,"1234540", 1.5, 'N1'),
(2, 5, 1746268200,"1234541", 2, 'N2'),
(2, 5, 1746275400,"1234542", 1, 'N3'),
(2, 6, 1746264600,"1234543", 2, 'O1'),
(2, 6, 1746275400,"1234544", 1.5, 'O2'),
(2, 6, 1746287400,"1234545", 1, 'O3');


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





















