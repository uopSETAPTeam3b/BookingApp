from collections import defaultdict
from fastapi.responses import JSONResponse
from datetime import datetime
from dataclasses import dataclass
from api import API
from database import User, DB, LoggedInUser
from notification import NotificationManager
from fastapi import BackgroundTasks
import bcrypt

class AccountManager(API):
    prefix = "/account"

    def __init__(self, nm: NotificationManager):
        super().__init__()
        self.nm = nm
       
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/logout", self.logout, methods=["POST"])
        self.router.add_api_route("/register", self.register, methods=["POST"])
        self.router.add_api_route("/me", self.me, methods=["GET"])
        self.router.add_api_route("/get_unis", self.get_unis, methods=["GET"])
        self.router.add_api_route("/accountDetails", self.accountDetails, methods=["GET"])
        self.router.add_api_route("/add_uni_user", self.add_uni_user, methods=["POST"])
        self.router.add_api_route("/get_uni_requests", self.get_uni_requests, methods=["GET"])
        self.router.add_api_route("/accept_uni_request", self.accept_uni_request, methods=["POST"])
        self.login_attempts = defaultdict(lambda: {"count": 0, "last_attempt": None})

    @dataclass
    class Login:
        username: str
        password: str
    async def accept_uni_request(self, token:str, university_id:int, user_id:int):
        """Accepts a request to join a university"""
        async with DB() as db:
            user: User = await db.get_user(token)
            if user is None or not user.role == "admin":
                return

            await db.accept_request(user_id, university_id)
            return JSONResponse(content={"message": "Request accepted"}, status_code=200)
            
    async def get_uni_requests(self, token:str, uni_id:int) -> JSONResponse:
        """Returns a list of users who have requested to join a university"""
        async with DB() as db:
            user: User = await db.get_user(token)
            if user is None or not user.role == "admin":
                return JSONResponse(content={"message": "Invalid token"}, status_code=401)

            uni_requests = await db.get_uni_requests(uni_id)
            if uni_requests is None:
                return JSONResponse(content={"message": "No requests found"}, status_code=404)
            return JSONResponse(content=uni_requests, status_code=200)
        
    async def add_uni_user(self, token:str, uni_id:int) -> JSONResponse:
        """Adds a user to a university"""
        async with DB() as db:
            user: User = await db.get_user(token)
            if user is None:
                return JSONResponse(content={"message": "Invalid token"}, status_code=401)

            await db.add_user_to_university(user.id, uni_id)
            
    async def get_unis(self) -> JSONResponse:
        """Returns a list of universities"""
        async with DB() as db:
            unis = await db.get_universities()
            if unis is None:
                return JSONResponse(content={"message": "No universities found"}, status_code=404)
            return JSONResponse(content=unis, status_code=200)
        
    async def accountDetails(self, token:str) -> JSONResponse:
        """Returns full account details and associated universities for a user"""
        async with DB() as db:
            user: User = await db.get_user(token)
            if user is None:
                return JSONResponse(content={"message": "Invalid token"}, status_code=401)

            details = await db.get_account_details(user.id)

            if "error" in details:
                return JSONResponse(content={"message": details["error"]}, status_code=404)

            return JSONResponse(content=details, status_code=200)
    
    async def me(self, token: str) -> JSONResponse:
        """ Returns the user object for the given token """
        async with DB() as db:
            user: User = await db.get_user(token)
            
            if user is None:
                return JSONResponse(content={"message": "Invalid token"}, status_code=401)
            return JSONResponse(content={"username": user.username}, status_code=200)

    
    async def login(self, login: Login) -> JSONResponse:
        print(f"Login attempt for {login.username}")
        async with DB() as db:
            user: User = await db.get_user_from_username(login.username)
            if user is None:
                print(f"User not found: {login.username}")
                return JSONResponse(content={"message": "Invalid username or password"}, status_code=401)

            password = await db.get_password(user)
            print(f"User found: {user.username}")
            loginStatus = await self.verifyPassword(login.password, password)

            if loginStatus:
                token = await db.create_token(user)
                print(f"Login successful: {user.username} & {token}")
                return JSONResponse(content={"token": token}, status_code=200)  

            print(f"Login incorrect password: {user.username}")
            self.record_failed_attempt(user.username)

            if self.get_failed_attempts(user.username) > 3:
                return JSONResponse(
                    content={"message": "Too many failed attempts. Please contact support."},
                    status_code=403
                )

            return JSONResponse(content={"message": "Invalid username or password"}, status_code=401)

    @dataclass
    class Logout:
        token: str

   
    async def logout(self, logout: Logout) -> str:
        """ invalidates the token """
        async with DB() as db:  
            await db.delete_token(token=logout.token)
        
        return "Logout successful"

    @dataclass
    class Register:
        username: str
        password: str
    
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')  

    
    async def register(self, register: Register, background_tasks:BackgroundTasks) -> str:
        """ creates user and returns token """
        async with DB() as db:
            user = await db.get_user_from_username(register.username.lower())
            if user is None:
                password = register.password
                
                hashed_password = self.hash_password(password=password)
                token = await db.create_user(register.username.lower(), hashed_password, register.username.lower())
                new_user = await db.get_user_from_username(register.username.lower())
                self.nm.account_created(user=new_user, background_tasks=background_tasks)
                return JSONResponse(content={"token": token or ""}, status_code=200)
            return JSONResponse(content={"message": "User already exists"}, status_code=400) 

    def record_failed_attempt(self,username: str):
        """Record a failed login attempt for a user."""
        self.login_attempts[username]["count"] += 1
        self.login_attempts[username]["last_attempt"] = datetime.now()

    def get_failed_attempts(self, username: str) -> int:
        """Get the number of failed login attempts for a user."""
        return self.login_attempts[username]["count"]

    def reset_failed_attempts(self, username: str):
        """Reset the failed login attempt count after a successful login."""
        self.login_attempts[username] = {"count": 0, "last_attempt": None}

    async def verifyPassword(self, password:str, hashed_password:str) -> bool:
        """Verify the password for a user."""
        async with DB() as db:
            
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
