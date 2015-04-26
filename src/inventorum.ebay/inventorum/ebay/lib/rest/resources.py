# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.util.celery import TaskExecutionContext
from rest_framework.generics import GenericAPIView
from inventorum.ebay.lib.rest.permissions import IsEbayAuthenticated

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


log = logging.getLogger(__name__)


class PublicAPIResource(APIView):
    permission_classes = ()


class UnauthorizedEbayAPIResource(GenericAPIView):
    permission_classes = (IsAuthenticated,)


class APIResource(UnauthorizedEbayAPIResource):
    permission_classes = UnauthorizedEbayAPIResource.permission_classes + (IsEbayAuthenticated, )

    def get_task_execution_context(self):
        """
        Creates an execution context for celery tasks from the current request
        :rtype: TaskExecutionContext
        """
        user = self.request.user
        account = user.account
        request_id = self.request.dispatch_uid

        return TaskExecutionContext(
            user_id=user.id,
            account_id=account.id,
            request_id=request_id
        )
