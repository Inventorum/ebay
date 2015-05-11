# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import os

from celery import Celery
from django.conf import settings
from inventorum.util.celery import CeleryBaseMiddleware


log = logging.getLogger(__name__)


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorum.ebay.settings')

app = Celery('ebay')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


class CeleryMiddleware(CeleryBaseMiddleware):

    def handle_exception(self, exc, task, task_id, args, kwargs, einfo, context):
        """
        :type exc: Exception
        :type task: InventorumTask
        :type task_id: unicode
        :type args: tuple
        :type kwargs: dict
        :type einfo:
        :type context: inventorum.util.celery.TaskExecutionContext
        """
        log.exception(exc, extra={
            "task_id": task_id,
            "task_execution_context": context
        })
