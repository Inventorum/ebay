# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from celery.app import shared_task


@shared_task
def publish_state(self, inv_product_id, state, details):
    pass