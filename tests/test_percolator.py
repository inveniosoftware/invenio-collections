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

"""Percolator test cases."""

from invenio_db import db
from invenio_indexer import InvenioIndexer
from invenio_records.api import Record
from invenio_search import InvenioSearch, current_search

from invenio_collections import current_collections
from invenio_collections.models import Collection


def test_percolator(app, request):
    """Test percolator."""
    def teardown():
        with app.app_context():
            list(current_search.delete())

    request.addfinalizer(teardown)

    with app.test_request_context():
        app.config.update(
            COLLECTIONS_USE_PERCOLATOR=True,
            SEARCH_ELASTIC_KEYWORD_MAPPING={None: ['_all']},
        )

        search = InvenioSearch(app)
        search.register_mappings('records', 'data')

        InvenioIndexer(app)

        current_collections.unregister_signals()
        current_collections.register_signals()

        list(current_search.create())

        _try_populate_collections()


def test_without_percolator(app, request):
    """Test percolator."""
    with app.test_request_context():
        app.config.update(
            COLLECTIONS_USE_PERCOLATOR=False,
        )

        current_collections.unregister_signals()
        current_collections.register_signals()

        _try_populate_collections()


def _try_populate_collections():
    """Try to update collections."""
    schema = {
        'type': 'object',
        'properties': {
                'title': {'type': 'string'},
                'field': {'type': 'boolean'},
            },
        'required': ['title'],
    }

    #                               a
    #                             (None)
    #            +------------------+--------------------+
    #            |                                       |
    #            b                                       e
    #         (None)                        (title:Test2 OR title:Test3)
    #     +------+-----+                    +------------+------------+
    #     |            |                    |            |            |
    #     c            d                    f            g            h
    # (title:Test0) (title:Test1)     (title:Test2)    (None)       (None)
    #                                                    |            |
    #                                                    i            j
    #                                             (title:Test3) (title:Test4))

    a = Collection(name="a")
    b = Collection(name="b", parent=a)
    e = Collection(
        name="e", dbquery="title:Test2 OR title:Test3", parent=a)
    c = Collection(name="c", dbquery="title:Test0", parent=b)
    d = Collection(name="d", dbquery="title:Test1", parent=b)
    f = Collection(name="f", dbquery="title:Test2", parent=e)
    g = Collection(name="g", parent=e)
    h = Collection(name="h", parent=e)
    i = Collection(name="i", dbquery="title:Test3", parent=g)
    j = Collection(name="j", dbquery="title:Test4", parent=h)

    with db.session.begin_nested():
        for coll in [a, b, c, d, e, f, g, h, i, j]:
            db.session.add(coll)

    db.session.commit()

    # start tests

    record0 = Record.create({'title': 'Test0', '$schema': schema})

    assert 'a' in record0['_collections']
    assert 'c' in record0['_collections']
    assert 'b' in record0['_collections']
    assert len(record0['_collections']) == 3

    record = Record.create({'title': 'TestNotFound', '$schema': schema})

    assert record['_collections'] == []

    record = Record.create({'title': 'Test1', '$schema': schema})

    assert 'a' in record['_collections']
    assert 'b' in record['_collections']
    assert 'd' in record['_collections']
    assert len(record['_collections']) == 3

    record = Record.create({'title': 'Test2', '$schema': schema})

    assert 'a' in record['_collections']
    assert 'e' in record['_collections']
    assert 'f' in record['_collections']
    assert len(record['_collections']) == 3

    record3 = Record.create({'title': 'Test3', '$schema': schema})

    assert 'a' in record3['_collections']
    assert 'e' in record3['_collections']
    assert 'g' in record3['_collections']
    assert 'i' in record3['_collections']
    assert len(record3['_collections']) == 4

    record4 = Record.create({'title': 'Test4', '$schema': schema})

    assert 'h' in record4['_collections']
    assert 'j' in record4['_collections']
    assert len(record4['_collections']) == 2

    # test delete
    db.session.delete(j)
    db.session.commit()
    record4.commit()

    assert 'h' not in record4['_collections']
    assert 'j' not in record4['_collections']
    assert len(record4['_collections']) == 0

    # test update dbquery
    i.dbquery = None
    db.session.add(i)
    db.session.commit()
    record3.commit()

    assert 'a' in record3['_collections']
    assert 'e' in record3['_collections']
    assert len(record3['_collections']) == 2

    # test update dbquery
    i.dbquery = 'title:Test3'
    db.session.add(i)
    db.session.commit()
    record3.commit()

    assert 'a' in record3['_collections']
    assert 'e' in record3['_collections']
    assert 'g' in record3['_collections']
    assert 'i' in record3['_collections']
    assert len(record3['_collections']) == 4

    # test update name
    a.name = "new-a"
    db.session.add(a)
    db.session.commit()
    record3.commit()

    assert 'g' in record3['_collections']
    assert 'i' in record3['_collections']
    assert 'new-a' in record3['_collections']
    assert 'e' in record3['_collections']
    assert len(record3['_collections']) == 4

    # test update name
    c.name = "new-c"
    db.session.add(c)
    db.session.commit()
    record0.commit()

    assert 'new-a' in record0['_collections']
    assert 'new-c' in record0['_collections']
    assert 'b' in record0['_collections']
    assert len(record0['_collections']) == 3
