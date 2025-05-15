===========
database.py
===========

The `database.py` module defines the data models and database access methods for the BookingApp system.

Overview
--------

The database.py module implements the data access layer of the application. It provides data models using Python dataclasses, a DatabaseManager class for SQL operations, and a DB context manager for handling database connections. The module includes methods for CRUD operations on users, bookings, rooms, and other entities.

Data Models
-----------

The module defines several dataclasses that represent the database entities:

Facility
~~~~~~~~

.. code-block:: python

    @dataclass
    class Facility:
        id: int
        name: str
        type: Optional[str] = None
        description: Optional[str] = None
        
        def to_dict(self):
            return {"id": self.id, "name": self.name}

Room
~~~~

.. code-block:: python

    @dataclass
    class Room:
        id: int
        name: str
        building_id: int
        type: Optional[str] = None
        capacity: Optional[int] = None
        facilities: Optional[list[Facility]] = None
        
        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "building_id": self.building_id,
                "type": self.type,
                "capacity": self.capacity,
                "facilities": [facility.to_dict() for facility in (self.facilities or [])],
            }

User
~~~~

.. code-block:: python

    @dataclass
    class User:
        username: str
        email: str
        id: Optional[int] = None
        role: Optional[str] = None

LoggedInUser
~~~~~~~~~~~~

.. code-block:: python

    @dataclass
    class LoggedInUser:
        token: str

Booking
~~~~~~~

.. code-block:: python

    @dataclass
    class Booking:
        id: int
        room: Room
        time: int
        user: Optional[User] = None
        access_code: Optional[str] = None
        share_code: Optional[str] = None
        shared: Optional[bool] = None
        duration: Optional[float] = None
        building: Optional["Building"] = None

Building
~~~~~~~~

.. code-block:: python

    @dataclass
    class Building:
        id: int
        name: str
        address_1: str
        address_2: str
        opening_time: str
        closing_time: str
        
        def to_dict(self):
            return {
                "id": self.id,
                "name": self.name,
                "address_1": self.address_1,
                "address_2": self.address_2,
                "opening_time": self.opening_time,
                "closing_time": self.closing_time,
            }

Database Context Manager
------------------------

The DB class provides a context manager for database operations:

.. code-block:: python

    class DB:
        def __init__(self):
            self.db = None

        async def __aenter__(self) -> "DatabaseManager":
            self.db = await DatabaseManager.create()
            return self.db

        async def __aexit__(self, exc_type, exc_val, traceback):
            if self.db:
                await self.db.close()

Usage:

.. code-block:: python

    async with DB() as db:
        # Perform database operations
        user = await db.get_user(token)
        bookings = await db.get_bookings_by_token(token)

Database Manager
----------------

The DatabaseManager class provides methods for interacting with the SQLite database:

.. code-block:: python

    class DatabaseManager:
        """Database class the has functions mapped to identified SQL queries that are necessary"""

        file: str = "database.db"
        create_script: str = "src/create.sql"
        insert_script: str = "src/insert.sql"

        def __init__(self, file: str | None = None, create: str | None = None, insert: str | None = None):
            DatabaseManager.file = file or DatabaseManager.file
            DatabaseManager.create_script = create or DatabaseManager.create_script
            DatabaseManager.insert_script = insert or DatabaseManager.insert_script
            self.conn: aiosqlite.Connection | None = None

Key Database Methods
--------------------

User Authentication
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def create_token(self, user: User) -> str:
        """Generate and store an authentication token for the given username."""
        # Implementation...

    async def verify_token(self, token: str) -> bool:
        """Verifies the token."""
        # Implementation...

    async def create_user(self, username: str, password: str, email: str) -> Optional[str]:
        """Create a new user and return authentication token."""
        # Implementation...

    async def get_user(self, token: str) -> Optional[User]:
        """Get user from authentication token."""
        # Implementation...

Booking Operations
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def add_booking(self, room_id: int, time: int, token: str, duration: int) -> Booking:
        """Adds a booking to the database."""
        # Implementation...

    async def remove_booking(self, booking_id: int) -> bool:
        """Removes a booking from the database using the booking_id."""
        # Implementation...

    async def get_booking(self, booking_id: int) -> Booking:
        """Returns a booking from a booking_id."""
        # Implementation...

    async def edit_booking(self, booking_id: int, room_id: int, start_time: str, duration: int) -> bool:
        """Edits a booking in the database."""
        # Implementation...

Room and Building Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def get_rooms(self) -> list[Room]:
        """Returns a list of all rooms with their facilities."""
        # Implementation...

    async def get_room(self, room_id: int) -> Room:
        """Returns a room from a room id."""
        # Implementation...

    async def get_building(self, building_id: int) -> Building:
        """Returns a building from a building_id."""
        # Implementation...

    async def get_buildings(self) -> list[Building]:
        """Returns a list of all buildings."""
        # Implementation...

University Management
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def get_universities(self) -> list[str]:
        """Returns a list of all universities."""
        # Implementation...

    async def add_user_to_university(self, user_id: int, university_id: int) -> bool:
        """Adds a user to a university."""
        # Implementation...

    async def get_uni_requests(self, university_id: int) -> list[User]:
        """Returns a list of all users who have requested to join a university."""
        # Implementation...

    async def accept_request(self,user_id: int, university_id:int) -> bool:
        """Adds a user to a university."""
        # Implementation...

Dependencies
------------

The module has the following dependencies:

- `os`: For file path handling
- `typing.Optional`: For optional type hints
- `datetime`: For timestamp handling
- `time`: For timestamp generation
- `secrets`: For token generation
- `aiosqlite`: For asynchronous SQLite database access
- `pydantic.dataclasses`: For data models
- `random`: For generating random codes
- `string`: For character sets used in random code generation
