# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask, url_for
from flask_babelex import Babel
from invenio_db import db

from invenio_collections import InvenioCollections
from invenio_collections.models import Collection
from invenio_collections.views import blueprint


def test_version():
    """Test version import."""
    from invenio_collections import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioCollections(app)
    assert 'invenio-collections' in app.extensions

    app = Flask('testapp')
    ext = InvenioCollections()
    assert 'invenio-collections' not in app.extensions
    ext.init_app(app)
    assert 'invenio-collections' in app.extensions


def test_view(app):
    """Test view."""
    Babel(app)
    InvenioCollections(app)
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.register_blueprint(blueprint)

    with app.app_context():
        index_url = url_for('invenio_collections.index')
        view_url = url_for('invenio_collections.collection')
        view_test_url = url_for('invenio_collections.collection', name='Test')

    with app.test_client() as client:
        res = client.get(index_url)
        assert res.status_code == 404

    with app.app_context():
        collection = Collection(name='Test')
        db.session.add(collection)
        db.session.commit()

        assert 1 == collection.id
        assert 'Collection <id: 1, name: Test, dbquery: None>' == repr(
            collection)

    with app.test_client() as client:
        res = client.get(index_url)
        assert res.status_code == 200

        res = client.get(view_url)
        assert res.status_code == 302

        res = client.get(view_test_url)
        assert res.status_code == 200
