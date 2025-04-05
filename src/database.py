import os
import sqlite3
import secrets
from pydantic.dataclasses import dataclass


@dataclass
class Room:
    id: int


@dataclass
class User:
    username: str
    email: str


@dataclass
class Booking:
    id: int
    user: User
    room: Room
    time: int


class DatabaseManager:
    """Database class the has functions mapped to identified SQL queries that are necersarry"""

    # sql queries should be put into these functions to interact with the database
    def __init__(
        self, file: str = "database.db", create_script: str = "src/create.sql"
    ):
        db_exists = os.path.exists("database.db")
        self.db = sqlite3.connect("database.db")
        self.cur = self.db.cursor()

        if not db_exists:
            with open(create_script, "r") as f:
                self.cur.executescript(f.read())

        self.db.commit()

    def get_email(self, user_id: int) -> str:
        """ Gets a email from a user """
        # takes a user_id and returns the email of the user
        # SELECT email FROM User WHERE user_id = ?;
        email = ""
        return email

    def create_token(self, user: User) -> str:
        """ Creates and returns a token new for a user """
        # query MUST insert token into the database that the user will use for the session
        # INSERT INTO Authentication (token, user_id, timestamp) VALUES (?, ?, datetime('now'));
        token = str(secrets.token_hex(32))
        return token
    
    def verify_token(self, token: str) -> bool:
        """ Verifies the token """
        user = self.get_user(token)
        if not user:
            return False
        return True

    def find_booking(self, room_id: int, time: int) -> Booking:
        """ Returns a booking if found at a room and time """
        # query must check DB for booking at room and time
        #SELECT * FROM Booking WHERE room_id = ? AND start_time <= time;
        return Booking(0, User("", ""), Room(0), 0)

    def get_booking(self, booking_id: int) -> Booking:
        """ Returns a booking from a booking id """
        # query must get the booking of booking_id
        #SELECT * FROM Booking WHERE booking_id = ?;
        return Booking(0, User("", ""), Room(0), 0)

    def add_booking(self, room_id: int, time: int, token: str) -> Booking:
        """ Adds a booking to the database  """
        # query must insert booking into database
        #INSERT INTO Booking (building_id, room_id, start_time, duration, access_code) VALUES (?, ?, ?, ?, ?);
        #INSERT INTO User_Booking (user_id, booking_id) VALUES (?, last_insert_rowid());
        # user is found from token
        user = self.get_user(token)
        if not user:
            return Booking(0, User("", ""), Room(0), 0)
        return Booking(0, User("", ""), Room(0), 0)

    def remove_booking(self, booking_id: int) -> Booking:
        """ Removes a booking from the database from booking id """
        # delete booking from database
        #DELETE FROM Booking WHERE booking_id = ?;
        #DELETE FROM User_Booking WHERE booking_id = ?;
        booking = self.get_booking(booking_id)
        return booking

    def get_all_bookings(self) -> list[Booking]:
        """ Returns a list of all future/current bookings """
        # query must get all future/current bookings
        #SELECT * FROM Booking WHERE datetime(start_time, '+' || duration || ' minutes') > datetime('now')ORDER BY start_time;

        return []

    def get_room(self, room_id: int) -> Room:
        """ Returns a room from a room id """
        # query must get a room from room_id
        #SELECT * FROM Room WHERE room_id = ?;
        return Room(0)

    def get_room_facilities(self, room_id: int) -> list[str]:
        """ Returns a list of facilities for a room """
        # query must get a list of facilities for a room
        #SELECT r.*, GROUP_CONCAT(f.facility_id) AS facility_ids FROM Room r LEFT JOIN Room_Facility rf ON r.room_id = rf.room_id LEFT JOIN Facility f ON rf.facility_id = f.facility_id WHERE r.room_id = ? GROUP BY r.room_id;
        return []
    def get_user(self, token: str) -> User:
        """ Returns a user from a token """
        # query must get a user from token
        #SELECT u.* FROM User u JOIN Authentication a ON u.user_id = a.user_id WHERE a.token = ?;
        return User("", "")

    def get_user_from_booking(self, booking_id: int) -> User:
        """ Returns a user from a booking id """
        # query must get a user from booking_id
        #SELECT u.* FROM User u JOIN User_Booking ub ON u.user_id = ub.user_id WHERE ub.booking_id = ?;
        return User("", "")
    
    def get_user_from_username(self, username: str)-> User:
        """ returns user from username """
        # query must get the users details
        #SELECT * FROM User WHERE username = ?;
        email = ""
        return User(username, email)
    
    def get_password(self, username: str) -> str:
        """ Returns a password for a user """
        # query must get the users password
        #SELECT password FROM User WHERE username = ?;
        password = ""
        return password
    
    def create_user(self, username: str, password: str) -> str:
        """ Create user in db """
        #INSERT INTO User (username, password, email, role) VALUES (?, ?, ?, 'user');
        user = User("", "")
        token = self.create_token(user)
        return token

    def get_user_email(self, user: User) -> str:
        """ Returns a user email from a user object """
        # query must get a user email from user object
        #SELECT email FROM User WHERE user_id = ?;
        return ""
