# encoding: utf-8
from __future__ import absolute_import, unicode_literals

import logging

log = logging.getLogger(__name__)


class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        logging.exception('Exception handling request for ' + request.path)