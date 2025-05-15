===========
Booking API
===========

The Booking API handles room booking management, including creating, viewing, editing, and cancelling bookings.

Endpoint: /booking/book
-----------------------

**Method**: POST

**Description**: Books a room for a specific time slot.

**Request body**:

.. code-block:: json

  {
    "token": "64-character-hex-token",
    "datetime": 1683680400,
    "room_id": 1,
    "duration": 1
  }

**Response**:

- Success (200):

  .. code-block:: json

    {
      "message": "Room booked successfully",
      "booking_id": 1,
      "access_code": "ABC123",
      "room_id": 1,
      "room_name": "Room 101",
      "building_id": 1,
      "building_name": "Engineering Building",
      "start_time": 1683680400,
      "duration": 1
    }

- Failure (409):

  .. code-block:: json

    {
      "detail": "Room already booked"
    }

**Implementation**:
The book_room method in the BookingManager class checks if the room is available for the requested time slot. If available, it creates a new booking record and sends a confirmation email.

Endpoint: /booking/cancel
-------------------------

**Method**: POST

**Description**: Cancels a booking.

**Request body**:

.. code-block:: json

  {
    "token": "64-character-hex-token",
    "booking_id": 1
  }

**Response**:

- Success (200): "Booking cancelled"
- Failure (404):

  .. code-block:: json

    {
      "detail": "Booking not found"
    }

**Implementation**:
The cancel_booking method in the BookingManager class removes the booking record from the database. If the cancellation is made within 30 minutes of the booking time, a strike is issued to the user.

Endpoint: /booking/share
------------------------

**Method**: POST

**Description**: Shares a booking with another user.

**Request body**:

.. code-block:: json

  {
    "token": "64-character-hex-token",
    "booking_id": 1,
    "username": "user2@example.com"
  }

**Response**:

- Success (200): Empty string
- Failure (404):

  .. code-block:: json

    {
      "detail": "User not found"
    }

**Implementation**:
The share_room method in the BookingManager class finds the specified user and sends a booking sharing notification.

Endpoint: /booking/edit_booking
-------------------------------

**Method**: POST

**Description**: Edits an existing booking.

**Request body**:

.. code-block:: json

  {
    "token": "64-character-hex-token",
    "dayTime": 14,
    "room_id": 1,
    "duration": 2,
    "old_booking_id": 1
  }

**Response**:

- Success (200): "Booking edited successfully"
- Failure (404):

  .. code-block:: json

    {
      "detail": "Booking not found"
    }

**Implementation**:
The edit_booking method in the BookingManager class updates the booking record with the new room, time, and duration. It also sends a notification about the changes.

Endpoint: /booking/get_room_facilities
--------------------------------------

**Method**: GET

**Description**: Returns a list of facilities available in a room.

**Query parameters**:

- token: The user's authentication token
- room_id: The ID of the room

**Response**:

- Success (200):

  .. code-block:: json

    {
      "facilities": [1, 2, 3]
    }

- Failure (404):

  .. code-block:: json

    {
      "detail": "Room not found"
    }

**Implementation**:
The get_room_facilities method in the BookingManager class retrieves the facilities associated with the specified room.

Endpoint: /booking/get_bookings
-------------------------------

**Method**: POST

**Description**: Returns a list of bookings for the authenticated user.

**Request body**:

.. code-block:: json

  {
    "token": "64-character-hex-token"
  }

**Response**:

- Success (200):

  .. code-block:: json

    {
      "bookings": [
        {
          "id": 1,
          "user": {
            "username": "user@example.com",
            "email": "user@example.com"
          },
          "room": {
            "id": 1,
            "name": "Room 101",
            "building_id": 1
          },
          "time": 1683680400,
          "building": {
            "id": 1,
            "name": "Engineering Building",
            "address_1": "123 Tech Street",
            "address_2": "Campus A",
            "opening_time": "08:00",
            "closing_time": "18:00"
          },
          "duration": 1,
          "access_code": "ABC123",
          "share_code": "XYZ789",
          "shared": 0
        }
      ]
    }

- Failure (404):

  .. code-block:: json

    {
      "detail": "No bookings found"
    }

**Implementation**:
The get_bookings method in the BookingManager class retrieves all bookings associated with the authenticated user.

