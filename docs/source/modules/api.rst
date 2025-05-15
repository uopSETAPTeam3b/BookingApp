======
api.py
======

The `api.py` module defines the base API class that is extended by service-specific API classes.

Overview
--------

The API class provides a common foundation for defining API routes with FastAPI. It establishes a router with a prefix that can be customized by subclasses. This approach ensures consistent API structure across the application.

Class Definition
----------------

.. code-block:: python

    class API:
        prefix = "API"

        def __init__(self):
            self.router = APIRouter(prefix=self.prefix)

Usage
-----

This base class is extended by other API classes in the application:

.. code-block:: python

    class AccountManager(API):
        prefix = "/account"
        
        def __init__(self, nm: NotificationManager):
            super().__init__()
            self.nm = nm
            # Define routes
            self.router.add_api_route("/login", self.login, methods=["POST"])
            # ...

    class BookingManager(API):
        prefix = "/booking"
        
        def __init__(self, nm: NotificationManager):
            super().__init__()
            self.nm = nm
            # Define routes
            self.router.add_api_route("/book", self.book_room, methods=["POST"])
            # ...

Benefits
--------

The API base class provides several benefits:

1. **Consistent Structure**: All API endpoints follow the same pattern
2. **Route Prefixing**: Each API group has its own URL prefix
3. **Modular Design**: New API functionality can be added by extending the base class
4. **Clean Separation**: Each API manager focuses on a specific domain

Dependencies
------------

The module has the following dependency:

- `fastapi.APIRouter`: For defining API routes
