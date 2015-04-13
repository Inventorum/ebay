# -*- coding: utf-8 -*-

# this is a namespace package
__import__('pkg_resources').declare_namespace(__name__)


class EbayProductPublishingStatus(object):
    DRAFT = 1
    IN_PROGRESS = 2
    PUBLISHED = 3

    CHOICES = (
        (DRAFT, "Draft"),
        (IN_PROGRESS, "In progress"),
        (PUBLISHED, "Published")
    )