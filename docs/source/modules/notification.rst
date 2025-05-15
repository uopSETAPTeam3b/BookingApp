===============
notification.py
===============

The `notification.py` module implements the NotificationManager class, which handles sending email notifications for various events in the BookingApp system.

Overview
--------

The NotificationManager class provides methods for sending email notifications for different types of events: booking confirmations, cancellations, edits, account creations, and booking sharing. Each notification type has a customized HTML email template tailored to the specific event.

Class Definition
----------------

.. code-block:: python

    class NotificationManager:
        """Handles email notifications for room bookings."""

        def __init__(self):
            load_dotenv()
            self.SMTP_SERVER = "smtp.gmail.com"
            self.SMTP_PORT = 465  
            self.SMTP_USERNAME = os.getenv("smtp_username")
            self.SMTP_PASSWORD = os.getenv("smtp_password") 

Email Sending Method
--------------------

.. code-block:: python

    def send_email(self, recipient_email: str, subject: str, body: str):
        """Sends an email notification with HTML content."""
        msg = MIMEText(body, "html")
        msg["Subject"] = subject or "No Subject"
        msg["From"] = self.SMTP_USERNAME
        msg["To"] = recipient_email
        print(f"Sending email to {recipient_email} with subject: {subject}")
        try:
            with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT, timeout=10) as server:
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
                server.sendmail(self.SMTP_USERNAME, recipient_email, msg.as_string())
            print(f"Email sent to {recipient_email} with subject: {subject}")
        except Exception as e:
            print(f"Failed to send email: {e}")

Utility Methods
---------------

.. code-block:: python

    def unix_to_local_parts(self, unix_timestamp: int) -> tuple[str, str, str]:
        """Converts a Unix timestamp to date, time, and weekday strings."""
        dt = datetime.fromtimestamp(unix_timestamp)
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        weekday = dt.strftime("%A")
        return date_str, time_str, weekday

Notification Methods
--------------------

booking_edited
~~~~~~~~~~~~~~

.. code-block:: python

    def booking_edited(self, old_booking: Booking, new_booking: Booking, background_tasks: BackgroundTasks) -> str:
        """Sends email notification when a booking is edited."""
        old_date_str, old_time_str, old_weekday = self.unix_to_local_parts(old_booking.time)
        new_date_str, new_time_str, new_weekday = self.unix_to_local_parts(new_booking.time)

        subject = "Your Booking Has Been Edited"
        body = f"""<html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        color: #333;
                        background-color: #f4f4f4;
                    }}
                    h2 {{
                        color: #f0ad4e;
                    }}
                    h3 {{
                        margin-top: 20px;
                        color: #333;
                    }}
                    ul {{
                        list-style-type: none;
                        padding: 0;
                    }}
                    li {{
                        margin: 6px 0;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 14px;
                        color: #777;
                    }}
                </style>
            </head>
            <body>
                <h2>Booking Edited Notification</h2>
                <p>Your booking has been successfully updated. Please review the changes below:</p>

                <h3>Previous Booking:</h3>
                <ul>
                    <li><strong>Room:</strong> {old_booking.room.name}</li>
                    <li><strong>Building:</strong> {old_booking.building.name}</li>
                    <li><strong>Date:</strong> {old_date_str}</li>
                    <li><strong>Time:</strong> {old_time_str}</li>
                    <li><strong>Day:</strong> {old_weekday}</li>
                </ul>

                <h3>Updated Booking:</h3>
                <ul>
                    <li><strong>Room:</strong> {new_booking.room.name}</li>
                    <li><strong>Building:</strong> {new_booking.building.name}</li>
                    <li><strong>Date:</strong> {new_date_str}</li>
                    <li><strong>Time:</strong> {new_time_str}</li>
                    <li><strong>Day:</strong> {new_weekday}</li>
                </ul>

                <p>If you did not request this change or need assistance, please contact us immediately.</p>
                <p>Thank you,<br>The Team</p>
                <div class="footer">Booking updated via your account on our platform.</div>
            </body>
        </html>"""
        
        background_tasks.add_task(self.send_email, old_booking.user.email, subject, body)
        return "Booking edited email sent."

booking_complete
~~~~~~~~~~~~~~~~

