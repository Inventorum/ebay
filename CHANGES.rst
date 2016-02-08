=======
CHANGES
=======

develop
=======
2016-02-05 0.2.0
================
Feature
.......
- INV-6302 Add "taxes included" (inkl. MwSt) in all products.

Fix
...
- INV-6380 Fix validation amount of attributes in products with variations.
- INV-6204 Make the ebay orders sync more robust
- INV-6377 Ebay product can use now item specifics with special characters (like umlauts)
- INV-6234 Ebay product now can contain special characters like "&"."

2016-02-04 0.1.20-1
===================
Fix
...
- ``allow_null`` for meta images
- INV-6377 Ebay product can use now item specifics with special characters (like umlauts)

2015-12-15 0.1.20
=================
Fix
...
- INV-6218 Handle "Invalid Request" or any other invalid email address as the buyer's email address when publishing to the Core-API.
- INV-6226 When C&C fails, log it and ignore it.

2015-12-15 0.1.19
=================
- Changed gevent to 1.0.2 (grequests have no constraints on it) so it works with new Python2.7

2015-12-11 0.1.18
=================
Feature
.......
- INV-6061 Add support for combined eBay orders.
- INV-6183 Fetch product attribute translations from the Core-API when publishing products to ebay.
- INV-5839 Transform new lines to `<br>` and do not escape HTML tags in product descriptions.


2015-11-06 0.1.17
=================
Fix
...
- INV-5559 Whitelist shipping services with ``DimensionsRequired = True`` (e.g. DHL Paket)

2015-11-04 0.1.16
=================
Code
....
- Configure sentry to use ``log01.inventorum.net``

2015-09-23 0.1.15
=================
Fix
...
- Do not require shipping services with click & collect

2015-09-22 0.1.14
=================
Feature
.......
- Enable Out-of-Stock feature for authenticated users

Code
....
- Add script to active Out-of-Stock feature for existing, ebay-authenticated accounts

Fix
...
- Fix core products sync by handling double deletion attempts gracefully

2015-09-18 0.1.13
=================
Feature
.......
- INV-5515 Allow accounts to configure return policies
- INV-5496: Use "Does not apply" by default if core product has no EAN

Code
....
- Refactor all publishing tests + re-record all related cassettes

2015-09-15 0.1.12
=================
Feature
.......
- INV-5164 Pull published items from ebay.com with SKUs only


2015-08-31 0.1.11
=================
- INV-5361 Fixed not visible images in Ebay (wrong hostname)

2015-08-23 0.1.10
=================
- Allow ``None`` for ``gross_price`` in core product meta serializer

2015-08-03 0.1.9
================
- INV-4966 Send EAN if needed and validate EAN availability for particular categories
  due to new ebay GTIN mandate

2015-06-25 0.1.8
================
- Use `product_inv_id` for published product lookup in core products sync

2015-06-19 0.1.7
================
- Change inv_id in serializers to string format
- Adapt core image serializer to the new image format
- INV-4695 Use core inv_id in ebay service
- INV-4631/INV-4457 Avoid double publishing by using database locks in the resource

2015-06-16 0.1.6
================
- add ``rc`` environment for release candidate environment
- add db configs for ``aero.inventorum.net``
- INV-4689 Do not send optional location attributes as "None"
- create ``production.conf`` and ``staging.conf`` depending on buildouts
  ``${config:environment}``, which is properly set in packager

2015-06-09 0.1.5
================
- Updated ebay urls to accept new host

2015-06-09 0.1.4
================
- Fix "Decimal is not JSON serializable" error

2015-06-09 0.1.3
================
Fix
...
- Add missing migration for returns

2015-06-05 0.1.2
================

2015-05-20 0.1.1
================
- add production config

2015-05-20 0.1.0
================
- start and autostart ``com.inventorum.ebay_worker`` on install
- INV-4111 Added endpoint for ebay sanity check (/inventory/check/)
- Added Sentry error logger
- INV-4067 Created cronjob for pulling categories data
- INV-4068 Added authorization endpoints and save all available data about user to database
- And so it begins

