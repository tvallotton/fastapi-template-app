from dotenv import load_dotenv

load_dotenv(".env")

from . import database
from .main import app
