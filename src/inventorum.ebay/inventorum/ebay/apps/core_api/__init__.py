# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.core_api.pager import Pager


log = logging.getLogger(__name__)


class PublishStates(object):
    PUBLISHED = 'published'
    UNPUBLISHED = 'unpublished'
    FAILED = 'failed'
    IN_PROGRESS = 'in_progress'


class CoreOrderStates(object):
    # all is possible with this state
    DRAFT = 1
    # temporarily frozen, waiting for money
    PENDING = 2
    # end of processing, nothing will happen, no responsibilities
    CANCELED = 4
    # frozen, indicator for ``is_paid``, can only be shipped or delivered or refunded
    CLOSED = 8
    # end of processing, has been returned
    REFUNDED = 16
    # frozen, can only be delivered or refunded
    SHIPPED = 32
    # frozen, can only be refunded. end of processing after return time.
    DELIVERED = 64
    TEST_PRINT = 128
    PAID = 256
    READ = 512


class FakeCoreAPIResponse(object):
    """
    Very simple fake object for `requests.models.Request`, which mocks a small subset of the original interface
    """
    def __init__(self, status_code=200, json=None):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json


class PaginatedFakeCoreAPIResponse(FakeCoreAPIResponse):

    def __init__(self, status_code=200, total=0, data=None):
        if data is None:
            data = []

        super(PaginatedFakeCoreAPIResponse, self).__init__(status_code, json={
            "total": total,
            "data": data
        })
