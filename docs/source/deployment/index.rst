================
Local Deployment
================

This guide will help you set up and run the BookingApp system in a local development environment.

Prerequisites
-------------

Before you begin, ensure you have the following installed:

1. **Python 3.10+**: The application is built with Python 3.10 or newer
2. **Git**: For cloning the repository
3. **pip**: For installing Python dependencies
4. **A text editor or IDE**: Visual Studio Code, PyCharm, etc.

Step 1: Clone the Repository
----------------------------

First, clone the repository to your local machine:

.. code-block:: bash

    git clone https://github.com/uopSETAPTeam3b/BookingApp.git
    cd BookingApp

Step 2: Create a Virtual Environment
------------------------------------

It's recommended to use a virtual environment to keep dependencies isolated:

.. code-block:: bash

    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

Step 3: Install Dependencies
----------------------------

Install the required Python packages:

.. code-block:: bash

    pip install -r requirement.txt

Step 4: Configure Email Notifications
-------------------------------------

To enable email notifications, create a `.env` file in the project root directory:

.. code-block:: bash

    # .env file
    smtp_username = "your_email@gmail.com"
    smtp_password = "your_app_password"

.. note::
   For Gmail, you'll need to use an app password rather than your regular password. You can generate an app password in your Google Account settings under Security > App passwords.

Step 5: Run the Application
---------------------------

Start the FastAPI application:

.. code-block:: bash

    # Using the FastAPI CLI
    fastapi run ./src/app.py

    # Alternatively, using uvicorn directly
    uvicorn src.app:app --reload

The application will be available at http://127.0.0.1:8000

Step 6: Access the Application
------------------------------

Open your web browser and navigate to:

- **Welcome page**: http://127.0.0.1:8000/
- **Login page**: http://127.0.0.1:8000/login
- **Signup page**: http://127.0.0.1:8000/signup

Step 7: Run Tests
-----------------

To run the tests:

.. code-block:: bash

    # Run the test suite
    pytest ./src/test.py

    # Run with verbose output
    pytest -v ./src/test.py

Database Setup
--------------

The application automatically sets up an SQLite database when it first runs. The database configuration is handled in the `app.py` file:

.. code-block:: python

    CREATE_FILE="src/create.sql"
    INSERT_FILE="src/insert.sql"
    DatabaseManager(create=CREATE_FILE, insert=INSERT_FILE)

If you want to reset the database:

1. Stop the application
2. Delete the `database.db` file
3. Restart the application (a new database will be created)

Development Tools
-----------------

These tools can enhance your development workflow:

- **SQLite Browser**: For inspecting and editing the database
- **FastAPI Swagger UI**: Available at http://127.0.0.1:8000/docs
- **FastAPI ReDoc**: Available at http://127.0.0.1:8000/redoc
- **Visual Studio Code**: Recommended with Python and SQLite extensions

Troubleshooting
---------------

If you encounter issues during local deployment:

1. **Module not found errors**:
   - Ensure your virtual environment is activated
   - Verify all dependencies are installed: `pip install -r requirement.txt`

2. **Database errors**:
   - Check file permissions for the database file
   - Try deleting the database file and restarting the application

3. **Email notification errors**:
   - Verify your `.env` file has the correct SMTP credentials
   - For Gmail, ensure you're using an app password
   - Check your email service's SMTP settings

4. **Port already in use**:
   - Change the port: `uvicorn src.app:app --port 8001`
   - Find and terminate the process using the default port

Development Workflow
--------------------

For an efficient development workflow:

1. Make code changes
2. Restart the application (with `--reload` flag, it will auto-restart for most changes)
3. Test your changes in the browser
4. Run the test suite to ensure nothing is broken
5. Commit your changes using Git
