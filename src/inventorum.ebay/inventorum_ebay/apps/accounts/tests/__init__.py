# -*- coding: utf-8 -*-
from inventorum_ebay.apps.returns import ReturnsAcceptedOption, ReturnsWithinOption, ShippingCostPaidByOption
from inventorum_ebay.apps.returns.models import ReturnPolicyModel


class AccountTestMixin(object):

    def prepare_account_for_publishing(self, account):
        """
        Ensures that the eBay account is configured correctly for publishing

        :type account: inventorum_ebay.apps.accounts.models.EbayAccountModel
        """
        # configure a valid return policy
        account.return_policy = ReturnPolicyModel.create(
            returns_accepted_option=ReturnsAcceptedOption.ReturnsAccepted,
            returns_within_option=ReturnsWithinOption.Days_14,
            shipping_cost_paid_by_option=ShippingCostPaidByOption.Seller,
            description='The article can be returned to the given conditions')
        account.save()
