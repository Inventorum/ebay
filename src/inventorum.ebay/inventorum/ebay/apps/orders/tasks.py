# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging


from inventorum.util.celery import inventorum_task


log = logging.getLogger(__name__)


@inventorum_task()
def core_order_creation_task(self, order_id):
    pass


def schedule_core_order_creation(order_id, context):
    """
    :type order_id: int
    :type context: inventorum.util.celery.TaskExecutionContext
    """
    core_order_creation_task.delay(order_id=order_id, context=context)
