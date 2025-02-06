from fastapi import FastAPI
from database import DatabaseManager
from booking import BookingManager
from account import AccountManager
# from notification import NotificationManager

app = FastAPI()

db = DatabaseManager()
account = AccountManager()
app.include_router(account.router)
booking = BookingManager()
app.include_router(booking.router)
# notif = NotificationManager()
# app.include_router(notif.router)