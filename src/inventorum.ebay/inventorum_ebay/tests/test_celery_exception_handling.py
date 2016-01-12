# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
from django.test.testcases import TestCase

from inventorum.util.celery import inventorum_task, get_anonymous_task_execution_context
from inventorum.util.tests import celery_test_case


log = logging.getLogger(__name__)


class TestCeleryExceptionHandling(TestCase):

    @inventorum_task()
    def task_with_exception(self, *args, **kwargs):
        raise ZeroDivisionError("Bang")

    @celery_test_case(propagate_exceptions=False)
    def test_exception_logging(self):
        self.task_with_exception.delay(context=get_anonymous_task_execution_context())
        # assert visual exception log
