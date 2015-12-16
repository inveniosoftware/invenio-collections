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

"""Record field function."""

from flask import current_app
from six import iteritems

from .models import Collection
from .proxies import current_collections
from .query import Query

try:
    from functools import lru_cache
except ImportError:  # pragma: no cover
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
    raise StopIteration


def _find_matching_collections_internally(collections, record):
    """Find matching collections with internal engine.

    :param collections: set of collections where search
    :param record: record to match
    """
    for name, data in iteritems(collections):
        if _build_query(data['query']).match(record):
            yield data['ancestors']
    raise StopIteration


def get_record_collections(record, matcher):
    """Return list of collections to which record belongs to.

    :record: Record instance
    :return: list of collection names
    """
    collections = current_collections.collections
    if collections is None:
        # build collections cache
        collections = current_collections.collections = dict(_build_cache())

    output = set()

    for collections in matcher(collections, record):
        output |= collections

    return list(output)


class CollectionUpdater(object):
    """Return the right update collections function."""

    def __init__(self, app=None):
        """Init."""
        app = app or current_app
        if not app.config['COLLECTIONS_USE_PERCOLATOR']:
            self.matcher = _find_matching_collections_internally
        else:
            from .percolator import _find_matching_collections_externally
            self.matcher = _find_matching_collections_externally

    def __call__(self, record, **kwargs):
        """Update collections list."""
        record['_collections'] = get_record_collections(record=record,
                                                        matcher=self.matcher)
