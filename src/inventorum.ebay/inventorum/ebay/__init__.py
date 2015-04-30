# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

log = logging.getLogger(__name__)

# This will make sure the celery app is always imported when
# django starts so that shared_task will use this app.
from .celery import app as celery_app

import os

ini = os.environ.get('PYRAMID_SETTINGS', None)
if ini:
    config_file, section_name = ini.split('#', 1)
    from paste.deploy.loadwsgi import appconfig
    import pyramid.paster

    pyramid.paster.setup_logging(config_file)
    app = pyramid.paster.get_app(config_file)
