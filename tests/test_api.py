import os
from typing import Any

from falcon import testing


class TestApi:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
        }
        os.environ['TEST_ACCESS'] = '1'
        import server
        self.client = testing.TestClient(server.app)

    def post(self, sub_url, data: Any) -> Any:
        return self.client.simulate_post('/' + sub_url, json=data, headers=self.headers)

    def get(self, sub_url) -> Any:
        return self.client.simulate_get('/' + sub_url, headers=self.headers)

    def patch(self, sub_url, data: Any) -> Any:
        return self.client.simulate_patch('/' + sub_url, json=data, headers=self.headers)

    def delete(self, sub_url) -> Any:
        return self.client.simulate_delete('/' + sub_url, headers=self.headers)

    def get_card_id(self) -> testing.Result:
        return self.get('card')

    def get_bay_open(self, bay_id: str) -> bool:
        return self.get(f'bays/{bay_id}').json['open']

    def post_open_bay(self, bay_id: str):
        return self.post(f'bays/{bay_id}/open', None)
