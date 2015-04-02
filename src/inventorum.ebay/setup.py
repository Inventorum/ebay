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
db_provision = inventorum.ebay.scripts.db:db_provision
manage = inventorum.util.paste:manage
"""

# alphabetically ordered
required_eggs = [
    'celery>=3.1.17',

    'Django>=1.7.7',
    'django-extensions>=1.5.2',
    'djangorestframework>=3.1.1',
    'django-pastedeploy-settings>=1.0rc4dev',

    'inventorum.util==9.2.6-dev',

    'plac>=0.9.1',
    'requests>=2.6.0',
    'waitress>=0.8.9',
    'django-mptt>=0.6.1',
    'ebaysdk>=2.1.0',
    'grequests>=0.2.0',
    'mock>=1.0.1',
    'vcrpy>=1.3.0',
    'python-keyczar>=0.715',
    'django-countries>=3.3'
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
            'factory_boy>=2.4',
            'mock>=1.0.1'
        ]
    ),
    # http://pythonhosted.org/distribute/setuptools.html#namespace-packages
    namespace_packages=['inventorum'],
    zip_safe=False,
    entry_points=entry_points,
    dependency_links=[
    ],
)
