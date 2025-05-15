====================
Repository Structure
====================

The repository is organised into the following structure:

.. code-block:: none

    BookingApp/
    ├── docs/                      # Documentation files
    │   ├── Makefile               # Sphinx documentation build file
    │   ├── make.bat               # Windows build script
    │   ├── requirements.txt       # Documentation dependencies
    │   └── source/                # RST documentation source files
    ├── src/                       # Source code
    │   ├── account.py             # Account management functionality
    │   ├── api.py                 # Base API class
    │   ├── app.py                 # Main application entry point
    │   ├── booking.py             # Booking management functionality
    │   ├── create.sql             # SQL for database schema creation
    │   ├── database.py            # Database access and models
    │   ├── insert.sql             # SQL for initial data insertion
    │   ├── notification.py        # Email notification system
    │   └── test.py                # Unit tests
    ├── static/                    # Static assets (CSS, JS, images)
    │   ├── 404.html               # 404 page
    │   ├── *.png                  # PNG files
    │   ├── *.svg                  # SVG files
    │   ├── *.css                  # CSS files
    │   └── *.js                   # JavaScript files
    ├── template/                  # HTML templates
    │   ├── account.html           # Account management page
    │   ├── book.html              # Room booking page
    │   ├── booking.html           # View bookings page
    │   ├── booking_cancelled_over # Popup Component that says your booking has been cancelled          # View bookings page
    │   ├── booking_overlay.html   # Popup Edit Menu For Bookings           # View bookings page
    │   ├── confirmation_overlay.h # Popup When You Book A Room
    │   ├── index.html             # Landing Page for the Application
    │   ├── login.html             # Login Page
    │   ├── nav.html               # Nav Bar Component
    │   ├── share_overlay.html     # Popup that shows Share Code
    │   ├── signup.html            # Signup
    │   └── welcome.html           # Welcome page for app
    ├── .gitignore                 # Git ignore file
    ├── .readthedocs.yaml          # Read the Docs configuration
    ├── LICENSE                    # MIT license file
    ├── README.md                  # Project overview and team info
    └── requirement.txt            # Project dependencies
