# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
import os

from celery import Celery
from celery.signals import task_prerun, task_postrun
from django.conf import settings


log = logging.getLogger(__name__)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventorum.ebay.settings')

app = Celery('ebay')

# Note: auto-discovery for celery task does not work properly, you can list modules with shared tasks
# in `settings.py` under `CELERY_IMPORTS` explicitly
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@task_prerun.connect()
def task_prerun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None):
    # TODO jm
    pass

@task_postrun.connect()
def task_postrun(signal=None, sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None):
    # TODO jm
    pass
