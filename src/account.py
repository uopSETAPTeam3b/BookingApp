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
        self.router.add_api_route("/me", self.me, methods=["POST"])
        self.login_attempts = defaultdict(lambda: {"count": 0, "last_attempt": None})

    @dataclass
    class Login:
        username: str
        password: str

    async def me(self, token: str) -> JSONResponse:
        """ Returns the user object for the given token """
        async with DB() as db:
            user: User = await db.get_user_from_token(token)
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
                return JSONResponse(content={"token": token}, status_code=200)  # ✅ Fixed here

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
