import httpx
from fastapi.testclient import TestClient
from typing import Optional

import device_server.api.auth
from device_server.api import app
from device_server.card.reader import CardAuthConfig
from device_server.config import config


class MockCardReader:
    card_id: Optional[str] = None
    config: Optional[CardAuthConfig] = None

    def start(self):
        pass

    def stop(self):
        pass

    def read_card_id(self) -> str:
        return self.card_id

    def __call__(self, config: CardAuthConfig):
        self.config = config
        return self


class MockAsyncClient:

    calls = []

    async def post(
            self,
            url: str,
            **kwargs
    ) -> httpx.Response:
        self.calls.append(('POST', url, kwargs))
        return httpx.Response(200, request=httpx.Request(
            'POST',
            url,
            params=kwargs.get('params'),
            headers=kwargs.get('headers'),
            cookies=kwargs.get('cookies'),
            data=kwargs.get('data'),
            files=kwargs.get('files'),
            json=kwargs.get('json'),
        ))

    def __call__(self, *args, **kwargs):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def test_card_auth(monkeypatch):
    config.card_auth.card_associate_login_timeout = 0.1
    config.card_auth.card_login_api_key = 'ABC'
    config.card_auth.server_url = 'http://localhost/test'

    mock_card_reader = MockCardReader()
    monkeypatch.setattr(device_server.api.auth, 'CardReader', mock_card_reader)
    mock_async_client = MockAsyncClient()
    monkeypatch.setattr(httpx, 'AsyncClient', mock_async_client)

    with TestClient(app) as client:
        assert mock_card_reader.config == config.card_auth

        resp = client.get('/api/v1/auth')
        assert resp.status_code == 204, resp.text

        mock_card_reader.card_id = 'CARD_ID_0'
        resp = client.get('/api/v1/auth')
        assert resp.status_code == 200, resp.text

        assert len(mock_async_client.calls) == 1
        assert mock_async_client.calls[0] == (
            'POST',
            'http://localhost/test/card/authorize',
            {
                'json': {'card_id': 'CARD_ID_0'},
                'headers': {'X-Card-Api-Key': config.card_auth.card_login_api_key},
            },
        )
