# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging

import factory
from factory import fuzzy
from inventorum.ebay.lib.db.models import MappedInventorumModelFactory

from inventorum.ebay.apps.accounts import models
from inventorum.ebay.tests import StagingTestAccount


log = logging.getLogger(__name__)


class EbayAccountFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayAccountModel

    user_id = fuzzy.FuzzyText(length=10)
    email = factory.Sequence(lambda n: 'test{0}@inventorum.com'.format(n))
    country = StagingTestAccount.COUNTRY


class EbayUserFactory(MappedInventorumModelFactory):

    class Meta:
        model = models.EbayUserModel

    account = factory.SubFactory(EbayAccountFactory)
