.. vim: set filetype=rst :

===============
inventorum.ebay
===============

Prerequisities
--------------
Install some required packages

::

  apt-get install libxml2-dev libxslt1-dev python2.7-dev


Mac OS X:

::

  sudo port -v install erlang xmlto

Quickstart
----------

To bootstrap the project:

::

    python2.7 -sS bootstrap.py
    bin/buildout -vv

    bin/provisioning/provision_db src/inventorum.ebay/development.ini inventorum_ebay_develop -D
    bin/provisioning/provision_rabbitmq src/inventorum.ebay/development.ini

Running tests
-------------

To run all tests:

::

    bin/ebay/manage src/inventorum.ebay/test.ini test --noinput src/inventorum.ebay/inventorum/ebay/apps


If you want to skip tests that take really long (like parsing ebay categories etc) you can apply
environment variable ``SKIP_LONG_TESTS`` with value ``1``. (ONLY FOR DEVELOPMENT PURPOSES!)

Working with the database
-------------------------

To reset database:

::

  bin/db_provision src/inventorum.ebay/development.ini inventorum_ebay_develop -D

To apply migrations:

::

    bin/ebay/manage src/inventorum.ebay/development.ini migrate

To generate migrations:

::

    bin/ebay/manage src/inventorum.ebay/development.ini makemigrations <app_name>


Known issues
------------

`Deprecated? On Andis computer it works with Python 2.7.9`
`Nope, on Mikes and Julians it works only <= 2.7.8`

In case you are getting this error in test:

::

    TypeError: __init__() got an unexpected keyword argument 'server_hostname'

You need to downgrade python to 2.7.8

::

    sudo port activate python27 @2.7.8



Account we are using for testing
--------------------------------

::

  # Inventorum test account (slingshot)
  Email: tech+slingshot-test@inventorum.com
  Account id: 346
  User id: 425
  Pin: 1111
  Password: login


How to add images in console on slingshot
-----------------------------------------

::

  >>> parent = ProductModel.objects.get(id=666032)
  >>> first_child = parent.childrens.first()
  >>> last_child = parent.childrens.last()
  >>> first_hash_image = ImageHashModel.objects.get(id=2978)
  >>> second_hash_image = ImageHashModel.objects.get(id=2979)
  >>> first_child.images.add(first_hash_image)
  >>> last_child.images.add(second_hash_image)

