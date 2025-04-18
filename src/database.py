import os
import sqlite3
import secrets
from pydantic.dataclasses import dataclass
import create.sql as cs
from datetime import datetime
from typing import Optional, List



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

        self.cur.execute("SELECT email FROM User WHERE user_id = ?", (user_id,))
        result = self.cur.fetchone()

        if result:
            email = result[0] # not result because it is a tuple
        else:
            return "Error. User not found"

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
    
    def create_user(self, username: str, password: str, email: str) -> Optional[str]:
        """Create a new user and return authentication token"""
        try:
            self.cur.execute(
                """
                INSERT INTO User (username, password, email, role) 
                VALUES (?, ?, ?, 'user')
                """,
                (username, password, email)
            )
            user_id = self.cur.lastrowid
            self.db.commit()
            return self.create_token(user_id)
        except sqlite3.IntegrityError:
            return None
    
    def get_user(self, token: str) -> Optional[User]:
        """Get user from authentication token"""
        self.cur.execute(
            """
            SELECT u.user_id, u.username, u.email, u.role 
            FROM User u 
            JOIN Authentication a ON u.user_id = a.user_id 
            WHERE a.token = ?
            """,
            (token,)
        )
        if result := self.cur.fetchone():
            return User(
                id=result["user_id"],
                username=result["username"],
                email=result["email"],
                role=result["role"]
            )
        return None

    def get_user_from_booking(self, booking_id: int) -> Optional[User]:
        """Get user associated with a booking"""
        self.cur.execute(
            """
            SELECT u.user_id, u.username, u.email, u.role
            FROM User u 
            JOIN User_Booking ub ON u.user_id = ub.user_id 
            WHERE ub.booking_id = ?
            """,
            (booking_id,)
        )
        if result := self.cur.fetchone():
            return User(
                id=result["user_id"],
                username=result["username"],
                email=result["email"],
                role=result["role"]
            )
        return None

    def get_user_from_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        self.cur.execute(
            "SELECT user_id, username, email, role FROM User WHERE username = ?",
            (username,)
        )
        if result := self.cur.fetchone():
            return User(
                id=result["user_id"],
                username=result["username"],
                email=result["email"],
                role=result["role"]
            )
        return None
    
    def get_password(self, username: str) -> Optional[str]:
        """Get hashed password for a user"""
        self.cur.execute(
            "SELECT password FROM User WHERE username = ?",
            (username,)
        )
        if result := self.cur.fetchone():
            return result["password"]
        return None
    
        
    def get_user_email(self, user_id: int) -> Optional[str]:
        """Get email from user_id"""
        self.cur.execute(
            "SELECT email FROM User WHERE user_id = ?",
            (user_id,)
        )
        if result := self.cur.fetchone():
            return result["email"]
        return None

    def find_booking(self, room_id: int, time: str) -> Booking:
        """ Returns a booking if found at a room and time """
        # Query to find a booking in the Booking table for the specified room and time
        self.cur.execute(
            '''
            SELECT b.booking_id, b.building_id, b.room_id, b.start_time, b.duration, b.access_code, ub.user_id
            FROM Booking b
            JOIN User_Booking ub ON b.booking_id = ub.booking_id
            WHERE b.room_id = ? AND b.start_time <= ?
            ''',
            (room_id, time)
        )
        
        result = self.cur.fetchone()

        if result:
            booking_id = result[0]  # booking_id
            building_id = result[1]  # building_id
            room_id = result[2]      # room_id
            start_time = result[3]   # start_time
            duration = result[4]      # duration
            access_code = result[5]   # access_code
            user_id = result[6]       # user_id

            # Retrieve User object from user_id
            user = self.get_user_from_booking(user_id)

            return Booking(booking_id, user, Room(room_id), start_time)
        else:
            return "Booking doesn't exist."

    def get_booking(self, booking_id: int) -> Booking:
        """ Returns a booking from a booking_id """
        # Query to get the booking details from the Booking table
        self.cur.execute(
            '''
            SELECT b.booking_id, b.building_id, b.room_id, b.start_time, b.duration, b.access_code, ub.user_id
            FROM Booking b
            JOIN User_Booking ub ON b.booking_id = ub.booking_id
            WHERE b.booking_id = ?
            ''',
            (booking_id,)
        )
        
        result = self.cur.fetchone()

        if result:  # Check if a booking was found
            booking_id = result[0]  # booking_id
            building_id = result[1]  # building_id
            room_id = result[2]      # room_id
            start_time = result[3]   # start_time
            duration = result[4]     # duration
            access_code = result[5]  # access_code
            user_id = result[6]      # user_id

            # Retrieve User object from user_id
            user = self.get_user_from_booking(user_id)

            room = self.get_room_by_id(room_id)

            return Booking(booking_id, user, room, start_time)
        else:
            return "Booking doesn't exist."  

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

    def remove_booking(self, booking_id: int) -> bool:
        """ Removes a booking from the database using the booking_id """
    
        booking = self.get_booking(booking_id)
        
        if isinstance(booking, Booking):  # check if booking exists
            
            self.cur.execute("DELETE FROM User_Booking WHERE booking_id = ?", (booking_id,)) # Delete from User_Booking table
            
            self.cur.execute("DELETE FROM Booking WHERE booking_id = ?", (booking_id,)) # Delete from Booking table

            self.db.commit() # commit to db
            
            return True  # successful removal
        else:
            return False  # booking didn't exist


    def get_all_bookings(self) -> list[Booking]:
        """ Returns a list of all future/current bookings """
        # Query to get all future/current bookings
        self.cur.execute(
            '''
            SELECT b.booking_id, b.building_id, b.room_id, b.start_time, b.duration, b.access_code, ub.user_id
            FROM Booking b
            JOIN User_Booking ub ON b.booking_id = ub.booking_id
            WHERE datetime(b.start_time, '+' || b.duration || ' minutes') > datetime('now')
            ORDER BY b.start_time;
            '''
        )
        
        results = self.cur.fetchall()  # Fetch all matching bookings
        bookings = []  # List to hold Booking objects

        for result in results:
            booking_id = result[0]  # booking_id
            building_id = result[1]  # building_id
            room_id = result[2]      # room_id
            start_time = result[3]   # start_time
            duration = result[4]      # duration
            access_code = result[5]   # access_code
            user_id = result[6]       # user_id

            # Retrieve User object from user_id
            user = self.get_user_from_booking(user_id)

            # Create Room object
            room = Room(id=room_id)

            # Create Booking object and append to the list
            bookings.append(Booking(id=booking_id, user=user, room=room, time=start_time))

        return bookings  # Return the list of Booking objects


    def get_room(self, room_id: int) -> Room:
        """ Returns a room from a room id """
        # Query to get a room from the Room table
        self.cur.execute(
            '''
            SELECT room_id FROM Room WHERE room_id = ?;
            ''',
            (room_id,)
        )
        
        result = self.cur.fetchone() 

        if result: 
            return Room(id=result[0]) 
        else:
            return "Room not found." 

    def get_room_facilities(self, room_id: int) -> list[str]:
        """ Returns a list of facilities for a room """
        # Query to get a list of facilities for the specified room

        #set below f.facility_id to f.facility_name when the sql file is changed
        self.cur.execute(
            '''
            SELECT f.facility_id 
            FROM Facility f
            LEFT JOIN Room_Facility rf ON f.facility_id = rf.facility_id
            WHERE rf.room_id = ?;
            ''',
            (room_id,)
        )
        
        results = self.cur.fetchall()  # Fetch all matching facilities
        facilities = [result[0] for result in results]  # Extract facility_ids into a list

        return facilities  # currently this returns ID's. Need to return actual facilities when necessary change is made in the sql file.
    
    def close(self): # for testing purposes
        self.db.close()
        