.. code-block:: python

    def booking_complete(self, booking: Booking, background_tasks: BackgroundTasks) -> str:
        """Sends confirmation email when a room is booked."""
        date_str, time_str, weekday = self.unix_to_local_parts(booking.time)
        subject = "Room Booking Confirmation"
        body = f"""<html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        color: #333;
                        background-color: #f4f4f4;
                    }}
                    h2 {{
                        color: #0056b3;
                    }}
                    p {{
                        font-size: 16px;
                        line-height: 1.6;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 14px;
                        color: #777;
                    }}
                    .access-code {{
                        color: #d9534f;
                        font-size: 22px;
                    }}
                </style>
            </head>
            <body>
                <h2>Room Booking Confirmation</h2>
                <p>We are pleased to inform you that your room booking has been successfully completed. Below are the details of your booking:</p>
                <ul>
                    <li><strong>Room:</strong> {booking.room.name}</li>
                    <li><strong>Building:</strong> {booking.building.name}</li>
                    <li><strong>Time:</strong> {time_str}</li>
                    <li><strong>Date:</strong> {date_str}</li>
                    <li><strong>Day:</strong> {weekday}</li>
                </ul>
                <p> Please arrive on time and ensure to follow the building's guidelines during your stay.</p>
                <p>-----------------------------------</p>
                <p class="access-code"><strong>Access Code:</strong> {booking.access_code}</p>
                <p>-----------------------------------</p>
                <p><strong>Building Address:</strong></p>
                <p>{booking.building.address_1}</p>
                <p>{booking.building.address_2}</p>
                <p>If you have any questions or need to make any changes, please contact us.</p>
                <p>Thank you,<br>The Team</p>
                <div class="footer">If you believe this was a mistake, please reach out to us immediately.</div>
            </body>
        </html>"""
        background_tasks.add_task(self.send_email, booking.user.email, subject, body)
        return "Booking confirmation email sent."

account_created
~~~~~~~~~~~~~~~

.. code-block:: python

    def account_created(self, user: User, background_tasks: BackgroundTasks) -> str:
        """Sends confirmation email when a user account is created."""
        subject = "Welcome to Our Booking Platform!"
        body = f"""<html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        color: #333;
                        background-color: #f4f4f4;
                    }}
                    h2 {{
                        color: #0056b3;
                    }}
                    p {{
                        font-size: 16px;
                        line-height: 1.6;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 14px;
                        color: #777;
                    }}
                </style>
            </head>
            <body>
                <h2>Welcome, {user.username}!</h2>
                <p>Your account has been successfully created. We're excited to have you on board.</p>
                <p>You can now log in, browse available rooms, and make bookings with ease.</p>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <p>Thank you,<br>The Team</p>
                <div class="footer">Need help? Contact our support team anytime.</div>
            </body>
        </html>"""
        recipient_email = user.email if user.email else db.get_user_email(user)
        background_tasks.add_task(self.send_email, recipient_email, subject, body)
        return "Account creation email sent."

booking_cancelled
~~~~~~~~~~~~~~~~~

.. code-block:: python

    def booking_cancelled(self, booking: Booking, strikes: int, newStrike: bool, background_tasks: BackgroundTasks) -> str:
        """Sends notification email when a booking is cancelled."""
        date_str, time_str, weekday = self.unix_to_local_parts(booking.time)

        if newStrike:
            subject = "Booking Cancellation Notice - Strike Issued"
            body = f"""<html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                            color: #333;
                            background-color: #f4f4f4;
                        }}
                        h2 {{
                            color: #d9534f;
                        }}
                        ul {{
                            list-style-type: none;
                            padding: 0;
                        }}
                        li {{
                            margin: 8px 0;
                        }}
                        .footer {{
                            margin-top: 20px;
                            font-size: 14px;
                            color: #777;
                        }}
                    </style>
                </head>
                <body>
                    <h2>Booking Cancellation Notice</h2>
                    <p>We regret to inform you that your booking has been cancelled. Below are the details of the cancelled booking:</p>
                    <ul>
                        <li><strong>Room:</strong> {booking.room.name}</li>
                        <li><strong>Booking Time:</strong> {time_str}</li>
                        <li><strong>Date:</strong> {date_str}</li>
                        <li><strong>Day:</strong> {weekday}</li>
                    </ul>
                    <p>Please note that a strike has been issued to your account due to this cancellation.</p>
                    <p>Number of strikes against account: {strikes}</p>
                    <p>If you believe this cancellation was made in error or if you would like to reschedule, please contact us.</p>
                    <p>Thank you,<br>The Team</p>
                    <div class="footer">If you believe this was a mistake, please reach out to us immediately.</div>
                </body>
            </html>"""
        else:
            subject = "Booking Cancellation Notice"
            body = f"""<html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                            color: #333;
                            background-color: #f4f4f4;
                        }}
                        h2 {{
                            color: #d9534f;
                        }}
                        ul {{
                            list-style-type: none;
                            padding: 0;
                        }}
                        li {{
                            margin: 8px 0;
                        }}
                        .footer {{
                            margin-top: 20px;
                            font-size: 14px;
                            color: #777;
                        }}
                    </style>
                </head>
                <body>
                    <h2>Booking Cancellation Notice</h2>
                    <p>We need to inform you that your booking has been cancelled. Below are the details of the cancelled booking:</p>
                    <ul>
                        <li><strong>Room:</strong> {booking.room.name}</li>
                        <li><strong>Booking Time:</strong> {time_str}</li>
                        <li><strong>Date:</strong> {date_str}</li>
                        <li><strong>Day:</strong> {weekday}</li>
                    </ul>
                    <p>Please note that no strikes have been issued to your account due to this cancellation.</p>
                    <p>Number of strikes against account: {strikes}</p>
                    <p>Strikes are issued for cancellations made within 30 minutes of the booking time.</p>
                    <p>If you believe this cancellation was made in error or if you would like to reschedule, please contact us.</p>
                    <p>Thank you,<br>The Team</p>
                    <div class="footer">If you need assistance, feel free to reach out.</div>
                </body>
            </html>"""

        background_tasks.add_task(self.send_email, booking.user.email, subject, body)
        return "Cancellation email sent."

