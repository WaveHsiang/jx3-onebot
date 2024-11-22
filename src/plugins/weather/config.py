from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    weather_api_key: str
