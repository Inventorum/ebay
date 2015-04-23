# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import mock


log = logging.getLogger(__name__)


class PatchMixin(object):

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()
