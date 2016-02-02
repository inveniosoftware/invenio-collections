# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

from flask import Flask, url_for
from flask.ext.admin import Admin
from invenio_admin import InvenioAdmin
from invenio_db import db

from invenio_collections import InvenioCollections
from invenio_collections.admin import CollectionView, collection_adminview


def test_admin(app):
    """Test flask-admin interace."""
    InvenioCollections(app)

    assert isinstance(collection_adminview, dict)

    assert 'model' in collection_adminview
    assert 'modelview' in collection_adminview

    admin = Admin(app, name='Test')

    user_model = collection_adminview.pop('model')
    user_view = collection_adminview.pop('modelview')
    admin.add_view(user_view(user_model, db.session,
                             **collection_adminview))

    with app.test_request_context():
        request_url = url_for('collection.index_view')

    with app.app_context():
        with app.test_client() as client:
            res = client.get(
                request_url,
                follow_redirects=True
            )
            assert res.status_code == 200
            assert b'left' in (res.get_data())
            assert b'query' in (res.get_data())
