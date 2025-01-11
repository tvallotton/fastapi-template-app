from typing import Annotated

from fastapi import Form
from pydantic import BaseModel

from src.utils import form


@form()
class LoginForm(BaseModel):
    email: str
    next: str = "/"
