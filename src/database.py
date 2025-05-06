import os
from typing import Optional
from datetime import datetime
import time
import secrets
import aiosqlite
from pydantic.dataclasses import dataclass


@dataclass
class Room:
    id: int
    name:str
    building_id: int
    type: Optional[str] = None

@dataclass
class LoggedInUser:
    token: str
@dataclass
class User:
    username: str
    email: str
    id: Optional[int] = None
    role: Optional[str] = None


@dataclass
class Booking:

    id: int
    user: User
    room: Room
    time: int
    duration: Optional[float] = None
    building: Optional["Building"] = None  
@dataclass
class Building:
    id: int
    name: str
    address_1: str
    address_2: str
    opening_time: str
    closing_time: str
class DB:
    def __init__(self):
        self.db = None

    async def __aenter__(self) -> "DatabaseManager":
        self.db = await DatabaseManager.create()
        return self.db

    async def __aexit__(self, exc_type, exc_val, traceback):
        if self.db:
            await self.db.close()

class DatabaseManager:
    """Database class the has functions mapped to identified SQL queries that are necersarry"""

    file: str = "database.db"
    create_script: str = "src/create.sql"

    # sql queries should be put into these functions to interact with the database
    def __init__(self, file: str | None = None, create: str | None = None):
        DatabaseManager.file = file or DatabaseManager.file
        DatabaseManager.create_script = create or DatabaseManager.create_script
        self.conn: aiosqlite.Connection | None = None

    @classmethod
    async def create(cls) -> "DatabaseManager":
        self = cls()

        db_exists = os.path.exists(self.file)

        self.conn = await aiosqlite.connect(self.file)

        if not db_exists:
            with open(self.create_script, "r") as f:
                await self.conn.executescript(f.read())

        await self.conn.commit()
        return self

    async def issue_strike_to_user(self, user_id: int) -> int:
        """ Issues a strike to a user """
        try:
            await self.conn.execute(
                "UPDATE User SET offence_count = offence_count + 1 WHERE user_id = ?",
                (user_id,)
            )
            await self.conn.commit()

            async with self.conn.execute(
                "SELECT offence_count FROM User WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

        except Exception as e:
            print("Error issuing strike:", e)
            return None
        
    
    async def get_account_details(self, user_id: int) -> dict:
        """Returns full account details and associated universities for a user."""

        # Fetch user details
        async with self.conn.execute("""
            SELECT user_id, username, email, phone_number, offence_count, role
            FROM User WHERE user_id = ?
        """, (user_id,)) as cursor:
            user = await cursor.fetchone()

        if not user:
            return {"error": "User not found"}

        # Fetch university associations
        async with self.conn.execute("""
            SELECT U.university_name, UU.status 
            FROM User_University UU
            JOIN University U ON UU.university_id = U.university_id
            WHERE UU.user_id = ?
        """, (user_id,)) as cursor:
            universities = await cursor.fetchall()

        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "phone_number": user[3],
            "offence_count": user[4],
            "role": user[5],
            "universities": [
                {"name": row[0], "status": row[1]} for row in universities
            ]
        }
    async def get_email(self, user_id: int) -> str:
        """ Gets a email from a user """
        # takes a user_id and returns the email of the user
        # SELECT email FROM User WHERE user_id = ?;

        async with self.conn.execute("SELECT email FROM User WHERE user_id = ?", (user_id,)) as cursor:
            result = await self.conn.fetchone()

        if result:
            return result[0]  # not result because it is a tuple
        return "Error. User not found"
    async def edit_booking(self, booking_id: int, room_id: int, start_time: str, duration: int) -> bool:
        """ Edits a booking in the database """
        try:
            await self.conn.execute(
                """
                UPDATE Booking
                SET room_id = ?, start_time = ?, duration = ?
                WHERE booking_id = ?
                """,
                (room_id, start_time, duration, booking_id)
            )
            await self.conn.commit()
            return True
        except Exception as e:
            print("Error editing booking:", e)
            return False
        
    async def delete_token(self, token: str) -> bool:
        """Delete the token from the database."""
        try:
            await self.conn.execute("DELETE FROM Authentication WHERE token = ?", (token,))
            await self.conn.commit()
            return True
        except Exception as e:
            print("Token deletion error:", e)
            return False
        
    async def create_token(self, user: User) -> str:
        """Generate and store an authentication token for the given username."""
        try:
            async with self.conn.execute(
                "SELECT user_id FROM User WHERE username = ?", (user.username,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None  # Username not found
                user_id = row[0]

            token = str(secrets.token_hex(32))
            timestamp = int(time.time() * 1000) 

            await self.conn.execute(
                """
                INSERT INTO Authentication (token, user_id, timestamp)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    token = excluded.token,
                    timestamp = excluded.timestamp
                """,
                (token, user_id, timestamp)
            )
            await self.conn.commit()
            return token

        except Exception as e:
            print("Token creation error:", e)
            return None
            """ Creates and returns a token new for a user """
    async def verify_token(self, token: str) -> bool:
        """ Verifies the token """
        user = self.get_user(token)
        if not user:
            return False
        return True

    async def create_user(self, username: str, password: str, email: str) -> Optional[str]:
        """Create a new user and return authentication token"""
        try:
            async with self.conn.execute(
                """
                INSERT INTO User (username, password, email, role) 
                VALUES (?, ?, ?, 'user')
                """,
                (username, password, email)
            ) as cur:
                user_id = cur.lastrowid
                user = await self.get_user_from_username(username)
                await self.conn.commit()
                return await self.create_token(user)
        except aiosqlite.IntegrityError:
            return None

    async def get_user(self, token: str) -> Optional[User]:
        """Get user from authentication token"""
        async with self.conn.execute(
            """
            SELECT  u.username, u.email, u.role, u.user_id
            FROM User u 
            JOIN Authentication a ON u.user_id = a.user_id 
            WHERE a.token = ?
            """,
            (token,)
        ) as cur:
            if result := await cur.fetchone():
                return User(
                    username=result[0],
                    email=result[1],
                    id=result[3],
                    role=result[2]
                )
        return None

    async def get_user_from_booking(self, booking_id: int) -> Optional[User]:
        """Get user associated with a booking"""
        async with self.conn.execute(
            """
            SELECT u.user_id, u.username, u.email, u.role
            FROM User u 
            JOIN User_Booking ub ON u.user_id = ub.user_id 
            WHERE ub.booking_id = ?
            """,
            (booking_id,)
        ) as cur:
            if result := await cur.fetchone():
                return User(
                    username=result[1],
                    email=result[2]
                )
        return None

    async def get_user_from_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        username = username.lower()
        print(username)
        async with self.conn.execute(
            "SELECT user_id, username, email, role FROM User WHERE username = ?",
            (username,)
        ) as cur:
            if result := await cur.fetchone():
                return User(
                    # id=result["user_id"],
                    username=result[1],
                    email=result[2],
                    # role=result["role"]
                )
        return None

    async def get_user_from_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with self.conn.execute(
            "SELECT user_id, username, email, role FROM User WHERE email = ?",
            (email,)
        ) as cur:
            if result := await cur.fetchone():
                return User(
                    # id=result["user_id"],
                    username=result[1],
                    email=result[2],
                    # role=result["role"]
                )
        return None
    async def get_password(self, user: User) -> Optional[str]:
        """Get hashed password for a user"""
        async with self.conn.execute(
            "SELECT password FROM User WHERE username = ?",
            (user.username,)
        ) as cur:
            if result := await cur.fetchone():
                return result[0]
        return None

    async def get_user_email(self, user_id: int) -> Optional[str]:
        """Get email from user_id"""
        async with self.conn.execute(
            "SELECT email FROM User WHERE user_id = ?",
            (user_id,)
        ) as cur:
            if result := cur.fetchone():
                return result["email"]
        return None

    async def find_booking(self, room_id: int, time: str) -> Booking:
        """ Returns a booking if found at a room and time """
        # Query to find a booking in the Booking table for the specified room and time
        async with self.conn.execute(
            '''
            SELECT b.booking_id, b.building_id, b.room_id, b.start_time, b.duration, b.access_code, ub.user_id
            FROM Booking b
            JOIN User_Booking ub ON b.booking_id = ub.booking_id
            WHERE b.room_id = ? AND b.start_time <= ?
            ''',
            (room_id, time)
        ) as cur:

            result = cur.fetchone()

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
            return "Booking doesn't exist."

    async def get_booking(self, booking_id: int) -> Booking:
        """ Returns a booking from a booking_id """
        # Query to get the booking details from the Booking table
        async with await self.conn.execute(
            '''
            SELECT b.booking_id, b.building_id, b.room_id, b.start_time, b.duration, b.access_code, ub.user_id
            FROM Booking b
            JOIN User_Booking ub ON b.booking_id = ub.booking_id
            WHERE b.booking_id = ?
            ''',
            (booking_id,)
        ) as cur:

            result = await cur.fetchone()
            
            if result:  # Check if a booking was found
                booking_id = result[0]  # booking_id
                building_id = result[1]  # building_id
                room_id = result[2]      # room_id
                start_time = result[3]   # start_time
                duration = result[4]     # duration
                access_code = result[5]  # access_code
                user_id = result[6]      # user_id

                # Retrieve User object from user_id
                user = await self.get_user_from_booking(booking_id)

                room = await self.get_room(room_id)

                return Booking(booking_id, user, room, start_time)
            return "Booking doesn't exist."
    async def get_rooms(self) -> list[Room]:
        """ Returns a list of all rooms """
        # Query to get all rooms from the Room table
        async with self.conn.execute(
            '''
            SELECT room_id, room_name, building_id, room_type FROM Room;
            '''
        ) as cur:

            results = await cur.fetchall()
            rooms = []  # List to hold Room objects
            for result in results:
                room_id = result[0]
                room_name = result[1]
                building_id = result[2]
                room_type = result[3] if len(result) > 3 else None  # Check if room_type exists

                # Create Room object and append to the list
                rooms.append(Room(id=room_id, name=room_name, building_id=building_id, type=room_type))
            return rooms

    async def get_buildings(self) -> list[Building]:
        """ Returns a list of all buildings """
        # Query to get all buildings from the Building table
        async with self.conn.execute(
            '''
            SELECT building_id, building_name, address_1, address_2, opening_time, closing_time FROM Building;
            '''
        ) as cur:

            results = await cur.fetchall()
            buildings = []
            for result in results:  
                building_id = result[0]
                building_name = result[1]
                address_1 = result[2]
                address_2 = result[3]
                opening_time = result[4]
                closing_time = result[5]

                # Create Building object and append to the list
                buildings.append(Building(
                    id=building_id,
                    name=building_name,
                    address_1=address_1,
                    address_2=address_2,
                    opening_time=opening_time,
                    closing_time=closing_time
                ))
            return buildings  # Return the list of Building objects
    async def add_booking(self, room_id: int, time: int, token: str) -> Booking:
        """ Adds a booking to the database  """
        # query must insert booking into database
        #INSERT INTO Booking (building_id, room_id, start_time, duration, access_code) VALUES (?, ?, ?, ?, ?);
        #INSERT INTO User_Booking (user_id, booking_id) VALUES (?, last_insert_rowid());
        # user is found from token
        user = self.get_user(token)
        if not user:
            return Booking(0, User("", ""), Room(0), 0)
        return Booking(0, User("", ""), Room(0), 0)

    async def remove_booking(self, booking_id: int) -> bool:
        """ Removes a booking from the database using the booking_id """

        booking = await self.get_booking(booking_id)

        if isinstance(booking, Booking):  # check if booking exists

            await self.conn.execute("DELETE FROM User_Booking WHERE booking_id = ?", (booking_id,))  # Delete from User_Booking table

            await self.conn.execute("DELETE FROM Booking WHERE booking_id = ?", (booking_id,))  # Delete from Booking table

            await self.conn.commit()

            return True
        return False  


    async def get_all_bookings(self) -> list[Booking]:
        """ Returns a list of all future/current bookings """
        # Query to get all future/current bookings
        async with self.conn.execute(
            '''
            SELECT 
                b.booking_id, 
                b.building_id, 
                b.room_id, 
                r.room_name, 
                b.start_time, 
                b.duration, 
                b.access_code, 
                ub.user_id
            FROM 
                Booking b
            JOIN 
                User_Booking ub ON b.booking_id = ub.booking_id
            JOIN 
                Room r ON b.room_id = r.room_id
            WHERE 
                datetime(b.start_time, '+' || b.duration || ' minutes') > datetime('now')
            ORDER BY 
                b.start_time;
            '''
        ) as cur:

            results = cur.fetchall()  # Fetch all matching bookings
            bookings = []  # List to hold Booking objects

            for result in results:
                booking_id = result[0]  # booking_id
                building_id = result[1]  # building_id
                room_id = result[2]      # room_id
                room_name = result[3]
                start_time = result[4]   # start_time
                duration = result[5]      # duration
                access_code = result[6]   # access_code
                user_id = result[7]       # user_id

                # Retrieve User object from user_id
                user = self.get_user_from_booking(user_id)

                # Create Room object
                room = Room(id=room_id,
                            name=room_name,
                            building_id=building_id)

                # Create Booking object and append to the list
                bookings.append(Booking(id=booking_id, user=user, room=room, time=start_time))

            return bookings  # Return the list of Booking objects
        
    async def get_bookings_by_token(self, token: str) -> list[Booking]:
        """Returns all current/future bookings for a user identified by their token, including building info"""
        # Get user_id from token
        async with self.conn.execute(
            "SELECT user_id FROM Authentication WHERE token = ?", (token,)
        ) as cur:
            result = await cur.fetchone()
            print(result)
            if result is None:
                return []  # Invalid token or not found
            user_id = result[0]
            user = await self.get_user(token)
        async with self.conn.execute(
        '''
            SELECT 
                b.booking_id, 
                b.building_id, 
                b.room_id, 
                r.room_name,
                b.start_time, 
                b.duration, 
                b.access_code, 
                bl.building_name, 
                bl.address_1, 
                bl.address_2, 
                bl.opening_time, 
                bl.closing_time
            FROM 
                Booking b
            JOIN 
                User_Booking ub ON b.booking_id = ub.booking_id
            JOIN 
                Building bl ON b.building_id = bl.building_id
            JOIN 
                Room r ON b.room_id = r.room_id  
            WHERE 
                ub.user_id = ?
            ORDER BY 
                b.start_time;
            ''',
            (user_id,)
        ) as cur:
            results = await cur.fetchall()
            print("results")
            print(results)
            bookings = []

            for result in results:
                booking_id = result[0]
                building_id = result[1]
                room_id = result[2]
                room_name = result[3]  # Extract room_name from the result
                start_time = result[4]
                duration = result[5]
                access_code = result[6]
                building_name = result[7]
                address_1 = result[8]
                address_2 = result[9]
                opening_time = result[10]
                closing_time = result[11]

                room = Room(id=room_id, name=room_name, building_id=building_id)  # Create Room instance with name
                building = Building(
                    id=building_id,
                    name=building_name,
                    address_1=address_1,
                    address_2=address_2,
                    opening_time=opening_time,
                    closing_time=closing_time
                )


                bookings.append(Booking(
                    id=booking_id,
                    user=user,
                    room=room,
                    time=start_time,
                    building=building,
                    duration=duration
                ))
            print("bookings" + str(len(bookings)) + "user" + user.username + " "+ str(user_id))
            return bookings

    async def get_room(self, room_id: int) -> Room:
        """ Returns a room from a room id """
        # Query to get a room from the Room table
        async with self.conn.execute(
            '''
            SELECT room_id, room_name, building_id FROM Room WHERE room_id = ?;
            ''',
            (room_id,)
        ) as cur:

            result = await cur.fetchone() 

            if result: 
                return Room(
                    id=result[0],
                    name=result[1],
                    building_id=result[2]
                )
            return "Room not found." 

    async def get_room_facilities(self, room_id: int) -> list[str]:
        """ Returns a list of facilities for a room """
        # Query t get a list of facilities for the specified room

        #set below f.facility_id to f.facility_name when the sql file is changed
        async with self.conn.execute(
            '''
            SELECT f.facility_id 
            FROM Facility f
            LEFT JOIN Room_Facility rf ON f.facility_id = rf.facility_id
            WHERE rf.room_id = ?;
            ''',
            (room_id,)
        ) as cur:
        
            results = await cur.fetchall()  # Fetch all matching facilities
            facilities = [result[0] for result in results]  # Extract facility_ids into a list

            return facilities  # currently this returns ID's. Need to return actual facilities when necessary change is made in the sql file.
    
    async def close(self):  # for testing purposes
        await self.conn.commit()
        await self.conn.close()
        
