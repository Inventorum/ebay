# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory

from inventorum.ebay.apps.accounts import models


log = logging.getLogger(__name__)


class EbayAccountFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayAccountModel

    inv_id = factory.Sequence(lambda n: n)


class EbayUserFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayUserModel

    inv_id = factory.Sequence(lambda n: n)
    account = factory.SubFactory(EbayAccountFactory)
