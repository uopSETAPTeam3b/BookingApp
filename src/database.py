from pydantic.dataclasses import dataclass
import sqlite3

@dataclass
class Room:
    id: int

@dataclass
class Booking:
    id: int
    room: Room
    time: int

@dataclass
class User:
    username: str

class DatabaseManager:
    """Database class the has functions mapped to identified SQL queries that are necersarry"""
    def __init__(self, file: str = "database.db", create_script: str = "src/create.sql"):
        pass
    def find_booking(self, room: Room, time: int):
        return None
    def find_booking(self, id: int):
        return None
    def add_booking(self, room: Room, time: int, user: User):
        return None
    def remove_booking(self, id: int):
        return None