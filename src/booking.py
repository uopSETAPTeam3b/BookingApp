from fastapi import HTTPException
from pydantic.dataclasses import dataclass

from api import API
from database import Booking, DB, Room
from notification import NotificationManager
from fastapi.responses import JSONResponse

class BookingManager(API):
    prefix = "/booking"

    def __init__(self, nm: NotificationManager):
        super().__init__()
        self.nm = nm
        self.router.add_api_route("/book", self.book_room, methods=["POST"])
        self.router.add_api_route("/cancel", self.cancel_room, methods=["POST"])
        self.router.add_api_route("/share", self.share_room, methods=["POST"])
        self.router.add_api_route("/get_bookings", self.get_bookings, methods=["POST"], response_model=list[Booking])
        self.router.add_api_route("/get_bookings_for_date", self.get_bookings_for_date, methods=["POST"], response_model=list[Booking])
        self.router.add_api_route("/get_booking", self.get_booking, methods=["POST"], response_model=Booking)
        self.router.add_api_route("/get_rooms", self.get_rooms, methods=["POST"], response_model=list[Room])
        self.router.add_api_route("/get_room", self.get_room, methods=["POST"], response_model=Room)

    @dataclass
    class BookRoom:
        token: str
        datetime: int
        room_id: int

    async def book_room(self, booking: BookRoom) -> str:
        """ Books a room from a (only) validated user """
        async with DB() as db:
            if not await db.verify_token(booking.token):
                raise HTTPException(status_code=404, detail="User not found")

            existing_booking = await db.find_booking(booking.room_id, booking.datetime)
            if existing_booking:
                raise HTTPException(status_code=409, detail="Room already booked")
            booked_room = await db.add_booking(
                booking.room_id, booking.datetime, booking.token
            )
            self.nm.booking_complete(booked_room)
            return "Booking successful"

    @dataclass
    class CancelRoom:
        token: str
        booking_id: int

    async def cancel_room(self, cancel: CancelRoom) -> str:
        """ Cancels a room booking from a (only) validated user """
        async with DB() as db:
            if not await db.verify_token(cancel.token):
                raise HTTPException(status_code=404, detail="User not found")
            booking = await db.find_booking(cancel.booking_id)
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")
            booking = await db.remove_booking(cancel.booking_id)
            self.nm.booking_cancelled(booking)
            return "Booking cancelled"

    @dataclass
    class ShareRoom:
        token: str
        booking_id: int
        username: str

    async def share_room(self, share: ShareRoom) -> str:
        """ Shares a room booking from a validated user with another user """
        async with DB() as db:
            if not await db.verify_token(share.token):
                raise HTTPException(status_code=404, detail="User not found")
            share_to = await db.get_user(share.username)
            if not share_to:
                # status code needs checking
                raise HTTPException(status_code=404, detail="User not found")
            booking = await db.get_booking(share.booking_id)
            self.nm.share_booking(booking)
            return ""

    @dataclass
    class GetBookings:
        token: str

    async def get_bookings(self, bookings: GetBookings) -> list[Booking]:
        """ Returns a list of active bookings for this user """
        
        async with DB() as db:
            if not await db.verify_token(bookings.token):
                print("User not found")
                raise HTTPException(status_code=404, detail="User not found")
            all_bookings = await db.get_bookings_by_token(bookings.token)
            if not all_bookings:
                print("No bookings found")
                raise HTTPException(status_code=404, detail="No bookings found")
            return JSONResponse(content={"bookings": all_bookings}, status_code=200)

    @dataclass
    class GetBookingsForDate:
        date: str
    def get_bookings_for_date(self, bookings: GetBookingsForDate) -> list[Booking]:
        """Returns a list of bookings for this date"""
        return []
       
    @dataclass
    class GetBooking:
        token: str
        booking_id: int

    async def get_booking(self, booking: GetBooking) -> Booking:
        """ Returns a single booking from a booking and user """
        async with DB() as db:
            if not await db.verify_token(booking.token):
                raise HTTPException(status_code=404, detail="User not found")

            return await db.find_booking(booking.booking_id)

    def get_rooms(self) -> list[Room]:
        """Get all the rooms"""
        return []
    
    @dataclass
    class GetRoom:
        token: str
        room_id: int

    async def get_room(self, room: GetRoom) -> Room:
        """ Returns a room from a room ID """
        async with DB() as db:
            searched_room = await db.get_room(room.room_id)
            if not searched_room:
                raise HTTPException(status_code=404, detail="Room not found")
            return searched_room
