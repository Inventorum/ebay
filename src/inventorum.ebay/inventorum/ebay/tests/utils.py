# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import json
import logging
import os
from inventorum.ebay import settings
import mock


log = logging.getLogger(__name__)


class PatchMixin(object):

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()


class AssertionMixin(object):

    def assertPrecondition(self, first, second, msg=None):
        self.assertEqual(first, second, msg)

    def assertPostcondition(self, first, second, msg=None):
        self.assertEqual(first, second, msg)

    def assertDecimal(self, first, second, msg=None):
        first = Decimal(str(first))
        second = Decimal(str(second))
        self.assertEqual(first, second, msg)


class JSONFixture(object):

    @classmethod
    def load(cls, path):
        file_path = os.path.join(settings.FIXTURE_DIR, path)

        with open(file_path) as data:
            data = json.load(data)

        return data