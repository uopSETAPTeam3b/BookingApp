from pydantic.dataclasses import dataclass
import sqlite3

@dataclass
class Room:
    id: int

@dataclass
class User:
    username: str

@dataclass
class Booking:
    id: int
    user: User
    room: Room
    time: int

class DatabaseManager:
    """Database class the has functions mapped to identified SQL queries that are necersarry"""
    #sql queries should be put into these functions to interact with the database
    def __init__(self, file: str = "database.db", create_script: str = "src/create.sql"):
        pass
    def verify_token(self, token: str) -> bool:
        user = self.get_user(token) 
        if not user:
            return False
        return True
    def find_booking(self, room: Room, time: int) -> Booking:
        # return booking object using room and time
        return Booking(0, User(""), Room(0), 0)
    def get_booking(self, id: int) -> Booking:
        # return booking object using id
        return Booking(0, User(""), Room(0), 0)
    def add_booking(self, room: Room, time: int, token: str) -> None:
        # add booking to database
        user = self.get_user(token) 
        if not user:
            return None
        return None
    def remove_booking(self, id: int) -> None:
        # remove booking from database
        booking = self.get_booking(id)
        return None
    def get_all_bookings(self) -> list[Booking]:
        # gets a list of all future bookings (not past)
        return []
    def get_room(self, room_id: int) -> Room:
        # get room object using room_id
        return Room(0)
    def get_user(self, token:str) -> User:
        # get user object using token
        return User("")
    def get_user_from_booking(self, booking_id: int) -> User:
        # get user object using booking_id
        return User("")
    