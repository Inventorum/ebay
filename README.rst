.. vim: set filetype=rst :

===============
inventorum.ebay
===============

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

To apply migrations:

::

    bin/ebay/manage src/inventorum.ebay/development.ini migrate

To generate migrations:

::

    bin/ebay/manage src/inventorum.ebay/development.ini makemigrations <app_name>
