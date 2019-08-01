# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for organizing metadata into collections."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'SQLAlchemy-Continuum>=1.2.1',
    'check-manifest>=0.25',
    'coverage>=4.0',
    'dojson>=1.1.0',
    'isort>=4.2.2',
    'mock>=1.3.0',
    'pydocstyle>=1.0.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.1',
]

extras_require = {
    ':python_version=="2.7"': [
        'functools32>=3.2.3.post2',
    ],
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'mysql': [
        'invenio-db[mysql]>=1.0.0',
    ],
    'postgresql': [
        'invenio-db[postgresql]>=1.0.0',
    ],
    'sqlite': [
        'invenio-db>=1.0.0',
    ],
    'tests': tests_require,
    'search': [
        'celery>=3.1.19,<4.0',
        'invenio-search>=1.0.0',
        'invenio-indexer>=1.0.0',
    ]
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name[0] == ':' or name in ('mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.6.2',
    'Babel>=1.3',
]

install_requires = [
    'Flask-BabelEx>=0.9.2',
    'Flask-Breadcrumbs>=0.3.0',
    'Flask>=0.11.1',
    'asciitree>=0.3.1',
    'elasticsearch>=2.0.0,<3.0.0',
    'elasticsearch-dsl>=2.0.0,<3.0.0',
    'invenio-query-parser>=0.6.0',
    'invenio-records>=1.0.0',
    'pyPEG2>=2.15.1',
    'sqlalchemy_mptt>=0.2',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_collections', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-collections',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio collections',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-collections',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'dojson.contrib.marc21': [
            'collections = invenio_collections.contrib.dojson',
        ],
        'dojson.contrib.to_marc21': [
            '980 = invenio_collections.contrib.dojson',
        ],
        'flask.commands': [
            'collections = invenio_collections.cli:collections',
        ],
        'invenio_base.apps': [
            'invenio_collections = invenio_collections:InvenioCollections',
        ],
        'invenio_base.blueprints': [
            'invenio_collections = invenio_collections.views:blueprint',
        ],
        'invenio_db.alembic': [
            'invenio_collections = invenio_collections:alembic',
        ],
        'invenio_db.models': [
            'invenio_collections = invenio_collections.models',
        ],
        'invenio_i18n.translations': [
            'invenio_collections = invenio_collections',
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 3 - Alpha',
    ],
)
