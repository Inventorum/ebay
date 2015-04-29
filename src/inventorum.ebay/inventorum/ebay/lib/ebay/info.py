# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.lib.ebay import EbayTrading
from inventorum.ebay.lib.ebay.data.categories.features import EbayFeature
from inventorum.ebay.lib.ebay.data.user import EbayUser


class EbayInfo(EbayTrading):
    def get_user(self, user_id=None):
        """
        Get user data, if `user_id` is not specified, get currently authenticated one
        :param user_id: Id of user from ebay
        :return: Dict of user data

        :type user_id: None | str | unicode
        :rtype: EbayUser
        """
        data = {'DetailLevel': 'ReturnAll'}
        if user_id is not None:
            data['UserID'] = user_id
        response = self.execute('GetUser', data)
        return EbayUser.create_from_data(response['User'])

    def get_site_defaults(self):
        response = self.execute('GetCategoryFeatures', dict(
            AllFeaturesForCategory=True,
            ViewAllNodes=True,
            LevelLimit=7,
            DetailLevel='ReturnAll'
        ))
        return EbayFeature.create_from_data(response)