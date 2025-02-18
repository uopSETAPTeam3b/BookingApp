from fastapi import HTTPException
from pydantic.dataclasses import dataclass
from api import API
from database import Room, Booking, User, DatabaseManager

class BookingManager(API):
    prefix = "/booking"
    def __init__(self):
        super().__init__()
        self.router.add_api_route("/book", self.book_room, methods=["POST"])
        self.router.add_api_route("/cancel", self.cancel_room, methods=["POST"])
        self.router.add_api_route("/share", self.share_room, methods=["POST"])
        self.router.add_api_route("/get_bookings", self.get_bookings, methods=["POST"], response_model=list[Booking])
        self.router.add_api_route("/get_booking", self.get_booking, methods=["POST"], response_model=Booking)
        self.router.add_api_route("/get_room", self.get_room, methods=["POST"], response_model=Room)

    @dataclass
    class BookRoom:
        token: str
        datetime: int
        room_id: int
    
    def book_room(self, booking: BookRoom) -> str:
        # check token first idk how to do that
        if not DatabaseManager.verify_token(booking.token):
            raise HTTPException(status_code=404, detail="User not found")
        
        existing_booking = DatabaseManager.find_booking(booking.datetime, booking.room_id)
        if existing_booking:
            raise HTTPException(status_code= 409, detail="Room already booked")
        else:
            DatabaseManager.add_booking(booking.datetime, booking.room_id, booking.token)
            return "Booking successful"
    
    @dataclass
    class CancelRoom:
        token: str
        booking_id: int

    def cancel_room(self, cancel: CancelRoom) -> str:
        if not DatabaseManager.verify_token(cancel.token):
            raise HTTPException(status_code=404, detail="User not found")
        booking = DatabaseManager.find_booking(cancel.booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        else:
            DatabaseManager.remove_booking(cancel.booking_id)
            return "Booking cancelled"
        raise HTTPException(500, {"error": "use appropriate status code"})
    
    @dataclass
    class ShareRoom:
        token: str
        booking_id: int
        username: str
    def share_room(self, share: ShareRoom) -> str:
        if not DatabaseManager.verify_token(share.token):
            raise HTTPException(status_code=404, detail="User not found")
        share_to = DatabaseManager.get_user(share.username)
        if not share_to:
            #status code needs checking
            raise HTTPException(status_code=404, detail="User not found")
        return ""
    
    @dataclass
    class GetBookings:
        token: str
    def get_bookings(self, bookings: GetBookings) -> list[Booking]:
        """Returns a list of active bookings for this user"""
        if not DatabaseManager.verify_token(bookings.token):
            raise HTTPException(status_code=404, detail="User not found")
        all_bookings = DatabaseManager.get_all_bookings()
        user = DatabaseManager.get_user(bookings.token)
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
        if not DatabaseManager.verify_token(booking.token):
            raise HTTPException(status_code=404, detail="User not found")
        
        return BookingManager.find_booking(booking.booking_id) 
       
    @dataclass
    class GetRoom:
        token: str
        room_id: int
    def get_room(self, room: GetRoom) -> Room:
        # check token first idk how to do that
        searched_room = DatabaseManager.get_room(room.room_id)
        if not searched_room:
            raise HTTPException(status_code=404, detail="Room not found")
        return searched_room