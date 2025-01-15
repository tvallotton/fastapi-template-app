
from fastapi import APIRouter, Request

from src.templating.service import render
from src.user.dependencies import UserGuard

router = APIRouter()


@router.get("/")
def home(r: Request, user: UserGuard):
    return render("home/index.html", r, {"user": user})
