# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import os

import celery
from celery import signals
from celery.utils.log import get_task_logger
from django.conf import settings
from inventorum.util.celery import CeleryBaseMiddleware


log = get_task_logger(__name__)


class Celery(celery.Celery):

    def on_configure(self):
        # raven integration (http://raven.readthedocs.org/en/latest/integrations/celery.html)
        import raven
        from raven.contrib.celery import register_signal, register_logger_signal
        # RAVEN_CONFIG is only defined in `staging.ini` and `production.ini`
        if hasattr(settings, "RAVEN_CONFIG"):
            client = raven.Client(settings.RAVEN_CONFIG['dsn'])

            # register a custom filter to filter out duplicate logs
            register_logger_signal(client)

            # hook into the Celery error
            register_signal(client)


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorum_ebay.settings')

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
        log.error(exc, exc_info=True, extra={
            "task_id": task_id,
            "task_execution_context": context,
            "rid": context.request_id
        })
