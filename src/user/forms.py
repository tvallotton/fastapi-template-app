from pydantic import BaseModel
from fastapi import Form
from typing import Annotated


class Login(BaseModel):
    email: str
    next: str = "/"


LoginForm = Annotated[Login, Form()]
