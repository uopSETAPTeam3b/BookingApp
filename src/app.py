import os

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from account import AccountManager
from booking import BookingManager
from database import DatabaseManager
from notification import NotificationManager

# from notification import NotificationManager

app = FastAPI()

db = DatabaseManager()
notif = NotificationManager()
# app.include_router(notif.router)

account = AccountManager()
app.include_router(account.router)
booking = BookingManager(db, notif)
app.include_router(booking.router)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

STATIC = "static"
TEMPLATE = "template"
print(os.path.join(BASE_DIR, TEMPLATE))
templates = Jinja2Templates(os.path.join(BASE_DIR, TEMPLATE))

R_404 = FileResponse(
            os.path.join(BASE_DIR, STATIC, "404.html"), 
            status_code=404
            )

@app.get("/{path:path}")
def index(request: Request, path):
    template_file_path = os.path.abspath(os.path.join(TEMPLATE, path))
    print(template_file_path)
    print(path)
    if os.path.exists(template_file_path):
        if os.path.isdir(template_file_path):
            if os.path.exists(f"{template_file_path}/index.html"):
                return templates.TemplateResponse(
                    f"{path}/index.html", {"request": request}
                )
        else:
            return templates.TemplateResponse(path, {"request": request})
    elif os.path.exists(template_file_path + ".html"):
        return templates.TemplateResponse(path + ".html", {"request": request})

    file_path = os.path.abspath(os.path.join(STATIC, path if path else "index.html"))
    if not os.path.exists(file_path):
        return R_404
    if not os.path.isfile(file_path):
        if os.path.exists(f"{file_path}/index.html"):
            return FileResponse(f"{file_path}/index.html")
        return R_404
    return FileResponse(file_path)
