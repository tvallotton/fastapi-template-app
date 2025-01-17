from fastapi import APIRouter, Request

from app.templating.service import render
from app.user.dependencies import UserGuard

router = APIRouter()


@router.get("/")
def home(r: Request, user: UserGuard):
    return render("home/index.html", r, {"user": user})
