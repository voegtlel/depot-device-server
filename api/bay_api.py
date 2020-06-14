import falcon

from access import BayAccess

"""
The API:

/bays/{bay_id}: GET: {open: boolean}
/bays/{bay_id}/open: POST
"""


class BayApi:
    def __init__(self, bay_access: BayAccess):
        self.bay_access = bay_access

    def on_get(self, req: falcon.Request, resp: falcon.Response, bay_id: str):
        """
        Gets the bay state by id
        """
        if not self.bay_access.has_bay(bay_id):
            raise falcon.HTTPNotFound()

        resp.media = {'open': self.bay_access.is_bay_open(bay_id)}

    def register(self, app: falcon.API):
        app.add_route('/bays/{bay_id}', self)


class BayOpenApi:
    def __init__(self, bay_access: BayAccess):
        self.bay_access = bay_access

    def on_post(self, req: falcon.Request, resp: falcon.Response, bay_id: str):
        """
        Opens the bay
        """
        if not self.bay_access.has_bay(bay_id):
            raise falcon.HTTPNotFound()

        self.bay_access.open_bay(bay_id)

    def register(self, app: falcon.API):
        app.add_route('/bays/{bay_id}/open', self)


def register(bayAccess: BayAccess, app: falcon.API):
    BayApi(bayAccess).register(app)
    BayOpenApi(bayAccess).register(app)
