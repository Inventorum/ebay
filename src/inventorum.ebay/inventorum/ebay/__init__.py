# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

log = logging.getLogger(__name__)

# This will make sure the celery app is always imported when
# django starts so that shared_task will use this app.
from .celery import app as celery_app

import os

config_file_name = os.environ.get('PYRAMID_SETTINGS', None)
if config_file_name:
    import pyramid.paster
    pyramid.paster.setup_logging(config_file_name)
    app = pyramid.paster.get_app(config_file_name)
