#!/usr/bin/env python
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
VERSION = open(os.path.join(here, 'VERSION')).read().strip()

entry_points = """\
[paste.app_factory]
ebay_main = inventorum.util.paste:make_wsgi_application

[console_scripts]
celery = inventorum.ebay.scripts.celery:run
provisioning/provision_db = inventorum.ebay.scripts.provisioning:provision_db
provisioning/provision_rabbitmq = inventorum.ebay.scripts.provisioning:provision_rabbitmq
manage = inventorum.util.paste:manage
"""

# alphabetically ordered(!)
required_eggs = [
    'celery>=3.1.17',
    'ebaysdk>=2.1.1-dev4',
    'flower>=0.8.1',
    'grequests>=0.3.1',

    'graypy>=0.2.11',

    'Django>=1.7.7',
    'django-countries>=3.3',
    'django-extensions>=1.5.2',
    'djangorestframework>=3.1.2',
    'django-mptt>=0.6.1',
    'django-pastedeploy-settings>=1.0rc4dev',
    'django-rest-swagger>=0.2.9',

    'inventorum.util==10.0.0',

    'mock>=1.0.1',
    'plac>=0.9.1',
    'python-keyczar>=0.715',
    'raven>=5.2.0',
    'requests>=2.6.0',
    'vcrpy>=1.3.0',
    'waitress>=0.8.9',
]

setup(
    name='inventorum.ebay',
    version=VERSION,
    description="",
    author="Inventorum GmbH",
    author_email='tech@inventorum.com',
    url='',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    package_data={'inventorum': [], 'static': [],},
    scripts=[],
    install_requires=required_eggs,
    extras_require=dict(
        # alphabetically ordered
        test=required_eggs + [
            'coverage>=3.7',
            'django-nose>=1.3',
            'factory_boy>=2.5',
            'mock>=1.0.1'
        ]
    ),
    # http://pythonhosted.org/distribute/setuptools.html#namespace-packages
    namespace_packages=['inventorum'],
    zip_safe=False,
    entry_points=entry_points,
    dependency_links=[
        # use the last commit-id in our branch that we rely on
        'https://github.com/bimusiek/ebaysdk-python/archive/master.zip'
        '#egg=ebaysdk-2.1.1-dev4',
        'https://github.com/rtdean/grequests/archive/0.3.0.zip'
        '#egg=grequests-0.3.1',
        'https://github.com/bimusiek/django-rest-framework/archive/master.zip'
        '#egg=djangorestframework-3.1.2',
    ],
)
# https://github.com/bimusiek/ebaysdk-python/archive/c8365ee3cb2db29fdaae6d96fbdeff482a65ac29.zip
