from typing import Literal

from pydantic import BaseModel


class OpenAddressesGeometry(BaseModel):
    type: Literal["Point"]
    coordinates: list[float]


class OpenAddressesProperties(BaseModel):
    id: int
    street: str
    number: str
    city: str
    region: str


class OpenAddressesRecord(BaseModel):
    geometry: OpenAddressesGeometry
    properties: OpenAddressesProperties
