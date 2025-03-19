import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from fastapi import BackgroundTasks
from database import Booking, Room, User, DatabaseManager as db
from typing import Optional

class NotificationManager:
    """Handles email notifications for room bookings."""

    def __init__(self):
        load_dotenv()
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = 465  
        self.SMTP_USERNAME = os.getenv("smtp_username")
        self.SMTP_PASSWORD = os.getenv("smtp_password") 
        
        pass

    def send_email(self, recipient_email: str, subject: str, body: str):
        """Sends an email notification."""
        msg = MIMEText(body)
        msg["Subject"] = subject or "No Subject"
        msg["From"] = self.SMTP_USERNAME
        msg["To"] = recipient_email

        with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT, timeout=10) as server:
            server.login(self.SMTP_USERNAME , self.SMTP_PASSWORD) 
            server.sendmail(self.SMTP_USERNAME, recipient_email, msg.as_string())

    def booking_complete(self, booking: Booking, background_tasks: BackgroundTasks) -> str:
        """Sends confirmation email when a room is booked."""
        subject = "Room Booking Confirmation"
        body = f""" <html>
            <body>
                <h2>Room Booking Confirmation</h2>
                <p>We are pleased to inform you that your room booking has been successfully completed. Below are the details of your booking:</p>
                <ul>
                    <li><strong>Room:</strong> {booking.room}</li>
                    <li><strong>Booking Time:</strong> {booking.time}</li>
                </ul>
                <p>If you have any questions or need to make any changes, please contact us</p>
                <p>Thank you</p>
            </body>
        </html>"""
        background_tasks.add_task(self.send_email(db.get_user_email(booking.user), subject, body))
        return "Booking confirmation email sent."

    def booking_cancelled(self, booking: Booking, background_tasks: BackgroundTasks) -> str:
        """Sends notification email when a booking is cancelled."""
        subject = "Booking Cancellation Notice"
        body = f"""<html>
            <body>
                <h2>Booking Cancellation Notice</h2>
                <p>We need to inform you that your booking has been cancelled. Below are the details of the cancelled booking:</p>
                <ul>
                    <li><strong>Room:</strong> {booking.room}</li>
                    <li><strong>Booking Time:</strong> {booking.time}</li>
                </ul>
                <p>If you believe this cancellation was made in error or if you would like to reschedule, please contact Us.</p>
                <p>Thank you</p>
            </body>
        </html>"""
        background_tasks.add_task(self.send_email( db.get_user_email(booking.user), subject, body))

        return "Cancellation email sent."

    def share_booking(
        self, booking: Booking, background_tasks: BackgroundTasks
    ) -> str:
        """Sends email notification when a booking is shared."""
        subject = "Booking Shared with You"
        body = f"""A booking (ID: ) has been shared with you. Time: .
        <html>
            <body>
                <h2>Booking Shared with You</h2>
                <p>Dear [Recipient Name],</p>
                <p>We would like to inform you that a booking has been shared with you. Please find the details below:</p>
                <ul>
                    <li><strong>Booking ID:</strong> {booking.booking_id}</li>
                    <li><strong>Booking Time:</strong> {booking.time}</li>
                    <li><strong>Booking Room:</strong> {booking.room}</li>
                </ul>
                <p>Thank you.</p>
            </body>
        </html>"""
        background_tasks.add_task(self.send_email(db.get_user_email(booking.user), subject, body))
        return "Booking share email sent."
