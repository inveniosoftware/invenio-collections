# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import pytest
from flask import Flask, url_for
from invenio_db import db

from invenio_collections import InvenioCollections, current_collections
from invenio_collections.models import Collection


def test_version():
    """Test version import."""
    from invenio_collections import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioCollections(app)
    assert 'invenio-collections' in app.extensions
    ext.unregister_signals()

    app = Flask('testapp')
    ext = InvenioCollections()
    assert 'invenio-collections' not in app.extensions
    ext.init_app(app)
    assert 'invenio-collections' in app.extensions
    with app.app_context():
        current_collections.unregister_signals()


def test_alembic(app):
    """Test alembic recipes."""
    ext = app.extensions['invenio-db']

    with app.app_context():
        if db.engine.name == 'sqlite':
            raise pytest.skip('Upgrades are not supported on SQLite.')

        assert not ext.alembic.compare_metadata()
        db.drop_all()
        ext.alembic.upgrade()

        assert not ext.alembic.compare_metadata()
        ext.alembic.stamp()
        ext.alembic.downgrade(target='96e796392533')
        ext.alembic.upgrade()

        assert not ext.alembic.compare_metadata()


def test_view(app):
    """Test view."""
    with app.app_context():
        current_collections.unregister_signals()
        view_url = url_for('invenio_collections.collection')
        view_test_url = url_for('invenio_collections.collection', name='Test')

    with app.test_client() as client:
        res = client.get(view_url)
        assert res.status_code == 404

    with app.app_context():
        with db.session.begin_nested():
            collection = Collection(name='Test')
            db.session.add(collection)
        db.session.commit()
        assert 1 == collection.id
        assert 'Collection <id: 1, name: Test, dbquery: None>' == repr(
            collection)

    with app.test_client() as client:
        res = client.get(view_url)
        assert res.status_code == 200

        res = client.get(view_test_url)
        assert res.status_code == 200

    with app.app_context():
        current_collections.unregister_signals()
