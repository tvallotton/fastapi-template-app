import re
import uuid
from os import environ
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import UUID4, BaseModel, Field

JWT_SECRET_KEY = environ["JWT_SECRET_KEY"]


def authorization(r: Request):
    if r.method == "GET" and r.cookies.get("auth"):
        value = r.cookies.get("auth")
        try:
            return Token(**jwt.decode(value, JWT_SECRET_KEY, algorithms="HS256"))  # type: ignore
        except:
            pass

    authorization = r.headers.get("authorization", None)
    if authorization is None:
        return

    match = re.match(r"^Bearer (.+)$", authorization)

    if match is None:
        return

    try:
        return Token(**jwt.decode(match[1], JWT_SECRET_KEY, algorithms=["HS256"]))  # type: ignore
    except:
        return


def auth_or_redirect(r: Request):
    token = authorization(r)
    if token is None:
        raise HTTPException(
            status_code=303, headers={"Location": f"/user/login?next={r.url.path}"}
        )
    return token


class Token(BaseModel):
    user_id: uuid.UUID
    is_admin: bool


UserGuard = Annotated[Token, Depends(auth_or_redirect)]
OptionalUserGuard = Annotated[Token | None, Depends(authorization)]
