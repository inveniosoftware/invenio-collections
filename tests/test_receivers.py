# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

from invenio_db import db
from invenio_records.api import Record
from werkzeug.contrib.cache import SimpleCache

from invenio_collections import current_collections
from invenio_collections.models import Collection


def test_build_cache_with_no_collections(app):
    """Test database backend."""
    with app.test_request_context():
        cache = SimpleCache()
        current_collections.cache = cache

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
        with db.session.begin_nested():
            record0 = Record.create({'title': 'Test0', '$schema': schema})

        assert record0['_collections'] == []

        # somewhere, B add new collection `mycoll`
        with db.session.begin_nested():
            mycoll = Collection(name="mycoll", dbquery="title:Test0")
            db.session.add(mycoll)

        # reload list of collections
        record0.commit()

        # now the collection 'mycoll' should appear in `record0` of A!
        assert record0['_collections'] == ['mycoll']
