==========
booking.py
==========

The `booking.py` module implements the BookingManager class, which handles all booking-related operations.

Overview
--------

The BookingManager class extends the base API class and provides endpoints for room booking, booking management, and room information retrieval. It includes methods for creating, editing, cancelling, and sharing bookings, as well as retrieving information about rooms and their facilities.

Class Definition
----------------

.. code-block:: python

    class BookingManager(API):
        prefix = "/booking"

        def __init__(self, nm: NotificationManager):
            super().__init__()
            self.nm = nm
            self.router.add_api_route("/book", self.book_room, methods=["POST"])
            self.router.add_api_route("/cancel", self.cancel_booking, methods=["POST"])
            self.router.add_api_route("/share", self.share_room, methods=["POST"])
            self.router.add_api_route("/edit_booking", self.edit_booking, methods=["POST"])
            self.router.add_api_route("/get_room_facilities", self.get_room_facilities, methods=["GET"])
            self.router.add_api_route("/get_bookings", self.get_bookings, methods=["POST"], response_model=list[Booking])
            self.router.add_api_route("/get_bookings_for_date", self.get_bookings_for_date, methods=["GET"], response_model=list[Booking])
            self.router.add_api_route("/get_booking", self.get_booking, methods=["POST"], response_model=Booking)
            self.router.add_api_route("/get_rooms", self.get_rooms, methods=["POST"], response_model=list[Room])
            self.router.add_api_route("/get_room", self.get_room, methods=["POST"], response_model=Room)
            self.router.add_api_route("/get_day_bookings", self.get_day_bookings, methods=["GET"], response_model=list[Booking])
            self.router.add_api_route("/get_booking_by_share_code", self.get_booking_by_share_code, methods=["GET"], response_model=Booking)

Key Methods
-----------

book_room
~~~~~~~~~

.. code-block:: python

    async def book_room(self, booking: BookRoom, background_tasks: BackgroundTasks) -> JSONResponse:
        """Books a room from a (only) validated user."""
        async with DB() as db:
            if not await db.verify_token(booking.token):
                raise HTTPException(status_code=404, detail="User not found")

            existing_booking = await db.find_booking(booking.room_id, booking.datetime)
            if existing_booking != "Booking doesn't exist.":
                raise HTTPException(status_code=409, detail="Room already booked")
            booked_room = await db.add_booking(
                booking.room_id, booking.datetime, booking.token, booking.duration
            )
            self.nm.booking_complete(booked_room, background_tasks=background_tasks)
            return JSONResponse(
                content={
                    "message": "Room booked successfully",
                    "booking_id": booked_room.id,
                    "access_code": booked_room.access_code,
                    "room_id": booked_room.room.id,
                    "room_name": booked_room.room.name,
                    "building_id": booked_room.building.id,
                    "building_name": booked_room.building.name,
                    "start_time": booked_room.time,
                    "duration": booked_room.duration
                },
                status_code=200,
            )

cancel_booking
~~~~~~~~~~~~~~

