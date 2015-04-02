# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
from django.conf import settings
import vcr


log = logging.getLogger(__name__)


class CoreApiTest(object):
    vcr = vcr.VCR(
        serializer='json',
        cassette_library_dir=os.path.join(settings.CASSETTES_DIR, 'core_api'),
        record_mode='once'
    )
