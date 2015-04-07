.. vim: set filetype=rst :

===============
inventorum.ebay
===============

Prerequisities
--------------
Install some required packages

::

  apt-get install libxml2-dev libxslt1-dev python2.7-dev

Quickstart
----------

To bootstrap the project:

::

    python2.7 -sS bootstrap.py
    bin/buildout -vv
    bin/db_provision src/inventorum.ebay/development.ini inventorum_ebay_develop -D

Running tests
-------------

To run all tests:

::

    bin/ebay/manage src/inventorum.ebay/test.ini test --noinput src/inventorum.ebay/inventorum/ebay/apps


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

In case you are getting this error in test:

::

    TypeError: __init__() got an unexpected keyword argument 'server_hostname'

You need to downgrade python to 2.7.6

::

    sudo port activate python27 @2.7.6


