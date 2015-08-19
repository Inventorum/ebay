from inventorum.ebay.apps.accounts.tests.factories import EbayAccountFactory, EbayUserFactory
from inventorum.ebay.apps.products.models import EbayItemModel
from inventorum.ebay.tests.testcases import UnitTestCase


class UnitTestEbayItemsSyncer(UnitTestCase):
    def setUp(self):
        super(UnitTestEbayItemsSyncer, self).setUp()

        self.account = EbayAccountFactory.create()
        self.default_user = EbayUserFactory.create(account=self.account)

        self.schedule_core_order_creation_mock = \
            self.patch("inventorum.ebay.apps.orders.tasks.schedule_core_order_creation")

        self.assertPrecondition(EbayItemModel.objects.count(), 0)
