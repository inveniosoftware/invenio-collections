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

"""Record field function."""

from invenio_records.signals import (
    before_record_insert,
    before_record_update,
)
from six import iteritems

from .query import Query
from .models import Collection

COLLECTIONS_DELETED_RECORDS = '{dbquery} AND NOT collection:"DELETED"'


def _ancestors(collection):
    """Get the ancestors of the collection."""
    for index, c in enumerate(collection.path_to_root()):
        if index > 0 and c.dbquery is not None:
            raise StopIteration
        yield c
    raise StopIteration


def _queries():
    """Preprocess collection queries."""
    return dict(
        (collection.name, dict(
            query=Query(COLLECTIONS_DELETED_RECORDS.format(
                dbquery=collection.dbquery)
            ),
            ancestors=set(c.name for c in _ancestors(collection))
        ))
        for collection in Collection.query.filter(
            Collection.dbquery.isnot(None),
        ).all()
    )


def get_record_collections(record):
    """Return list of collections to which record belongs to.

    :record: Record instance
    :return: list of collection names
    """
    output = set()
    for name, data in iteritems(_queries()):
        if data['query'].match(record):
            output.add(name)
            output |= data['ancestors']
    return list(output)


@before_record_insert.connect
@before_record_update.connect
def update_collections(sender, *args, **kwargs):
    """Update the list of collections to which the record belongs."""
    sender['_collections'] = get_record_collections(sender)
