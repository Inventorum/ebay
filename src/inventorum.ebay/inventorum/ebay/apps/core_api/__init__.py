# -*- coding: utf-8 -*-

# this is a namespace package
__import__('pkg_resources').declare_namespace(__name__)


class PublishStates(object):
    PUBLISHED = 'published'
    UNPUBLISHED = 'unpublished'
    FAILED = 'failed'
    IN_PROGRESS = 'in_progress'
