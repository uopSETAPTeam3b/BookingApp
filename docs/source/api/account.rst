===========
Account API
===========

The Account API handles user authentication, registration, and account management.

Endpoint: /account/login
------------------------

**Method**: POST

**Description**: Authenticates a user and returns an authentication token.

**Request body**:

.. code-block:: json

  {
    "username": "user@example.com",
    "password": "password123"
  }

**Response**:

- Success (200):

  .. code-block:: json

    {
      "token": "64-character-hex-token"
    }

- Failure (401):

  .. code-block:: json

    {
      "message": "Invalid username or password"
    }

**Implementation**:
The login method in the AccountManager class verifies the provided username and password. The password is compared to the hashed password stored in the database using bcrypt. If the credentials are valid, a new authentication token is generated and stored in the database.

Endpoint: /account/logout
-------------------------

**Method**: POST

**Description**: Invalidates the user's authentication token.

**Request body**:

.. code-block:: json

  {
    "token": "64-character-hex-token"
  }

**Response**:

- Success (200): "Logout successful"

**Implementation**:
The logout method in the AccountManager class removes the token from the Authentication table in the database.

Endpoint: /account/register
---------------------------

**Method**: POST

**Description**: Creates a new user account.

**Request body**:

.. code-block:: json

  {
    "username": "user@example.com",
    "password": "password123"
  }

**Response**:

- Success (200):

  .. code-block:: json

    {
      "token": "64-character-hex-token"
    }

- Failure (400):

  .. code-block:: json

    {
      "message": "User already exists"
    }

**Implementation**:
The register method in the AccountManager class creates a new user record in the database. The password is hashed using bcrypt before storing. If the registration is successful, a welcome email is sent via the NotificationManager.

Endpoint: /account/me
---------------------

**Method**: GET

**Description**: Returns information about the currently authenticated user.

**Query parameters**:

- token: The user's authentication token

**Response**:

- Success (200):

  .. code-block:: json

    {
      "username": "user@example.com"
    }

- Failure (401):

  .. code-block:: json

    {
      "message": "Invalid token"
    }

**Implementation**:
The me method in the AccountManager class retrieves the user record associated with the provided token.

Endpoint: /account/get_unis
---------------------------

**Method**: GET

**Description**: Returns a list of available universities.

**Response**:

- Success (200): Array of university objects
- Failure (404):

  .. code-block:: json

    {
      "message": "No universities found"
    }

**Implementation**:
The get_unis method in the AccountManager class retrieves all university records from the database.

Endpoint: /account/accountDetails
---------------------------------

**Method**: GET

**Description**: Returns detailed information about the user's account.

**Query parameters**:

- token: The user's authentication token

**Response**:

- Success (200):

  .. code-block:: json

    {
      "id": 1,
      "username": "user@example.com",
      "email": "user@example.com",
      "phone_number": "1234567890",
      "offence_count": 0,
      "role": "user",
      "university": "University of Portsmouth",
      "university_id": 1
    }

- Failure (401):

  .. code-block:: json

    {
      "message": "Invalid token"
    }

**Implementation**:
The accountDetails method in the AccountManager class retrieves the user record and related university information.

Endpoint: /account/add_uni_user
-------------------------------

**Method**: POST

**Description**: Adds a user to a university.

**Query parameters**:

- token: The user's authentication token
- uni_id: The ID of the university

**Response**:

- Success (200): No content
- Failure (401):

  .. code-block:: json

    {
      "message": "Invalid token"
    }

**Implementation**:
The add_uni_user method in the AccountManager class creates a university request record linking the user to the specified university.

Endpoint: /account/get_uni_requests
-----------------------------------

**Method**: GET

**Description**: Returns a list of pending university access requests.

**Query parameters**:

- token: The user's authentication token
- uni_id: The ID of the university

**Response**:

- Success (200): Array of user objects with pending requests
- Failure (401):

  .. code-block:: json

    {
      "message": "Invalid token"
    }

**Implementation**:
The get_uni_requests method in the AccountManager class retrieves all pending university access requests for the specified university.

Endpoint: /account/accept_uni_request
-------------------------------------

**Method**: POST

**Description**: Accepts a university access request.

**Query parameters**:

- token: The user's authentication token
- university_id: The ID of the university
- user_id: The ID of the user whose request is being accepted

**Response**:

- Success (200):

  .. code-block:: json

    {
      "message": "Request accepted"
    }

- Failure (401):

  .. code-block:: json

    {
      "message": "Invalid token"
    }

**Implementation**:
The accept_uni_request method in the AccountManager class updates the status of the university access request to accepted.
