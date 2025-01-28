import json

from pydantic import BaseModel

from app.database.repository import Repository
from app.location.city.models import City
from app.location.openaddresses.models import OpenAddressesRecord
from app.location.place.models import Place
from app.location.region.models import Region


class OpenAddressesService(BaseModel):
    region_repository: Repository[Region]
    city_repository: Repository[City]
    place_repository: Repository[Place]

    async def import_addresses(self, filename: str):
        for record in self.parse_records(filename):
            await self.save_record(record)

    def parse_records(self, filename: str):
        with open(filename) as file:
            for line in file:
                data = json.loads(line)
                yield OpenAddressesRecord(**data)

    async def save_record(self, record: OpenAddressesRecord):
        city = await self.get_city(record)
        number = record.properties.number
        number = None if number == "SN" else number
        street = self.normalize_name(record.properties.street)
        await self.place_repository.save(
            Place(
                id=record.properties.id,
                number=number,
                street=street,
                longitude=record.geometry.coordinates[0],
                latitude=record.geometry.coordinates[1],
                city_id=city.id,
            )
        )

    async def get_city(self, record: OpenAddressesRecord):
        async with self.city_repository.transaction():
            city_name = self.normalize_name(record.properties.city)
            city = await self.city_repository.find_one(id=city_name)
            if city is not None:
                return city
            region = await self.get_region(record)
            return await self.city_repository.save(
                City(id=city_name, region_id=region.id)
            )

    async def get_region(self, record: OpenAddressesRecord):
        async with self.region_repository.transaction():
            region_name = self.normalize_name(record.properties.region)
            region = await self.region_repository.find_one(id=region_name)
            if region is not None:
                return region
            return await self.region_repository.save(Region(id=region_name))

    def normalize_name(self, name):
        lowercased = {"de", "en", "el", "la", "lo", "las", "los", "del"}

        replacements = {f" {word} ".title(): f" {word} " for word in lowercased}
        name = name.title()
        for target, replacement in replacements.items():
            name = name.title().replace(target, replacement)

        return name
