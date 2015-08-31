# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from inventorum.ebay.apps.products.models import EbayItemImageModel
from inventorum.ebay.tests.testcases import EbayAuthenticatedAPITestCase


class TestImagesUrls(EbayAuthenticatedAPITestCase):
    def test_hosts(self):
        """
        Proves that url for images is changed to have correct host (media) and http instead of https
        """
        url = 'https://app.intern.inventorum.net/some/image.png'

        image = EbayItemImageModel.objects.create(
            inv_image_id=1,
            url=url
        )

        self.assertEqual(image.ebay_object.url, 'http://app.inventorum.net/some/image.png')