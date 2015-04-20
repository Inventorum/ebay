# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.util.celery import inventorum_task


log = logging.getLogger(__name__)


@inventorum_task()
def foo(self):
    raise Exception("celery works!")
