from uuid import uuid4
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from src.templating.service import render
from src.user.dependencies import UserGuard


router = APIRouter()


@router.get("/")
def home(r: Request, user: UserGuard):
    return render("home/index.html", r, {"user": user})
