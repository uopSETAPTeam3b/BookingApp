from dataclasses import dataclass
from api import API
from database import User


class AccountManager(API):
    prefix = "/account"

    def __init__(self):
        super().__init__()
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/logout", self.logout, methods=["POST"])
        self.router.add_api_route("/register", self.register, methods=["POST"])

    @dataclass
    class Login:
        username: str
        password: str

    def login(self, login: Login) -> str:  # Needs to return either a token or a error message for the client (probably json)
        return ""

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
        return ""

    def _get_user(self, token: str) -> User:
        # Not API method
        return User("")
