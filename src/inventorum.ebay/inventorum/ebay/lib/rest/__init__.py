# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from rest_framework import pagination
from rest_framework.response import Response


log = logging.getLogger(__name__)


class APIPagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data):
        return Response({
            "links": {
                "next": self.get_next_link(),
                "previous": self.get_previous_link()
            },
            "total": self.page.paginator.count,
            "data": data
        })
