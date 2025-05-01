from collections import defaultdict
from fastapi.responses import JSONResponse
from datetime import datetime
from dataclasses import dataclass
from api import API
from database import User, DB
import bcrypt

class AccountManager(API):
    prefix = "/account"

    def __init__(self):
        super().__init__()
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/logout", self.logout, methods=["POST"])
        self.router.add_api_route("/register", self.register, methods=["POST"])
        self.login_attempts = defaultdict(lambda: {"count": 0, "last_attempt": None})

    @dataclass
    class Login:
        username: str
        password: str

    async def login(self, login: Login) -> str:
        print(f"Login attempt for {login.username}")
        # Needs to return either a token or a error message for the client (probably json)
        """ Returns the users token if login succeful"""
        async with DB() as db:
            user: User = await db.get_user_from_username(login.username)
            if user is None:
                print(f"User not found: {login.username}")
                return JSONResponse(content={"message": "Invalid username or password"}, status_code=400)
            password = await db.get_password(user)
            print(f"User found: {user.username}")
            loginStatus = await self.verifyPassword(login.password, password)
            if  loginStatus:
                token = await db.create_token(user)
                #self.reset_failed_attempts(user.username)
                print(f"Login successful: {user.username} & {token}")
                return JSONResponse(content={"token": token}, status_code=400)
            print(f"Login incorrect password: {user.username}")
            # If the user is not found or the password is incorrect, record the failed attempt
            if self.get_failed_attempts(user.username) > 3:
                return JSONResponse(content={"message": "Too many failed attempts: Please try contact support"}, status_code=400) #error, lock out user or require email verify or pass reset
            self.record_failed_attempt(user.username)
            return JSONResponse(content={"message": "Invalid username or password"}, status_code=400) #error need help ben pls

    @dataclass
    class Logout:
        token: str

    def logout(self, logout: Logout) -> str:
        return ""

    @dataclass
    class Register:
        username: str
        password: str

    # Needs to return either a token or an error message for the client (probably json)
    async def register(self, register: Register) -> str:
        """ creates user and returns token """
        async with DB() as db:
            user = await db.get_user_from_username(register.username)
            if user is None:
                token = await db.create_user(register.username, register.password, "")
                print(f"OMG the token is {token}")
                return token or ""
            return ""  # error

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
            #user: User = await db.get_user_from_username(login.username)
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
