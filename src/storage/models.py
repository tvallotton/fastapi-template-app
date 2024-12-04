from src.database.models import BaseModel


class Storage(BaseModel):
    bucket: str
    sha1: bytes
