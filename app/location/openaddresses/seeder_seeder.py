from pydantic import BaseModel

from app.location.openaddresses.service import OpenAddressesService
from app.utils import dependency

SEEDER_PATH = "app/location/openaddresses/seeder-data.geojson"


@dependency()
class OpenAddressesSeederService(BaseModel):
    open_addresses_service: OpenAddressesService

    async def seed(self):
        records = self.open_addresses_service.parse_records(SEEDER_PATH)
        for record in records:
            await self.open_addresses_service.save_record(record)
