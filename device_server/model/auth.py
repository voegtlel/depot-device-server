from pydantic import BaseModel as PydanticBaseModel

from device_server.model.base import BaseModel


class CardModel(BaseModel):
    card_id: str


class AuthenticationResult(PydanticBaseModel):
    redirect_uri: str
