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

from flask import current_app
from six import iteritems

from .models import Collection
from .proxies import current_collections
from .query import Query

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache


def _ancestors(collection):
    """Get the ancestors of the collection."""
    for index, c in enumerate(collection.path_to_root()):
        if index > 0 and c.dbquery is not None:
            raise StopIteration
        yield c.name
    raise StopIteration


@lru_cache(maxsize=1000)
def _build_query(dbquery):
    """Build ``Query`` object for given collection query."""
    return Query(dbquery)


def _build_cache():
    """Preprocess collection queries."""
    query = current_app.config['COLLECTIONS_DELETED_RECORDS']
    for collection in Collection.query.filter(
            Collection.dbquery.isnot(None)).all():
        yield collection.name, dict(
            query=query.format(dbquery=collection.dbquery),
            ancestors=set(_ancestors(collection)),
        )


def get_record_collections(record):
    """Return list of collections to which record belongs to.

    :record: Record instance
    :return: list of collection names
    """
    collections = current_collections.collections
    if collections is None:
        collections = current_collections.collections = dict(_build_cache())

    output = set()

    for name, data in iteritems(collections):
        if _build_query(data['query']).match(record):
            output.add(name)
            output |= data['ancestors']
    return list(output)


def update_collections(sender, *args, **kwargs):
    """Update the list of collections to which the record belongs."""
    sender['_collections'] = get_record_collections(sender)
