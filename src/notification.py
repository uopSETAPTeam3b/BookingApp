import smtplib
from email.mime.text import MIMEText
from pydantic.dataclasses import dataclass
from fastapi import BackgroundTasks

class NotificationManager:
    SMTP_SERVER = "smtp.gmail.com"  # Replace with actual SMTP server
    SMTP_PORT = 587  # Common SMTP port for TLS
    SMTP_USERNAME = "setupgrp3bnotify@gmail.com"
    SMTP_PASSWORD = "yfLMLh@@#3eHV1a4gCS#"

    def __init__(self):
        pass

    def send_email(self, recipient: str, subject: str, body: str):
        """Sends an email notification."""
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.SMTP_USERNAME
        msg["To"] = recipient

        with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
            server.sendmail(self.SMTP_USERNAME, recipient, msg.as_string())

    @dataclass
    class BookedRoom:
        time: int
        room_id: int
        user_email: str

    def booking_complete(self, booking: BookedRoom, background_tasks: BackgroundTasks):
        """Sends confirmation email when a room is booked."""
        subject = "Room Booking Confirmation"
        body = f"Your room {booking.room_id} has been successfully booked at {booking.time}."
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        return "Booking confirmation email sent."

    @dataclass
    class CancelledRoom:
        time: int
        room_id: int
        user_email: str

    def booking_cancelled(self, booking: CancelledRoom, background_tasks: BackgroundTasks):
        """Sends notification email when a booking is cancelled."""
        subject = "Booking Cancellation Notice"
        body = f"Your booking for room {booking.room_id} at {booking.time} has been cancelled."
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        return "Cancellation email sent."

    @dataclass
    class ShareBooking:
        time: int
        booking_id: int
        user_email: str

    def share_booking(self, booking: ShareBooking, background_tasks: BackgroundTasks):
        """Sends email notification when a booking is shared."""
        subject = "Booking Shared with You"
        body = f"A booking (ID: {booking.booking_id}) has been shared with you. Time: {booking.time}."
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        return "Booking share email sent."
