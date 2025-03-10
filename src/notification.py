import smtplib
from email.mime.text import MIMEText
from pydantic.dataclasses import dataclass
from fastapi import BackgroundTasks
#from database import get_Email
@dataclass
class BookedRoom:
    time: int
    room_id: int
    user_email: str
    user: str
    room: str

@dataclass
class CancelledRoom:
    time: int
    room_id: int
    room: str
    user_email: str

@dataclass
class ShareBooking:
    time: int
    booking_id: int
    user_email: str
    room: str

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
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        return "Booking confirmation email sent."

    def booking_cancelled(self, booking: CancelledRoom, background_tasks: BackgroundTasks)-> str: 
        #Sends notification email when a booking is cancelled.
        subject = "Booking Cancellation Notice"
        body = f"""<html>
            <body>
                <h2>Booking Cancellation Notice</h2>
                <p>We need  to inform you that your booking has been cancelled. Below are the details of the cancelled booking:</p>
                <ul>
                    <li><strong>Room:</strong> {booking.room}</li>
                    <li><strong>Booking Time:</strong> {booking.time}</li>
                </ul>
                <p>If you believe this cancellation was made in error or if you would like to reschedule, please contact Us.</p>
                <p>Thank you</p>
            </body>
        </html>"""
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        
        return "Cancellation email sent."

    def share_booking(self, booking: ShareBooking, background_tasks: BackgroundTasks)-> str:
        #Sends email notification when a booking is shared.
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
        background_tasks.add_task(self.send_email, booking.user_email, subject, body)
        return "Booking share email sent."
