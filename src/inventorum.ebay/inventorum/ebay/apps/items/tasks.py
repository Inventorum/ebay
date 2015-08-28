from inventorum.ebay.apps.accounts.models import EbayAccountModel
from inventorum.util.celery import inventorum_task


@inventorum_task()
def ebay_items_sync(self, account_id):
    """
    :type self: inventorum.util.celery.InventorumTask
    :type account_id: int
    """
    from inventorum.ebay.apps.items.ebay_items_sync_services import EbayItemsSync

    account = EbayAccountModel.objects.get(id=account_id)
    EbayItemsSync(account)