.. code-block:: python

    async def cancel_booking(self, cancel: CancelRoom, background_tasks: BackgroundTasks) -> str:
        """Cancels a room booking from a (only) validated user."""
        async with DB() as db:
            if not await db.verify_token(cancel.token):
                raise HTTPException(status_code=404, detail="User not found")
            booking = await db.get_booking(cancel.booking_id)
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")
            booking_time = datetime.fromtimestamp(booking.time, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            newStrike = False
            if 0 <= (booking_time - now).total_seconds() <= 1800: 
                strikes = await db.issue_strike_to_user(booking.user.id)
                newStrike = True
            else:
                strikes = await db.get_strikes(booking.user.id)

            await db.remove_booking(cancel.booking_id)
            self.nm.booking_cancelled(booking, strikes, newStrike, background_tasks=background_tasks)
            return "Booking cancelled"

edit_booking
~~~~~~~~~~~~

.. code-block:: python

    async def edit_booking(self, newBooking: EditBooking, background_tasks: BackgroundTasks) -> str:
        """Edits a room booking from a (only) validated user."""
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
                newBookedRoom = await db.get_booking(newBooking.old_booking_id)
                self.nm.booking_edited(oldBooking, newBookedRoom, background_tasks=background_tasks)
                return "Booking edited successfully"
            else:
                return "Booking edit failed"

share_room
~~~~~~~~~~

.. code-block:: python

    async def share_room(self, share: ShareRoom) -> str:
        """Shares a room booking from a validated user with another user."""
        async with DB() as db:
            if not await db.verify_token(share.token):
                raise HTTPException(status_code=404, detail="User not found")
            share_to = await db.get_user(share.username)
            if not share_to:
                raise HTTPException(status_code=404, detail="User not found")
           
            booking = await db.get_booking(share.booking_id)
            self.nm.share_booking(booking)
            return ""

get_booking_by_share_code
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def get_booking_by_share_code(self, token:str, share_code: str) -> JSONResponse:
        """Returns a booking from a share code."""
        async with DB() as db:
            if not await db.verify_token(token):
                raise HTTPException(status_code=404, detail="User not found")
            booking = await db.get_booking_by_share_code(share_code)
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")
            user = await db.get_user(token)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            if await db.add_shared_booking(booking.id, user.id):
                return JSONResponse(status_code=200, content={"message": "Booking shared successfully"})
            raise HTTPException(status_code=404, detail="Booking not found")

Room Information Methods
------------------------

get_rooms
~~~~~~~~~

.. code-block:: python

    async def get_rooms(self) -> list[Room]:
        """Returns a list of all rooms."""
        async with DB() as db:
            all_rooms = await db.get_rooms()
            if not all_rooms:
                raise HTTPException(status_code=404, detail="No rooms found")
            
            all_buildings = await db.get_buildings()
            if not all_buildings:
                raise HTTPException(status_code=404, detail="No buildings found")
            
            # Use the to_dict method to serialize the rooms and buildings
            rooms_data = [room.to_dict() for room in all_rooms]
            buildings_data = [b.to_dict() for b in all_buildings]
            
            # Ensure unique buildings by name
            unique_buildings = {b['name']: b for b in buildings_data}.values()
            
            return JSONResponse(content={"rooms": rooms_data, "buildings": list(unique_buildings)}, status_code=200)

get_room_facilities
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def get_room_facilities(self, token: str, room_id: int) -> JSONResponse:
        """Returns a list of facilities for a room."""
        async with DB() as db:
            if not await db.verify_token(token):
                raise HTTPException(status_code=404, detail="User not found")
            room = await db.get_room(room_id)
            if not room:
                raise HTTPException(status_code=404, detail="Room not found")
            facilities = await db.get_room_facilities(room_id)
            return JSONResponse(content={"facilities": facilities}, status_code=200)

Utility Methods
---------------

set_hour_on_same_day
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def set_hour_on_same_day(self, unix_timestamp: int, target_hour: int) -> int:
        """Sets the hour on the same day for a Unix timestamp."""
        dt = datetime.utcfromtimestamp(unix_timestamp)
        updated_dt = dt.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        return int(updated_dt.timestamp())

Data Classes
------------

The module defines several dataclasses for request and response structures:

.. code-block:: python

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
        
    @dataclass
    class CancelRoom:
        token: str
        booking_id: int

    @dataclass
    class ShareRoom:
        token: str
        booking_id: int
        username: str

    @dataclass
    class GetBookings:
        token: str

    @dataclass
    class BookingRequest:
        dateTime: int  

    @dataclass
    class GetBooking:
        token: str
        booking_id: int

    @dataclass
    class GetRoom:
        token: str
        room_id: int

Dependencies
------------

The module has the following dependencies:

- `fastapi.HTTPException`: For error handling
- `pydantic.dataclasses`: For request/response models
- `datetime`: For timestamp handling
- `api.API`: Base API class
- `database`: Database access
- `notification`: Email notifications
- `fastapi.responses.JSONResponse`: For structured API responses
- `dataclasses.asdict`: For dataclass serialization
- `fastapi.BackgroundTasks`: For asynchronous notification sending
