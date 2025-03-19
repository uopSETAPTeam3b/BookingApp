from fastapi import HTTPException
from pydantic.dataclasses import dataclass

from api import API
from database import Booking, DatabaseManager, Room, User
from notification import BookedRoom, CancelledRoom, NotificationManager, ShareBooking


class BookingManager(API):
    prefix = "/booking"

    def __init__(self, db: DatabaseManager, nm: NotificationManager):
        super().__init__()
        self.db = db
        self.nm = nm
        self.router.add_api_route("/book", self.book_room, methods=["POST"])
        self.router.add_api_route("/cancel", self.cancel_room, methods=["POST"])
        self.router.add_api_route("/share", self.share_room, methods=["POST"])
        self.router.add_api_route(
            "/get_bookings",
            self.get_bookings,
            methods=["POST"],
            response_model=list[Booking],
        )
        self.router.add_api_route(
            "/get_booking", self.get_booking, methods=["POST"], response_model=Booking
        )
        self.router.add_api_route(
            "/get_room", self.get_room, methods=["POST"], response_model=Room
        )

    @dataclass
    class BookRoom:
        token: str
        datetime: int
        room_id: int

    def book_room(self, booking: BookRoom) -> str:
        """ Books a room from a (only) validated user """
        if not self.db.verify_token(booking.token):
            raise HTTPException(status_code=404, detail="User not found")

        existing_booking = self.db.find_booking(booking.room_id, booking.datetime)
        if existing_booking:
            raise HTTPException(status_code=409, detail="Room already booked")
        booked_room = self.db.add_booking(
            booking.datetime, booking.room_id, booking.token
        )
        self.nm.booking_complete(booked_room)
        return "Booking successful"

    @dataclass
    class CancelRoom:
        token: str
        booking_id: int

    def cancel_room(self, cancel: CancelRoom) -> str:
        """ Cancels a room booking from a (only) validated user """
        if not self.db.verify_token(cancel.token):
            raise HTTPException(status_code=404, detail="User not found")
        booking = self.db.find_booking(cancel.booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        booking = self.db.remove_booking(cancel.booking_id)
        self.nm.booking_cancelled(booking)
        return "Booking cancelled"

    @dataclass
    class ShareRoom:
        token: str
        booking_id: int
        username: str

    def share_room(self, share: ShareRoom) -> str:
        """ Shares a room booking from a validated user with another user """
        if not self.db.verify_token(share.token):
            raise HTTPException(status_code=404, detail="User not found")
        share_to = self.db.get_user(share.username)
        if not share_to:
            # status code needs checking
            raise HTTPException(status_code=404, detail="User not found")
        booking = self.db.get_booking(share.booking_id)
        self.nm.share_booking(booking)
        return ""

    @dataclass
    class GetBookings:
        token: str

    def get_bookings(self, bookings: GetBookings) -> list[Booking]:
        """ Returns a list of active bookings for this user """
        if not self.db.verify_token(bookings.token):
            raise HTTPException(status_code=404, detail="User not found")
        all_bookings = self.db.get_all_bookings()
        user = self.db.get_user(bookings.token)
        user_bookings = []
        for booking in all_bookings:
            if booking.user == user:
                user_bookings.append(booking)
        return user_bookings

    @dataclass
    class GetBooking:
        token: str
        booking_id: int

    def get_booking(self, booking: GetBooking) -> Booking:
        """ Returns a single booking from a booking and user """
        if not self.db.verify_token(booking.token):
            raise HTTPException(status_code=404, detail="User not found")

        return self.db.find_booking(booking.booking_id)

    @dataclass
    class GetRoom:
        token: str
        room_id: int

    def get_room(self, room: GetRoom) -> Room:
        """ Returns a room from a room ID """
        searched_room = self.db.get_room(room.room_id)
        if not searched_room:
            raise HTTPException(status_code=404, detail="Room not found")
        return searched_room