Endpoint: /booking/get_bookings_for_date
----------------------------------------

**Method**: GET

**Description**: Returns a list of bookings for a specific date.

**Query parameters**:

- dateTime: Unix timestamp representing the date

**Response**:

- Success (200):

  .. code-block:: json

    {
      "bookings": [
        {
          "booking_id": 1,
          "building_id": 1,
          "room_name": "Room 101",
          "building_name": "Engineering Building",
          "room_id": 1,
          "start_time": 1683680400,
          "duration": 1,
          "access_code": "ABC123",
          "address_1": "123 Tech Street",
          "address_2": "Campus A",
          "opening_time": "08:00",
          "closing_time": "18:00"
        }
      ]
    }

**Implementation**:
The get_bookings_for_date method in the BookingManager class retrieves all bookings for the specified date.

Endpoint: /booking/get_booking
------------------------------

**Method**: POST

**Description**: Returns information about a specific booking.

**Request body**:

.. code-block:: json

  {
    "token": "64-character-hex-token",
    "booking_id": 1
  }

**Response**:

- Success (200): Booking object
- Failure (404):

  .. code-block:: json

    {
      "detail": "Booking not found"
    }

**Implementation**:
The get_booking method in the BookingManager class retrieves the booking with the specified ID.

Endpoint: /booking/get_rooms
----------------------------

**Method**: POST

**Description**: Returns a list of all rooms.

**Response**:

- Success (200):

  .. code-block:: json

    {
      "rooms": [
        {
          "id": 1,
          "name": "Room 101",
          "building_id": 1,
          "type": "study room",
          "capacity": 10,
          "facilities": [
            {
              "id": 1,
              "name": "Projector"
            },
            {
              "id": 2,
              "name": "Whiteboard"
            }
          ]
        }
      ],
      "buildings": [
        {
          "id": 1,
          "name": "Engineering Building",
          "address_1": "123 Tech Street",
          "address_2": "Campus A",
          "opening_time": "08:00",
          "closing_time": "18:00"
        }
      ]
    }

- Failure (404):

  .. code-block:: json

    {
      "detail": "No rooms found"
    }

**Implementation**:
The get_rooms method in the BookingManager class retrieves all rooms and buildings from the database.

Endpoint: /booking/get_room
---------------------------

**Method**: POST

**Description**: Returns information about a specific room.

**Request body**:

.. code-block:: json

  {
    "token": "64-character-hex-token",
    "room_id": 1
  }

**Response**:

- Success (200): Room object
- Failure (404):

  .. code-block:: json

    {
      "detail": "Room not found"
    }

**Implementation**:
The get_room method in the BookingManager class retrieves the room with the specified ID.

Endpoint: /booking/get_day_bookings
-----------------------------------

**Method**: GET

**Description**: Returns all bookings for the same day as a specified booking.

**Query parameters**:

- booking_id: The ID of the reference booking

**Response**:

- Success (200):

  .. code-block:: json

    {
      "bookings": [
        {
          "booking_id": 1,
          "building_id": 1,
          "room_name": "Room 101",
          "building_name": "Engineering Building",
          "room_id": 1,
          "start_time": 1683680400,
          "duration": 1,
          "access_code": "ABC123",
          "address_1": "123 Tech Street",
          "address_2": "Campus A",
          "opening_time": "08:00",
          "closing_time": "18:00"
        }
      ]
    }

- Failure (404):

  .. code-block:: json

    {
      "detail": "Booking not found"
    }

**Implementation**:
The get_day_bookings method in the BookingManager class retrieves all bookings for the same day as the specified booking.

Endpoint: /booking/get_booking_by_share_code
--------------------------------------------

**Method**: GET

**Description**: Adds a shared booking to the user's bookings using a share code.

**Query parameters**:

- token: The user's authentication token
- share_code: The share code of the booking

**Response**:

- Success (200):

  .. code-block:: json

    {
      "message": "Booking shared successfully"
    }

- Failure (404):

  .. code-block:: json

    {
      "detail": "Booking not found"
    }

**Implementation**:
The get_booking_by_share_code method in the BookingManager class finds the booking with the specified share code and adds it to the user's bookings with the shared flag set to true.
