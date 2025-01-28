from pydantic import BaseModel

from app.database.factory import Factory
from app.location.city.models import City
from app.location.region.models import Region
from app.utils import dependency


@dependency()
class CityFactory(BaseModel):

    city_factory: Factory[City]
    region_factory: Factory[Region]

    async def create(self, **data):
        region = await self.region_factory.create()
        return await self.city_factory.create(region_id=region.id)
