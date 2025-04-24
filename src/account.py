from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass
from api import API
from database import User, DatabaseManager

class AccountManager(API):
    prefix = "/account"

    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/logout", self.logout, methods=["POST"])
        self.router.add_api_route("/register", self.register, methods=["POST"])
        self.login_attempts = defaultdict(lambda: {"count": 0, "last_attempt": None})

    @dataclass
    class Login:
        username: str
        password: str

    def login(self, login: Login) -> str:
        # Needs to return either a token or a error message for the client (probably json)
        """ Returns the users token if login succeful"""
        user: User = self.db.get_user_from_username(login.username)
        user_password = self.db.get_password(user)
        if login.password == user_password:
            self.reset_failed_attempts(user.username)
            return self.db.create_token(user) #successful login
        if self.get_failed_attempts(user.username) > 3:
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
        user = self.db.get_user_from_username(register.username)
        if user is not None:
            token = self.db.create_user(register.username, register.password)
            return token
        return "" #error

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
