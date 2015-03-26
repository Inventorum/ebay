# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory

from inventorum.ebay.apps.products import models


log = logging.getLogger(__name__)


class EbayProductFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.EbayProductModel

    inv_id = factory.Sequence(lambda n: n)
    account = factory.SubFactory(EbayAccountFactory)
