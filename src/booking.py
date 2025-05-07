from fastapi import HTTPException
from pydantic.dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from api import API
from database import Booking, DB, Room
from notification import NotificationManager
from fastapi.responses import JSONResponse
from dataclasses import asdict
from fastapi import BackgroundTasks
class BookingManager(API):
    prefix = "/booking"

    def __init__(self, nm: NotificationManager):
        super().__init__()
        self.nm = nm
        self.router.add_api_route("/book", self.book_room, methods=["POST"])
        self.router.add_api_route("/cancel", self.cancel_booking, methods=["POST"])
        self.router.add_api_route("/share", self.share_room, methods=["POST"])
        self.router.add_api_route("/edit_booking", self.edit_booking, methods=["POST"])
        self.router.add_api_route("/get_bookings", self.get_bookings, methods=["POST"], response_model=list[Booking])
        self.router.add_api_route("/get_bookings_for_date", self.get_bookings_for_date, methods=["GET"], response_model=list[Booking])
        self.router.add_api_route("/get_booking", self.get_booking, methods=["POST"], response_model=Booking)
        self.router.add_api_route("/get_rooms", self.get_rooms, methods=["POST"], response_model=list[Room])
        self.router.add_api_route("/get_room", self.get_room, methods=["POST"], response_model=Room)
        self.router.add_api_route("/get_day_bookings", self.get_day_bookings, methods=["GET"], response_model=list[Booking])
    @dataclass
    class BookRoom:
        token: str
        datetime: int
        room_id: int
        duration: int
    @dataclass
    class EditBooking:
        token: str
        dayTime: int
        room_id: int
        duration: int
        old_booking_id: int

    def set_hour_on_same_day(self, unix_timestamp: int, target_hour: int) -> int:
        # Convert to UTC datetime
        dt = datetime.utcfromtimestamp(unix_timestamp)

        # Replace the hour, and reset minutes, seconds, microseconds
        updated_dt = dt.replace(hour=target_hour, minute=0, second=0, microsecond=0)

        # Return as Unix timestamp (seconds)
        return int(updated_dt.timestamp())
    
    async def edit_booking(self, newBooking: EditBooking) -> str:
        """ Edits a room booking from a (only) validated user """
        async with DB() as db:
            if not await db.verify_token(newBooking.token):
                raise HTTPException(status_code=404, detail="User not found")
            oldBooking = await db.get_booking(newBooking.old_booking_id)
            if not oldBooking:
                raise HTTPException(status_code=404, detail="Booking not found")
            
            date_time = self.set_hour_on_same_day(oldBooking.time, newBooking.dayTime)
            if await db.edit_booking(
                newBooking.old_booking_id, newBooking.room_id, date_time, newBooking.duration
            ):
                #self.nm.booking_edited(oldBooking, newBooking)
                return "Booking edited successfully"
            else:
                return "Booking edit failed"
            

        
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

    async def cancel_booking(self, cancel: CancelRoom, background_tasks: BackgroundTasks) -> str:
        """ Cancels a room booking from a (only) validated user """
        async with DB() as db:
            if not await db.verify_token(cancel.token):
                raise HTTPException(status_code=404, detail="User not found")
            booking = await db.get_booking(cancel.booking_id)
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")
            booking_time = datetime.fromtimestamp(booking.time, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            newStrike = False
            if 0 <= (booking_time - now).total_seconds() <= 1800:  # 1800 seconds = 30 minutes
                
                strikes = await db.issue_strike_to_user(booking.user_id)
                newStrike = True
                

            await db.remove_booking(cancel.booking_id)
            self.nm.booking_cancelled(booking, strikes, newStrike, background_tasks)
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

    

    async def get_bookings(self, bookings: GetBookings):
        """ Returns a list of active bookings for this user """

        async with DB() as db:
            if not await db.verify_token(bookings.token):
                raise HTTPException(status_code=404, detail="User not found")

            all_bookings = await db.get_bookings_by_token(bookings.token)
            if not all_bookings:
                raise HTTPException(status_code=404, detail="No bookings found")

            # Convert each Booking object to a dict
            booking_dicts = [asdict(b) for b in all_bookings]
            return JSONResponse(content={"bookings": booking_dicts}, status_code=200)
    @dataclass
    class BookingRequest:
        dateTime: int  # Ensure this matches the incoming data

    async def get_bookings_for_date(self, dateTime:int):
        
        print(f"Received dateTime: {dateTime}")
        """Returns a list of bookings for the given date"""
        async with DB() as db:
            # Convert the Unix timestamp to a date (assuming it's in UTC)
            date_obj = datetime.utcfromtimestamp(dateTime)
            # Use this date to get bookings for that specific day
            bookings = await db.get_bookings_by_date(date_obj.date())

            if not bookings:
                return JSONResponse(content={"bookings": []}, status_code=200)

            booking_list = []
            for booking in bookings:
                booked = {
                    "booking_id": booking.id,
                    "building_id": booking.building.id,
                    "room_name": booking.room.name,
                    "building_name": booking.building.name,
                    "room_id": booking.room.id,
                    "start_time": booking.time,
                    "duration": booking.duration,
                    "access_code": booking.access_code,
                    "address_1": booking.building.address_1,
                    "address_2": booking.building.address_2,
                    "opening_time": booking.building.opening_time,
                    "closing_time": booking.building.closing_time
                }
                booking_list.append(booked)

            return JSONResponse(content={"bookings": booking_list})
    
    async def get_day_bookings(self, booking_id: int):
        """Handles a route to get all bookings for the same day as the given booking_id."""
        async with DB() as db:
            # Get the date of the booking from booking_id
            booking_date = await db.get_booking_date(booking_id)
            if not booking_date:
                raise HTTPException(status_code=404, detail="Booking not found")

            # Get bookings for that date
            bookings = await db.get_bookings_by_date(booking_date)

            # Format the bookings as a list of dicts for JSON response
            booking_list = []
            for booking in bookings:
                booked = {
                    "booking_id": booking.id,
                    "building_id": booking.building.id,
                    "room_name": booking.room.name,
                    "building_name": booking.building.name,
                    "room_id": booking.room.id,
                    "start_time": booking.time,
                    "duration": booking.duration,
                    "access_code": booking.access_code,
                    "address_1": booking.building.address_1,
                    "address_2": booking.building.address_2,
                    "opening_time": booking.building.opening_time,
                    "closing_time": booking.building.closing_time
                }
                booking_list.append(booked)
                
                

            # Return the list of bookings as a JSON response
            return JSONResponse(content={"bookings": booking_list})
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

    async def get_rooms(self) -> list[Room]:
        """ Returns a list of all rooms """
        async with DB() as db:
            all_rooms = await db.get_rooms()
            if not all_rooms:
                raise HTTPException(status_code=404, detail="No rooms found")
            all_buildings = await db.get_buildings()
            if not all_buildings:
                raise HTTPException(status_code=404, detail="No buildings found")
            rooms_data = [room.__dict__ for room in all_rooms]
            buildings_data = [b.__dict__ for b in all_buildings]
            # Optional: Remove duplicates by building name (or ID)
            unique_buildings = {b['name']: b for b in buildings_data}.values()
            return JSONResponse(content={"rooms": rooms_data, "buildings": buildings_data}, status_code=200)
    
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
