#!/usr/bin/env python
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
VERSION = open(os.path.join(here, 'VERSION')).read().strip()

# alphabetically ordered(!)
required_eggs = [
    'psycopg2==2.5.4',
    'Django==1.7.7',
    'uwsgi==2.0',
    'BeautifulSoup==3.2.1',
    'Jinja2==2.7.3',
    'MarkupSafe==0.23',
    'Paste==1.7.5.1',
    'PasteScript==1.7.5',
    'Pygments==2.0.2',
    'WebOb==1.4',
    'check-manifest==0.23',
    'cssutils==1.0',
    'devpi-client==2.1.0',
    'devpi-common==2.0.5',
    'django-extensions==1.5.2',
    'django-model-utils==2.2',
    'djangorestframework==3.1.3',
    'ipdb==0.8',
    'meld3==1.0.0',
    'nose==1.3.4',
    'PasteDeploy==1.5.0',
    'pkginfo==1.2.1',
    'py==1.4.26',
    'pynliner==0.5.2',
    'repoze.lru==0.6',
    'requests==2.6.0',
    'six==1.9.0',
    'tox==1.9.1',
    'translationstring==1.3',
    'venusian==1.0',
    'virtualenv==12.0.7',
    'zope.deprecation==4.1.2',
    'zope.interface==4.1.2',
    'waitress==0.8.9',
    'django-mptt==0.7.1',
    'PyYAML==3.11',
    'lxml==3.4.2',
    'celery==3.1.17',
    'amqp==1.4.6',
    'anyjson==0.3.3',
    'billiard==3.3.0.19',
    'kombu==3.0.24',
    'plac==0.9.1',
    'gevent==1.0.1',
    'greenlet==0.4.5',
    'vcrpy==1.3.0',
    'contextlib2==0.4.0',
    'wrapt==1.10.4',
    'django-countries==3.3',
    'pycrypto==2.6.1',
    'python-keyczar==0.715',
    'pyasn1==0.1.7',
    'django-rest-swagger==0.2.9',
    'raven==5.2.0',
    'Babel==1.3',
    'flower==0.8.1',
    'tornado==4.1',
    'backports.ssl-match-hostname==3.4.0.2',
    'certifi==14.5.14',
    'futures==2.2.0',
    'graypy==0.2.11',
    # version defined by dependency links
    'inventorum.util',
    'ebaysdk',
    'grequests'
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
            'coverage==3.7',
            'django-nose==1.3',
            'factory_boy==2.5',
            'mock==1.0.1'
        ]
    ),
    # http://pythonhosted.org/distribute/setuptools.html#namespace-packages
    namespace_packages=['inventorum'],
    zip_safe=False,
    dependency_links=[
        # use the last commit-id in our branch that we rely on
        'https://github.com/bimusiek/ebaysdk-python/archive/master.zip'
        '#egg=ebaysdk-2.1.1-dev4',
        'https://github.com/rtdean/grequests/archive/0.3.0.zip'
        '#egg=grequests-0.3.1',
        'git+ssh://git@git.inventorum.net/inventorum/inventorum.util.git'
        '#egg=inventorum.util-10.6.4-dev'
    ],
)
