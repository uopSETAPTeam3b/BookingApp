import smtplib
from email.mime.text import MIMEText
from pydantic.dataclasses import dataclass
from fastapi import BackgroundTasks
@dataclass
class BookedRoom:
    time: int
    room_id: int
    user_email: str

@dataclass
class CancelledRoom:
    time: int
    room_id: int
    user_email: str

@dataclass
class ShareBooking:
    time: int
    booking_id: int
    user_email: str

class NotificationManager:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465  # SSL port 
    SMTP_USERNAME = "setupgrp3bnotify@gmail.com"  # SETUP address
    SMTP_PASSWORD = "phlsdkyafhrpqgpc"  # app password

    def __init__(self):
        pass

    def send_email(self, recipient: str, subject: str, body: str):
        #Sends an email notification.
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.SMTP_USERNAME
        msg["To"] = recipient

        with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT, timeout=10) as server:
            server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
            server.sendmail(self.SMTP_USERNAME, recipient, msg.as_string())

    def booking_complete(self, booking: BookedRoom, background_tasks: BackgroundTasks) -> str:
        #Sends confirmation email when a room is booked.
        subject = "Room Booking Confirmation"
        body = f"Your room {booking.room_id} has been successfully booked at {booking.time}."
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        return "Booking confirmation email sent."

    def booking_cancelled(self, booking: CancelledRoom, background_tasks: BackgroundTasks)-> str: 
        #Sends notification email when a booking is cancelled.
        subject = "Booking Cancellation Notice"
        body = f"Your booking for room {booking.room_id} at {booking.time} has been cancelled."
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        return "Cancellation email sent."

    def share_booking(self, booking: ShareBooking, background_tasks: BackgroundTasks)-> str:
        #Sends email notification when a booking is shared.
        subject = "Booking Shared with You"
        body = f"A booking (ID: {booking.booking_id}) has been shared with you. Time: {booking.time}."
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        return "Booking share email sent."
