# -*- coding: utf-8 -*-

# this is a namespace package
from inventorum.ebay.apps.core_api import PublishStates

__import__('pkg_resources').declare_namespace(__name__)


class EbayProductPublishingStatus(object):
    DRAFT = 1
    IN_PROGRESS = 2
    PUBLISHED = 3
    UNPUBLISHED = 4
    FAILED = 5

    CHOICES = (
        (DRAFT, "Draft"),
        (IN_PROGRESS, "In progress"),
        (PUBLISHED, "Published"),
        (FAILED, "Failed"),
    )

    CORE_API_MAP = {
        IN_PROGRESS: PublishStates.IN_PROGRESS,
        PUBLISHED: PublishStates.PUBLISHED,
        FAILED: PublishStates.FAILED
    }

    @classmethod
    def core_api_state(cls, state):
        return cls.CORE_API_MAP.get(state, None)