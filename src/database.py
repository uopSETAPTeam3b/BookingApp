import sqlite3

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
        pass

    def create_database(self):
        """create database and tables"""
        pass

    def get_email(self, user_id: int) -> str:
        """ Gets a email from a user """
        # takes a user_id and returns the email of the user
        email = ""
        return email

    def verify_token(self, token: str) -> bool:
        """ Verifies the token """
        user = self.get_user(token)
        if not user:
            return False
        return True

    def find_booking(self, room: int, time: int) -> Booking:
        """ Returns a booking if found at a room and time """
        # query must check DB for booking at room and time
        return Booking(0, User("", ""), Room(0), 0)

    def get_booking(self, booking_id: int) -> Booking:
        """ Returns a booking from a booking id """
        # query must get the booking of booking_id
        return Booking(0, User("", ""), Room(0), 0)

    def add_booking(self, room: Room, time: int, token: str) -> None:
        """ Adds a booking to the database  """
        # query must insert booking into database
        # user is found from token
        user = self.get_user(token)
        if not user:
            return None
        return None

    def remove_booking(self, booking_id: int) -> Booking:
        """ Removes a booking from the database from booking id """
        # delete booking from database
        booking = self.get_booking(id)
        return booking

    def get_all_bookings(self) -> list[Booking]:
        """ Returns a list of all future/current bookings """
        # query must get all future/current bookings
        return []

    def get_room(self, room_id: int) -> Room:
        """ Returns a room from a room id """
        # query must get a room from room_id
        return Room(0)

    def get_user(self, token: str) -> User:
        """ Returns a user from a token """
        # query must get a user from token
        return User("", "")

    def get_user_from_booking(self, booking_id: int) -> User:
        """ Returns a user from a booking id """
        # query must get a user from booking_id
        return User("", "")
    def get_user_email(self, user: User) -> str:
        """ Returns a user email from a user object """
        # query must get a user email from user object
        return ""
