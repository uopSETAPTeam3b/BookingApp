from pydantic.dataclasses import dataclass
class NotificationManager:
    def __init__(self):
        super().__init__()
    @dataclass
    class BookedRoom:
        time : int
        room_id : int
        user : str
    def booking_complete(self, booking: BookedRoom) -> str:
        #send email to user saying room has been booked
        return "Booking complete"
    
    @dataclass
    class CancelledRoom:
        time : int
        room_id : int
        user : str

    def booking_complete(self, booking: CancelledRoom) -> str:
        #send email to user saying booking has been cancelled
        return "Booking cancelled"
    
    @dataclass
    class ShareBooking:
        time : int
        booking_id : int
        user : str
    def share_booking(self, booking: ShareBooking) -> str:
        #send email to user sharing the booking details
        return "Share complete"