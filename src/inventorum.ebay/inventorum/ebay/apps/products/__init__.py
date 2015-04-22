# -*- coding: utf-8 -*-

# this is a namespace package
from inventorum.ebay.apps.core_api import PublishStates

__import__('pkg_resources').declare_namespace(__name__)


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


class EbayApiAttemptType(object):
    PUBLISH = 'publish'
    UNPUBLISH = 'unpublish'

    CHOICES = (
        (PUBLISH, 'Publish'),
        (UNPUBLISH, 'Unpublish')
    )
