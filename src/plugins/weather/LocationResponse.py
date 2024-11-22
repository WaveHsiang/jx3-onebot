from pydantic import BaseModel
from typing import List

class Location(BaseModel):
    name: str
    id: str
    lat: str
    lon: str
    adm2: str
    adm1: str
    country: str
    tz: str
    utcOffset: str
    isDst: str
    type: str
    rank: str
    fxLink: str

class Refer(BaseModel):
    sources: List[str]
    license: List[str]

class LocationResponse(BaseModel):
    code: str
    location: List[Location]
    refer: Refer

# [详见文档](https://dev.qweather.com/docs/api/geoapi/city-lookup/)