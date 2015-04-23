# encoding: utf-8
from __future__ import absolute_import, unicode_literals
import logging
from inventorum.ebay.apps.accounts.tests.factories import EbayUserFactory
from inventorum.ebay.apps.products.models import EbayProductModel
from inventorum.ebay.apps.products.services import ProductDeletionService, UnpublishingService
from inventorum.ebay.apps.products.tests.factories import EbayProductFactory, PublishedEbayItemFactory
from inventorum.ebay.tests.testcases import UnitTestCase
from mock import Mock


log = logging.getLogger(__name__)


class TestDeletionService(UnitTestCase):

    def setUp(self):
        super(TestDeletionService, self).setUp()

        self.user = EbayUserFactory.create()
        self.account = self.user.account

        self.product = EbayProductFactory.create()

        self.mock_dependencies()

    def mock_dependencies(self):
        unpublishing_service = "inventorum.ebay.apps.products.services.UnpublishingService"
        self.unpublishing_service_ctor_mock = self.patch(unpublishing_service)

        self.unpublishing_service = Mock(spec_set=UnpublishingService)
        self.unpublishing_service_ctor_mock.return_value = self.unpublishing_service

    def test_deletion_of_unpublished_products(self):

        subject = ProductDeletionService(self.product, user=self.user)
        subject.delete()

        with self.assertRaises(EbayProductModel.DoesNotExist):
            EbayProductModel.objects.get(id=self.product.id)

    def test_deletion_of_published_products(self):
        published_item = PublishedEbayItemFactory.create(product=self.product, id=1337)

        subject = ProductDeletionService(self.product, user=self.user)
        subject.delete()

        self.assertTrue(self.unpublishing_service_ctor_mock.called)
        ctor_args = self.unpublishing_service_ctor_mock.call_args[0]
        self.assertEqual(ctor_args[0] and ctor_args[0].id, 1337)

        self.assertTrue(self.unpublishing_service.unpublish.called)
