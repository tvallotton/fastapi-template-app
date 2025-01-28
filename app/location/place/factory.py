from pydantic import BaseModel

from app.database.factory import Factory
from app.location.city.factory import CityFactory
from app.location.place.models import Place
from app.utils import dependency


@dependency()
class PlaceFactory(BaseModel):
    place_factory: Factory[Place]
    city_factory: CityFactory

    async def create(self, **data):
        city = await self.city_factory.create()
        return await self.place_factory.create(**data, city_id=city.id)
