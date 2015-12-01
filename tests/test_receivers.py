# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
# -*- coding: utf-8 -*-
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Model test cases."""

from __future__ import unicode_literals

import os

from flask import Flask
from flask_cli import FlaskCLI
from invenio_db import InvenioDB, db
from invenio_records import InvenioRecords
from invenio_records.api import Record
from werkzeug.contrib.cache import SimpleCache

from invenio_collections import InvenioCollections
from invenio_collections.models import Collection


def test_build_cache_with_no_collections(request):
    """Test database backend."""
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv(
            'SQLALCHEMY_DATABASE_URI', 'sqlite://'),
        TESTING=True,
        SECRET_KEY='TEST',
    )
    FlaskCLI(app)
    InvenioDB(app)
    InvenioRecords(app)

    cache = SimpleCache()
    InvenioCollections(app, cache=cache)

    with app.app_context():
        db.create_all()

    def teardown():
        with app.app_context():
            db.drop_all()

    request.addfinalizer(teardown)

    with app.test_request_context():
        schema = {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'field': {'type': 'boolean'},
                'hello': {'type': 'array'},
            },
            'required': ['title'],
        }

        # A is creating `record0`
        record0 = Record.create({'title': 'Test0', '$schema': schema})
        assert record0['_collections'] == []

        # somewhere, B add new collection `mycoll`
        mycoll = Collection(name="mycoll", dbquery="title:Test0")
        db.session.add(mycoll)
        db.session.commit()

        # reload list of collections
        record0.commit()

        # now the collection 'mycoll' should appear in `record0` of A!
        assert record0['_collections'] == ['mycoll']
