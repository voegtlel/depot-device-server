from pydantic import BaseModel, Field
from typing import Optional, List

from device_server.bay.station import StationConfig
from device_server.card.reader import CardAuthConfig


class Config(BaseModel):
    card_auth: CardAuthConfig = Field(...)
    allow_origins: List[str] = Field(...)
    station: StationConfig = Field(...)
