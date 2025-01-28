
from app.database.models import BaseModel


class City(BaseModel):
    id: str  # type: ignore
    region_id: str
