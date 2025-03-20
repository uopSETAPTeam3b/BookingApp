from fastapi import APIRouter


class API:
    prefix = "API"

    def __init__(self):
        self.router = APIRouter(prefix=self.prefix)
