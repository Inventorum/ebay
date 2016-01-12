# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from django.test.utils import override_settings
from inventorum.util.celery import TaskExecutionContext
from nose.tools.nontrivial import make_decorator


log = logging.getLogger(__name__)


def get_anonymous_task_execution_context():
    """
    :rtype: inventorum.util.celery.TaskExecutionContext
    """
    return TaskExecutionContext(user_id=None, account_id=None, request_id=None)


def celery_test_case(eager=True, propagate_exceptions=True):
    """
    Decorator for test cases which execute celery tasks.

    If this decorator is applied, all delayed celery tasks are run synchronously in the main execution thread
    and exceptions thrown by these tasks are also propagated and thrown in the main thread.
    """
    def decorator(fn):
        @override_settings(CELERY_ALWAYS_EAGER=eager, CELERY_EAGER_PROPAGATES_EXCEPTIONS=propagate_exceptions)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        # Will preserve nose metadata
        return make_decorator(fn)(wrapper)
    return decorator
