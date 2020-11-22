import httpx
from fastapi import APIRouter, Body
from starlette.responses import Response
from typing import Optional

from device_server.card.reader import CardReader
from device_server.config import config
from device_server.model.auth import AuthenticationResult, CardModel

router = APIRouter()
card_reader: Optional[CardReader] = None


@router.on_event('startup')
async def card_startup():
    global card_reader
    assert card_reader is None, "Already initialized"
    card_reader = CardReader(config.card_auth)
    card_reader.start()


@router.on_event('shutdown')
async def card_shutdown():
    global card_reader
    assert card_reader is not None, "Not initialized"
    card_reader.stop()
    card_reader = None


@router.get(
    '',
    tags=['Auth'],
    response_model=AuthenticationResult,
    responses={404: {'model': CardModel}},
)
async def get_card():
    """Gets the authentication result. If 404 is returned, a card was found but not registered yet."""
    card_id = card_reader.read_card_id()
    if card_id is None:
        return Response(status_code=204)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.card_auth.server_url}/card/authorize",
            json=CardModel(card_id=card_id).dict(),
            headers={'X-Card-Api-Key': config.card_auth.card_login_api_key},
        )
    if response.status_code == 404:
        return CardModel(card_id=card_id)
    return Response(content=response.content, status_code=response.status_code, headers=response.headers)


@router.post(
    'register',
    tags=['Auth'],
)
async def register_card(card: CardModel = Body(...)):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.card_auth.server_url}/card/register",
            json=card.dict(),
            headers={'X-Card-Api-Key': config.card_auth.card_login_api_key},
        )
    return Response(content=response.content, status_code=response.status_code, headers=response.headers)
