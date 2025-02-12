from typing import Annotated

import jwt
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.templating.service import render
from app.user.exceptions import (
    EmailAlreadyRegisteredException,
    UnregisteredEmailException,
)
from app.user.forms import LoginForm
from app.user.service import UserService

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
    try:
        await service.send_login_link(form.email, form.next)
        return RedirectResponse(f"/user/sent", status_code=303)
    except UnregisteredEmailException:
        cx = {"error": f'The email "{form.email}" is not registered.'}
        return render("user/login.html", r, cx)


@router.post("/signup")
async def send_signup_link(r: Request, form: LoginForm, service: UserService):
    try:
        await service.send_signup_link(form.email, form.next)
        return RedirectResponse(f"/user/sent", status_code=303)
    except EmailAlreadyRegisteredException:
        cx = {"error": f'The email "{form.email}" is already registered.'}
        return render("user/signup.html", r, cx)


@router.get("/access")
async def handle_access_link(token: str, next: str, r: Request, service: UserService):
    try:
        auth = await service.verify_token(token)
        response = RedirectResponse(next)
        response.set_cookie("auth", auth)
        return response
    except jwt.exceptions.ExpiredSignatureError:
        return render("user/expired-token.html", r)
