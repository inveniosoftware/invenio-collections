# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Query enhancer for collections."""

from invenio_query_parser.ast import AndOp, DoubleQuotedValue, Keyword, \
    KeywordOp


def collection_formatter(value):
    """Format collection filter."""
    return KeywordOp(Keyword("_collections"), DoubleQuotedValue(value))


def create_collection_query(collection,
                            formatter=collection_formatter):
    """Create the new AST nodes that should be added to the search query.

    :param collection: name of the current collection
    :param formatter: function used to generate collection AST
    """
    return formatter(collection)


def apply(query, collection=None):
    """Enhance the query restricting not permitted collections.

    Get the permitted restricted collection for the current user from the
    user_info object and all the restriced collections from the
    restricted_collection_cache.
    """
    if not collection:
        return query
    result_tree = create_collection_query(collection)
    return AndOp(query, result_tree)
