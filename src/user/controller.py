import os
from email import header
from typing import Annotated

import jwt
from fastapi import APIRouter, BackgroundTasks, Form, Request
from fastapi.responses import RedirectResponse

from src.database.service import Connection
from src.templating.service import render
from src.user import service
from src.user.forms import LoginForm
from src.user.models import User
from src.user.service import UserService
from src.utils import redirect

router = APIRouter(prefix="/user")

FormStr = Annotated[str, Form()]


@router.get("/login")
async def login(r: Request, next: str = "/"):
    return render("user/login.html", r, {"next": next})


@router.get("/signup")
def signup(r: Request, next: str = "/"):
    return render("user/signup.html", r, {"next": next})


@router.get("/sent")
def sent(r: Request):
    return render("/user/sent.html", r)


@router.post("/login")
async def send_login_link(r: Request, form: LoginForm, service: UserService):
    if not await service.user_exists(form.email):
        cx = {"error": f'The email "{form.email}" is not registered.'}
        return render("user/login.html", r, cx)

    await service.send_access_link(form.email, form.next)
    return RedirectResponse(f"/user/sent", status_code=303)


@router.post("/signup")
async def send_signup_link(r: Request, form: LoginForm, service: UserService):
    print("/signup")
    if await service.user_exists(form.email):
        print("/signup error")
        cx = {"error": f'The email "{form.email}" is already registered.'}
        return render("user/signup.html", r, cx)
    print("/send access link")
    await service.send_access_link(form.email, form.next)
    return RedirectResponse(f"/user/sent", status_code=303)


@router.get("/access")
async def handle_access_link(token: str, next: str, r: Request, service: UserService):
    try:
        auth = await service.verify_token(token)
        response = RedirectResponse(next)
        response.set_cookie("auth", auth)
        return response
    except jwt.exceptions.ExpiredSignatureError:
        return render("user/expired-token.html", r)
