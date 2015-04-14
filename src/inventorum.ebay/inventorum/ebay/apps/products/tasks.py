# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.util.celery import inventorum_task


@inventorum_task()
def foo(self):
    raise Exception("WAT")
