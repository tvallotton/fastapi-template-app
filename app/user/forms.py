from pydantic import BaseModel

from app.utils import form


@form()
class LoginForm(BaseModel):
    email: str
    next: str = "/"
