import os
from typing import Optional
from datetime import datetime
import time
import secrets
import aiosqlite
from pydantic.dataclasses import dataclass
import random
import string
@dataclass
class Facility:
    id: int
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    def to_dict(self):
        return {"id": self.id, "name": self.name}
    
@dataclass
class Room:
    id: int
    name:str
    building_id: int
    type: Optional[str] = None
    capacity: Optional[int] = None
    facilities: Optional[list[Facility]] = None
    def to_dict(self):
        # Convert the list of Facility objects to dictionaries
        return {
            "id": self.id,
            "name": self.name,
            "building_id": self.building_id,
            "type": self.type,
            "capacity": self.capacity,
            "facilities": [facility.to_dict() for facility in (self.facilities or [])],
        }

@dataclass
class LoggedInUser:
    token: str
@dataclass
class User:
    username: str
    email: str
    id: Optional[int] = None
    role: Optional[str] = None
    strikes: Optional[int] = None


@dataclass
class Booking:

    id: int
    room: Room
    time: int
    user: Optional[User] = None
    access_code: Optional[str] = None
    share_code: Optional[str] = None
    shared: Optional[bool] = None
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
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address_1": self.address_1,
            "address_2": self.address_2,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
        }
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
    insert_script: str = "src/insert.sql"
    
    def __init__(self, file: str | None = None, create: str | None = None, insert: str | None = None):
        DatabaseManager.file = file or DatabaseManager.file
        DatabaseManager.create_script = create or DatabaseManager.create_script
        DatabaseManager.insert_script = insert or DatabaseManager.insert_script
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

        
        async with self.conn.execute("""
            SELECT user_id, username, email, phone_number, offence_count, role
            FROM User WHERE user_id = ?
        """, (user_id,)) as cursor:
            user = await cursor.fetchone()

        if not user:
            return {"error": "User not found"}

        
        async with self.conn.execute("""
            SELECT U.university_name, U.university_id
            FROM University U
            JOIN User ON User.university_id = U.university_id
            WHERE User.user_id = ?
        """, (user_id,)) as cursor:
            university = await cursor.fetchone()
        
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "phone_number": user[3],
            "offence_count": user[4],
            "role": user[5],
            "university": university[0] if university else None,
            "university_id": university[1] if university else None
        }
    async def get_email(self, user_id: int) -> str:
        """ Gets a email from a user """
        
        

        async with self.conn.execute("SELECT email FROM User WHERE user_id = ?", (user_id,)) as cursor:
            result = await self.conn.fetchone()

        if result:
            return result[0]  
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
                    return None  
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
        user = await self.get_user(token)
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
            SELECT  u.username, u.email, u.role, u.user_id, u.offence_count
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
                    role=result[2],
                    strikes=result[4]
                )
        return None
    async def enterRoom(self, room_id, room_code, datetime):
       
        bookings = await self.get_all_bookings()
        for booking in bookings:
            if booking.room.id == room_id and booking.access_code == room_code:
                if booking.time <= datetime <= booking.time + booking.duration * 3600:
                    print("Booking found")
                    async with DB() as db:
                        await db.execute(
                            """
                            UPDATE Booking
                            SET completed = ?
                            WHERE room_id = ? AND start_time = ?
                            """,
                            (1, room_id, datetime)
                        )
                    return True
        return False
        
        
        
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
        async with self.conn.execute(
            "SELECT user_id, username, email, role FROM User WHERE username = ?",
            (username,)
        ) as cur:
            if result := await cur.fetchone():
                return User(
                    
                    username=result[1],
                    email=result[2],
                    
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
                    
                    username=result[1],
                    email=result[2],
                    
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

    async def find_booking(self, room_id: int, time: int) -> Booking | str:
        """ Returns a booking if found at a room and time """
        async with await self.conn.execute(
            '''
            SELECT b.booking_id, b.building_id, b.room_id, b.start_time, b.duration, b.access_code, ub.user_id,
                   r.room_name
            FROM Booking b
            JOIN User_Booking ub ON b.booking_id = ub.booking_id
            JOIN Room r ON b.room_id = r.room_id
            WHERE b.room_id = ? AND b.start_time <= ? AND (b.start_time + b.duration * 3600) > ?
            ''',
            (room_id, time, time)
        ) as cur:
            result = await cur.fetchone()
            
            if result:
                booking_id = result[0]
                building_id = result[1]
                room_id = result[2]
                start_time = result[3]
                duration = result[4]
                access_code = result[5]
                user_id = result[6]
                room_name = result[7]

                user = await self.get_user_from_booking(user_id)  
                room = Room(room_id, room_name, building_id)

                return Booking(booking_id,room,start_time, user, access_code, duration)
            return "Booking doesn't exist."
    async def get_booking(self, booking_id: int) -> Booking:
        """ Returns a booking from a booking_id """
        
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
            
            if result:  
                booking_id = result[0]  
                building_id = result[1]  
                room_id = result[2]      
                start_time = result[3]   
                duration = result[4]     
                access_code = result[5]  
                user_id = result[6]      

                
                user = await self.get_user_from_id(user_id)
                building = await self.get_building(building_id)  
                room = await self.get_room(room_id)
                return Booking(booking_id, room, start_time, user, building = building, access_code=access_code, duration=duration)
            return None
        
    async def get_user_from_id(self, user_id: int) -> User:
        """ Returns a user from a user_id """
        
        async with self.conn.execute(
            '''
            SELECT user_id, username, email, role FROM User WHERE user_id = ?;
            ''',
            (user_id,)
        ) as cur:

            result = await cur.fetchone()
            if result:
                return User(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    role=result[3]
                )
            return None
        
    async def get_rooms(self) -> list[Room]:
        """ Returns a list of all rooms with their facilities """

        async with self.conn.execute(
            '''
            SELECT 
                r.room_id, r.room_name, r.building_id, r.room_type, r.room_capacity,
                f.facility_id, f.facility_name, f.facility_description
            FROM Room r
            LEFT JOIN Room_Facility rf ON r.room_id = rf.room_id
            LEFT JOIN Facility f ON rf.facility_id = f.facility_id
            ORDER BY r.room_id;
            '''
        ) as cur:
            results = await cur.fetchall()
            rooms = {}
            for row in results:
                room_id = row[0]
                if room_id not in rooms:
                    rooms[room_id] = Room(
                        id=room_id,
                        name=row[1],
                        building_id=row[2],
                        type=row[3],
                        capacity=row[4],
                        facilities=[]
                    )
                if row[5] is not None:
                    facility = Facility(
                        id=row[5],
                        name=row[6],
                        description=row[7]
                    )
                    rooms[room_id].facilities.append(facility)

            return list(rooms.values())

    async def get_buildings(self) -> list[Building]:
        """ Returns a list of all buildings """
        
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

                
                buildings.append(Building(
                    id=building_id,
                    name=building_name,
                    address_1=address_1,
                    address_2=address_2,
                    opening_time=opening_time,
                    closing_time=closing_time
                ))
            return buildings  
    async def add_booking(self, room_id: int, time: int, token: str, duration: int) -> Booking:
        """ Adds a booking to the database """
        async with DB() as db:
            user = await db.get_user(token)  
            if not user:
                return Booking(0, User("", ""), Room(0), 0)

            room = await db.get_room(room_id)  
            if not room:
                return Booking(0, User("", ""), Room(0), 0)

            building_id = room.building_id
            building = await db.get_building(building_id) 
            access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            share_code = str(''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))
            async with await db.conn.execute(
                '''
                INSERT INTO Booking (building_id, room_id, start_time, duration, access_code, share_code)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (building_id, room_id, time, duration, access_code, share_code)
            ) as cursor:
                await db.conn.commit()

            booking_id = cursor.lastrowid

            await db.conn.execute(
                '''
                INSERT INTO User_Booking (user_id, booking_id)
                VALUES (?, ?)
                ''',
                (user.id, booking_id)
            )
            await db.conn.commit()

            return Booking(booking_id, room, time, user, access_code, share_code, 0, duration, building) 
    async def add_shared_booking(self, booking_id:int, user_id:int):
        """ Adds a shared booking to the database """
        try:
            await self.conn.execute(
                '''
                INSERT INTO User_Booking (user_id, booking_id, shared)
                VALUES (?, ?, ?)
                ''',
                (user_id, booking_id, 1)
            )
            await self.conn.commit()
            return True
        except Exception as e:
            print("Error adding shared booking:", e)
            return False
     
    async def remove_booking(self, booking_id: int) -> bool:
        """ Removes a booking from the database using the booking_id """

        booking = await self.get_booking(booking_id)

        if isinstance(booking, Booking):  

            await self.conn.execute("DELETE FROM User_Booking WHERE booking_id = ?", (booking_id,))  

            await self.conn.execute("DELETE FROM Booking WHERE booking_id = ?", (booking_id,))  

            await self.conn.commit()

            return True
        return False  

    async def get_building(self, building_id: int) -> Building:
        """ Returns a building from a building_id """
        
        async with self.conn.execute(
            '''
            SELECT building_id, building_name, address_1, address_2, opening_time, closing_time FROM Building WHERE building_id = ?;
            ''',
            (building_id,)
        ) as cur:

            result = await cur.fetchone()
            if result:
                return Building(
                    id=result[0],
                    name=result[1],
                    address_1=result[2],
                    address_2=result[3],
                    opening_time=result[4],
                    closing_time=result[5]
                )
            return None  
    async def get_all_bookings(self) -> list[Booking]:
        """ Returns a list of all future/current bookings """
        
        async with await self.conn.execute(
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

            results = await cur.fetchall()  
            bookings = []  

            for result in results:
                booking_id = result[0]  
                building_id = result[1]  
                room_id = result[2]      
                room_name = result[3]
                start_time = result[4]   
                duration = result[5]      
                access_code = result[6]   
                user_id = result[7]       

                
                user = self.get_user_from_booking(user_id)

                
                room = Room(id=room_id,
                            name=room_name,
                            building_id=building_id)

                
                bookings.append(Booking(id=booking_id, user=user, room=room, time=start_time))

            return bookings  
        
    async def get_bookings_by_token(self, token: str) -> list[Booking]:
        """Returns all current/future bookings for a user identified by their token, including building info"""
        
        async with self.conn.execute(
            "SELECT user_id FROM Authentication WHERE token = ?", (token,)
        ) as cur:
            result = await cur.fetchone()
            
            if result is None:
                return []  
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
                b.share_code,
                bl.building_name, 
                bl.address_1, 
                bl.address_2, 
                bl.opening_time, 
                bl.closing_time,
                ub.shared
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
                b.start_time DESC;
            ''',
            (user_id,)
        ) as cur:
            results = await cur.fetchall()
            bookings = []

            for result in results:
                booking_id = result[0]
                building_id = result[1]
                room_id = result[2]
                room_name = result[3]  
                start_time = result[4]
                duration = result[5]
                access_code = result[6]
                share_code = result[7]
                building_name = result[8]
                address_1 = result[9]
                address_2 = result[10]
                opening_time = result[11]
                closing_time = result[12]
                shared = result[13]

                room = Room(id=room_id, name=room_name, building_id=building_id)  
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
                    duration=duration,
                    access_code=access_code,
                    share_code=share_code,
                    shared=shared
                ))
            return bookings
    async def get_booking_by_share_code(self, share_code: str) -> Booking:
        """ Returns a booking from a share code """
        
        async with self.conn.execute(
            '''
            SELECT b.booking_id
            FROM Booking b
            WHERE b.share_code = ?
            ''',
            (share_code,)
        ) as cur:

            result = await cur.fetchone()
            
            if result:  
                booking_id = result[0]     

                
                booking = await self.get_booking(booking_id)
                return booking
            return None
    async def get_room(self, room_id: int) -> Room:
        """ Returns a room from a room id """
        
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
            return None;
    async def get_bookings_by_date(self, booking_date: str) -> list[Booking]:
        """Gets all bookings for the same day as the given date."""
        
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
                    Building bl ON b.building_id = bl.building_id
                JOIN 
                    Room r ON b.room_id = r.room_id  
                WHERE 
                    DATE(datetime(b.start_time, 'unixepoch')) = ?
                ORDER BY 
                    b.start_time;
            ''', (booking_date,)
        ) as cur:
            results = await cur.fetchall()

        bookings = []
        for result in results:
            booking_id = result[0]
            building_id = result[1]
            room_id = result[2]
            room_name = result[3]
            start_time = result[4]
            duration = result[5]
            access_code = result[6]
            building_name = result[7]
            address_1 = result[8]
            address_2 = result[9]
            opening_time = result[10]
            closing_time = result[11]

            room = Room(id=room_id,
                        name=room_name,
                        building_id=building_id
                        )
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
                building_id=building_id,
                user=None,  
                room=room,
                time=start_time,
                building=building,
                duration=duration
            ))

        return bookings
    
    async def add_user_to_university(self, user_id: int, university_id: int) -> bool:
        """ Adds a user to a university """
        try:
            
            await self.conn.execute(
                '''
                INSERT INTO User_University (user_id, university_id) 
                VALUES (?, ?);
                ''',
                (user_id, university_id)
            )
            await self.conn.commit()
            return True
        except Exception as e:
            print("Error adding user to university:", e)
            return False
    async def get_uni_requests(self, university_id: int) -> list[User]:
        """ Returns a list of all users who have requested to join a university """
        
        async with self.conn.execute(
            '''
            SELECT u.user_id, u.username, u.email, u.role, uu.status
            FROM User u
            JOIN User_University uu ON u.user_id = uu.user_id
            WHERE uu.university_id = ?;
            ''',
            (university_id,)
        ) as cur:
            results = await cur.fetchall()
            users = []
            for result in results:
                users.append({
                    "id": result[0],
                    "username": result[1],
                    "email": result[2],
                    "role": result[3],
                    "status": result[4],
                })
            return users
    async def accept_request(self,user_id: int, university_id:int) -> bool:
        """ Adds a user to a university """
        try:
            
            await self.conn.execute(
                '''
                UPDATE User_University
                SET status = '1'
                WHERE user_id = ? AND university_id = ?;
                ''',
                (user_id, university_id)
            )
            await self.conn.commit()
            return True
        except Exception as e:
            print("Error adding user to university:", e)
            return False
        

    async def get_universities(self) -> list[str]:
        """ Returns a list of all universities """
        
        async with self.conn.execute(
            '''
            SELECT university_name, university_id FROM University;
            '''
        ) as cur:
            results = await cur.fetchall()
            universities = []
            for result in results:
                university_name = result[0]
                university_id = result[1]

                
                universities.append({
                    "name": university_name,
                    "id": university_id
                })
            return universities
    async def get_strikes(self, user_id: int) -> int:
        """ Gets the number of strikes for a user """
        
        async with self.conn.execute(
            '''
            SELECT offence_count FROM User WHERE user_id = ?;
            ''',
            (user_id,)
        ) as cur:
            result = await cur.fetchone()
            if result:
                return result[0]
            return 0

    async def get_booking_date(self, booking_id: int) -> str:
        """Gets the date of the given booking ID."""
        
        async with self.conn.execute(
            "SELECT start_time FROM Booking WHERE booking_id = ?", (booking_id,)
        ) as cur:
            result = await cur.fetchone()
            if result is None:
                return None  

            start_time = int(result[0])         
            booking_date = datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d')
            return booking_date


    async def get_room_facilities(self, room_id: int) -> list[str]:
        """ Returns a list of facilities for a room """
        async with self.conn.execute(
            '''
            SELECT f.facility_id 
            FROM Facility f
            LEFT JOIN Room_Facility rf ON f.facility_id = rf.facility_id
            WHERE rf.room_id = ?;
            ''',
            (room_id,)
        ) as cur:
        
            results = await cur.fetchall()  
            facilities = [result[0] for result in results]  

            return facilities  
    
    async def close(self):  
        await self.conn.commit()
        await self.conn.close()
        
