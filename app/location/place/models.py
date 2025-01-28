from uuid import UUID

from app.database.models import BaseModel


class Place(BaseModel):
    id: int  # type: ignore
    street: str
    number: str | None
    latitude: float
    longitude: float
    city_id: str
    address: str | None = None
