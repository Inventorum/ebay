# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import os

from celery import Celery
from celery.signals import task_prerun, task_postrun
from django.conf import settings
from inventorum.util.celery import initialize_celery_context


log = logging.getLogger(__name__)


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorum.ebay.settings')

app = Celery('ebay')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@task_prerun.connect()
def task_prerun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None):
    initialize_celery_context(task)

@task_postrun.connect()
def task_postrun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None):
    pass