share_booking
~~~~~~~~~~~~~

.. code-block:: python

    def share_booking(self, booking: Booking, background_tasks: BackgroundTasks) -> str:
        """Sends email notification when a booking is shared."""
        date_str, time_str, weekday = self.unix_to_local_parts(booking.time)
        subject = "Booking Shared with You"
        body = f"""<html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        color: #333;
                        background-color: #f4f4f4;
                    }}
                    h2 {{
                        color: #5bc0de;
                    }}
                    ul {{
                        list-style-type: none;
                        padding: 0;
                    }}
                    li {{
                        margin: 8px 0;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 14px;
                        color: #777;
                    }}
                </style>
            </head>
            <body>
                <h2>Booking Shared with You</h2>
                <p>Dear [Recipient Name],</p>
                <p>We would like to inform you that a booking has been shared with you. Please find the details below:</p>
                <ul>
                    <li><strong>Booking ID:</strong> {booking.booking_id}</li>
                    <li><strong>Room:</strong> {booking.room.name}</li>
                    <li><strong>Booking Time:</strong> {time_str}</li>
                    <li><strong>Date:</strong> {date_str}</li>
                    <li><strong>Day:</strong> {weekday}</li>
                </ul>
                <p>If you have any questions, feel free to reach out to us.</p>
                <p>Thank you,<br>The Team</p>
                <div class="footer">Thank you for using our service!</div>
            </body>
        </html>"""
        recipient_email = db.get_user_email(booking.user)  # Assuming we have this method to get the email
        background_tasks.add_task(self.send_email, recipient_email, subject, body)
        return "Booking share email sent."

Email Templates
---------------

The module uses HTML email templates for the different notification types. These templates include:

1. **Booking Confirmation**: Sent when a booking is created
2. **Booking Cancellation**: Sent when a booking is cancelled
3. **Booking Edited**: Sent when a booking is modified
4. **Account Creation**: Sent when a new user registers
5. **Booking Shared**: Sent when a booking is shared with another user

Each template has:

- CSS styling for a professional appearance
- Responsive design for mobile and desktop email clients
- Appropriate branding and color scheme
- Detailed information specific to the notification type

Asynchronous Processing
-----------------------

The module uses FastAPI's BackgroundTasks to send emails asynchronously:

.. code-block:: python

    # In the API endpoint
    @router.post("/book")
    async def book_room(booking: BookRoom, background_tasks: BackgroundTasks):
        # Process booking
        # ...
        
        # Send email in the background
        notification_manager.booking_complete(booked_room, background_tasks=background_tasks)
        
        return {"success": True}

This approach prevents email sending from blocking the main request-response cycle.

Email Security
--------------

The module implements several security measures:

1. **Environment Variables**: SMTP credentials are stored in environment variables loaded via dotenv

2. **SSL Connection**: Uses SMTP_SSL for a secure connection to the email server

3. **Error Handling**: Catches and logs exceptions during the email sending process

4. **Timeout Configuration**: Sets a timeout for the SMTP connection to prevent hanging

Dependencies
------------

The module has the following dependencies:

- `smtplib`: For SMTP email sending
- `email.mime.text.MIMEText`: For creating HTML email messages
- `dotenv`: For loading environment variables
- `os`: For accessing environment variables
- `datetime`: For timestamp handling
- `fastapi.BackgroundTasks`: For asynchronous email sending
- `database`: For database models and access
- `typing.Optional`: For optional type hints
