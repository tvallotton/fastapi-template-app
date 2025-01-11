import re
import uuid
from os import environ
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import UUID4, BaseModel, Field

JWT_SECRET_KEY = environ["JWT_SECRET_KEY"]


class Token(BaseModel):
    user_id: uuid.UUID
    is_admin: bool


def authenticate(r: Request):
    if r.method == "GET" and r.cookies.get("auth"):
        value = r.cookies.get("auth")
        try:
            if value:
                return Token(**jwt.decode(value, JWT_SECRET_KEY, algorithms="HS256"))
        except:
            pass

    authorization = r.headers.get("authorization", None)
    if authorization is None:
        return

    match = re.match(r"^Bearer (.+)$", authorization)

    if match is None:
        return

    try:
        return Token(**jwt.decode(match[1], JWT_SECRET_KEY, algorithms=["HS256"]))
    except:
        return


def authenticate_or_redirect(r: Request):
    token = authenticate(r)
    if token is None:
        raise HTTPException(
            status_code=303, headers={"Location": f"/user/login?next={r.url.path}"}
        )
    return token


def admin_user(r: Request):
    user = authenticate_or_redirect(r)
    if not user.is_admin:
        raise HTTPException(status_code=403)


OptionalUserGuard = Annotated[Token | None, Depends(authenticate)]
UserGuard = Annotated[Token, Depends(authenticate_or_redirect)]
AdminUserGuard = Annotated[Token, Depends(admin_user)]
