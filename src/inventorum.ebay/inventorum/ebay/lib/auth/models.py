# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging


log = logging.getLogger(__name__)


class AuthenticableModelMixin(object):
    """
    Ensures the required django interface for authenticable database models

    For more information, see: https://docs.djangoproject.com/en/1.7/topics/auth/customizing/
    """
    # TODO jm: What else needs to be added?

    def is_authenticated(self):
        """ Authenticable models are always authenticated """
        return True

    def is_anonymous(self):
        """ Authenticable models are never anonymous """
        return False
