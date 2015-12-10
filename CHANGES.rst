=======
CHANGES
=======

develop
=======

Feature
.......
- INV-6183 Fetch product attribute translations from the Core-API when publishing products to ebay.


2015-11-06 0.1.17
=================
Fix
...
- INV-5559 Whitelist shipping services with ``DimensionsRequired=True`` (e.g. DHL Paket)

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

