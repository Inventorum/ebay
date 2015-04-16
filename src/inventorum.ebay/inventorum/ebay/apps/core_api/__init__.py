# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.core_api.pager import Pager


log = logging.getLogger(__name__)


class FakeResponse(object):
    """
    Very simple fake object for `requests.models.Request`, which mocks a small subset of the original interface
    """
    def __init__(self, status_code=200, json=None):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json


class PaginatedFakeResponse(FakeResponse):

    def __init__(self, status_code=200, total=0, data=None):
        if data is None:
            data = []

        super(PaginatedFakeResponse, self).__init__(status_code, json={
            "total": total,
            "data": data
        })
