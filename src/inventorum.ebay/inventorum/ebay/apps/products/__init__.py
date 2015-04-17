# -*- coding: utf-8 -*-

# this is a namespace package
__import__('pkg_resources').declare_namespace(__name__)


class EbayProductPublishingStatus(object):
    DRAFT = 1
    IN_PROGRESS = 2
    PUBLISHED = 3
    UNPUBLISHED = 4

    CHOICES = (
        (DRAFT, "Draft"),
        (IN_PROGRESS, "In progress"),
        (PUBLISHED, "Published"),
        (UNPUBLISHED, "Unpublished"),
    )


class EbayItemUpdateStatus(object):
    DRAFT = 1
    PENDING = 2
    IN_PROGRESS = 3
    SUCCEEDED = 4
    FAILED = 5

    CHOICES = (
        (DRAFT, "DRAFT"),
        (PENDING, "PENDING"),
        (IN_PROGRESS, "IN_PROGRESS"),
        (SUCCEEDED, "SUCCEEDED"),
        (FAILED, "FAILED")
    )
