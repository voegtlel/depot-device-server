#!/usr/bin/env python
import os

import falcon
from falcon_cors import CORS

from access import BayAccess, CardAccess
from api import bay_api, card_api
from config import config

cors = CORS(
    allow_origins_list=config['allowOrigins'],
    allow_headers_list=[
        'Content-Type', 'Authorization', 'Accept'
    ],
    allow_methods_list=['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
)


class RequireJSON:

    @staticmethod
    def _get_require_json_settings(resource) -> bool:
        return getattr(resource, 'require_json', True)

    @staticmethod
    def _get_accept_json_settings(resource) -> bool:
        return getattr(resource, 'accept_json', True)

    def process_resource(self, req: falcon.Request, resp: falcon.Response, resource, params):
        if self._get_accept_json_settings(resource) and not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json'
            )

        if self._get_require_json_settings(resource) and req.method in ('POST', 'PUT', 'PATCH'):
            if not req.content_type or 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.',
                    href='http://docs.examples.com/api/json'
                )


class MaxBody:
    def __init__(self, max_size=1*1024):
        self._max_size = max_size

    def _get_max_body_settings(self, resource) -> int:
        return getattr(resource, 'max_body_size', self._max_size)

    def process_resource(self, req: falcon.Request, resp: falcon.Response, resource, params):
        length = req.content_length
        if length is not None and length > self._get_max_body_settings(resource):
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(self._max_size) + ' bytes in length.')
            raise falcon.HTTPPayloadTooLarge('Request body is too large', msg)


app = falcon.API(
    middleware=[cors.middleware, RequireJSON(), MaxBody()],
)

if os.environ.get('TEST_ACCESS') == "1":
    from mock_access import BayAccessMock, CardAccessFileMock
    bay_access = BayAccessMock()
    card_access = CardAccessFileMock()
else:
    bay_access = BayAccess()
    card_access = CardAccess()

bay_api.register(bay_access, app)
card_api.register(card_access, app, config['cardAuth'])
