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
    def __init__(self, file: str = "database.db", create_script: str = "src/create.sql"):
        pass
    def find_booking(self, room: Room, time: int):
        return None
    def find_booking(self, id: int):
        return None
    def add_booking(self, room: Room, time: int, token: int):
        user = self.get_user(token) 
        return None
    def remove_booking(self, id: int):
        return None
    def get_all_bookings(self):
        return []
    def get_room(self, room_id: int):
        return None
    def get_user(token:int):
        return None
    def get_user(booking_id: int):
        return None