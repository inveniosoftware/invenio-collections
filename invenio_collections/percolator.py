# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2011, 2012, 2013, 2014, 2015, 2016 CERN.
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

"""Percolator."""

from invenio_indexer.api import RecordIndexer
from invenio_query_parser.contrib.elasticsearch import IQ
from invenio_search import current_search, current_search_client


def new_collection_percolator(target):
    """Create new percolator associated with the new collection."""
    query = IQ(target.dbquery)
    for name in current_search.mappings.keys():
        if target.name and target.dbquery:
            current_search.client.index(
                index=name,
                doc_type='.percolator',
                id='collection-{}'.format(target.name),
                body={'query': query.to_dict()}
            )


def delete_collection_percolator(target):
    """Delete percolator associated with the new collection."""
    for name in current_search.mappings.keys():
        if target.name and target.dbquery:
            current_search.client.delete(
                index=name,
                doc_type='.percolator',
                id='collection-{}'.format(target.name),
                ignore=[404]
            )


def collection_inserted_percolator(mapper, connection, target):
    """Create percolator when collection is created."""
    if target.dbquery is not None:
        new_collection_percolator(target)


def collection_updated_percolator(mapper, connection, target):
    """Create percolator when collection is created."""
    delete_collection_percolator(target)
    if target.dbquery is not None:
        new_collection_percolator(target)


def collection_removed_percolator(mapper, connection, target):
    """Delete percolator when collection is deleted."""
    if target.dbquery is not None:
        delete_collection_percolator(target)


def _find_matching_collections_externally(collections, record):
    """Find matching collections with percolator engine.

    :param collections: set of collections where search
    :param record: record to match
    """
    index, doc_type = RecordIndexer().record_to_index(record)
    body = {"doc": record.dumps()}
    results = current_search_client.percolate(
        index=index,
        doc_type=doc_type,
        allow_no_indices=True,
        ignore_unavailable=True,
        body=body
    )
    prefix_len = len('collection-')
    for match in results['matches']:
        collection_name = match['_id']
        if collection_name.startswith('collection-'):
            name = collection_name[prefix_len:]
            if name in collections:
                yield collections[name]['ancestors']
    raise StopIteration
