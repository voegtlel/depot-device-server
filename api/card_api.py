import falcon
from falcon_auth import JWTAuthBackend

from access import CardAccess

"""
The API:

/card: GET: {cardId: string, token: string}

"""


class CardApi:
    def __init__(self, card_access: CardAccess, config_card: dict):
        self.card_access = card_access

        self.auth_backend_card = JWTAuthBackend(
            None,
            secret_key=config_card['secretKey'],
            auth_header_prefix=config_card['headerPrefix'],
            expiration_delta=config_card['expiration']
        )

    def on_get(self, req: falcon.Request, resp: falcon.Response):
        card_id = self.card_access.get_card_id()

        if card_id is None:
            resp.media = {'cardId': None, 'token': None}
            return

        token = self.auth_backend_card.get_auth_token({'card_id': card_id})
        resp.media = {'cardId': self.card_access.get_card_id(), 'token': token}

    def register(self, app: falcon.API):
        app.add_route('/card', self)


def register(card_access: CardAccess, app: falcon.API, config_card: dict):
    CardApi(card_access, config_card).register(app)
