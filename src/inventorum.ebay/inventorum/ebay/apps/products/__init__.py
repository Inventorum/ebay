# -*- coding: utf-8 -*-
# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

from inventorum.ebay.apps.core_api import PublishStates


log = logging.getLogger(__name__)


class EbayItemPublishingStatus(object):
    DRAFT = 'draft'
    IN_PROGRESS = 'in_progress'
    PUBLISHED = 'published'
    UNPUBLISHED = 'unpublished'
    FAILED = 'failed'

    CHOICES = (
        (DRAFT, "Draft"),
        (IN_PROGRESS, "In progress"),
        (PUBLISHED, "Published"),
        (UNPUBLISHED, "Unpublished"),
        (FAILED, "Failed"),
    )

    CORE_API_MAP = {
        IN_PROGRESS: PublishStates.IN_PROGRESS,
        PUBLISHED: PublishStates.PUBLISHED,
        FAILED: PublishStates.FAILED,
        UNPUBLISHED: PublishStates.UNPUBLISHED
    }

    @classmethod
    def core_api_state(cls, state):
        return cls.CORE_API_MAP.get(state, None)


# TODO jm: Change to string
class EbayItemUpdateStatus(object):
    DRAFT = 1
    IN_PROGRESS = 2
    SUCCEEDED = 3
    FAILED = 4

    CHOICES = (
        (DRAFT, "DRAFT"),
        (IN_PROGRESS, "IN_PROGRESS"),
        (SUCCEEDED, "SUCCEEDED"),
        (FAILED, "FAILED"),
    )


class EbayApiAttemptType(object):
    PUBLISH = 'publish'
    UNPUBLISH = 'unpublish'

    CHOICES = (
        (PUBLISH, 'Publish'),
        (UNPUBLISH, 'Unpublish')
    )
