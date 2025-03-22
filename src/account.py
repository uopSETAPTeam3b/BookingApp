from dataclasses import dataclass
from api import API
from database import User, DatabaseManager as db
from collections import defaultdict
from datetime import datetime, timedelta

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

    def login(self, login: Login) -> str:  # Needs to return either a token or a error message for the client (probably json)
        """ Returns the users token if login succeful"""
        user_passwrd = db.get_passwrd(login.username)
        if login.password == user_passwrd:
            self.reset_failed_attempts(login.username)
            return db.create_token(login.username) #successful login
        else:
            if self.get_failed_attempts(login.username) > 3:
                return "" #error, lock out user or require email verify or pass reset
            self.record_failed_attempt(login.username)
        return "" #error need help ben pls

    @dataclass
    class Logout:
        token: str

    def logout(self, logout: Logout) -> None:
        pass

    @dataclass
    class Register:
        username: str
        password: str

    # Needs to return either a token or an error message for the client (probably json)
    def register(self, register: Register) -> str:
        """ creates user and returns token """
        user = db.get_user_from_username(register.username)
        if user != None:
            token = db.create_user(register.username, register.password)
            return token
        return "" #error

    def get_user(self, token: str) -> User:
        # Not API method
        return User("")
    
    def record_failed_attempt(self,username: str):
        """Record a failed login attempt for a user."""
        self.failed_attempts[username]["count"] += 1
        self.failed_attempts[username]["last_attempt"] = datetime.now()

    def get_failed_attempts(self, username: str) -> int:
        """Get the number of failed login attempts for a user."""
        return self.failed_attempts[username]["count"]

    def reset_failed_attempts(self, username: str):
        """Reset the failed login attempt count after a successful login."""
        self.failed_attempts[username] = {"count": 0, "last_attempt": None}
