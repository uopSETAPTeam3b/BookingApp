from fastapi import HTTPException
from pydantic.dataclasses import dataclass
from api import API
from database import Room, Booking

class BookingManager(API):
    prefix = "/booking"
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/book", self.book_room, methods=["POST"])
        self.router.add_api_route("/cancel", self.cancel_room, methods=["POST"])
        self.router.add_api_route("/share", self.share_room, methods=["POST"])
        self.router.add_api_route("/get_bookings", self.get_bookings, methods=["POST"], response_model=list[Booking])
        self.router.add_api_route("/get_bookings_for_date", self.get_bookings_for_date, methods=["POST"], response_model=list[Booking])
        self.router.add_api_route("/get_booking", self.get_booking, methods=["POST"], response_model=Booking)
        self.router.add_api_route("/get_room", self.get_room, methods=["POST"], response_model=Room)

    @dataclass
    class BookRoom:
        token: str
        datetime: int
        room_id: int

    def book_room(self, booking: BookRoom) -> str:
        return ""
    
    @dataclass
    class CancelRoom:
        token: str
        booking_id: int

    def cancel_room(self, cancel: CancelRoom) -> str:
        raise HTTPException(500, {"error": "use appropriate status code"})
    
    @dataclass
    class ShareRoom:
        token: str
        booking_id: int
        username: int

    def share_room(self, share: ShareRoom) -> str:
        return ""
    
    @dataclass
    class GetBookings:
        token: str
    def get_bookings(self, bookings: GetBookings) -> list[Booking]:
        """Returns a list of active bookings for this user"""
        return []
    
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
    def get_booking(self, booking: GetBooking) -> Booking:
        return Booking(0, Room(0), 0)
    
    @dataclass
    class GetRoom:
        token: str
        room_id: int
    def get_room(self, room: GetRoom) -> Room:
        return Room(0)