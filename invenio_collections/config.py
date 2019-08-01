# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Collections configuration."""

from __future__ import unicode_literals

COLLECTIONS_DELETED_RECORDS = '{dbquery} AND NOT collection:"DELETED"'
"""Enhance collection query to exclude deleted records."""

COLLECTIONS_QUERY_PARSER = 'invenio_query_parser.parser:Main'
"""User search query lexical parser."""

COLLECTIONS_QUERY_WALKERS = [
    'invenio_query_parser.walkers.pypeg_to_ast:PypegConverter',
]
"""Modules to create the query AST."""

COLLECTIONS_CACHE = None
"""A cache instance or an importable string pointing to the cache instance."""

COLLECTIONS_CACHE_KEY = 'DynamicCollections::'
"""Key prefix added before all keys in cache server."""

COLLECTIONS_REGISTER_RECORD_SIGNALS = True
"""Catch record insert/update signals and update the `_collections` field."""

COLLECTIONS_USE_PERCOLATOR = False
"""Define which percolator you want to use.

Default value is `False` to use the internal percolator.
You can also set True to use elasticsearch to provide percolator resolver."""

COLLECTIONS_DEFAULT_TEMPLATE = 'invenio_collections/index.html'
"""Template to be used as default for collection landing pages."""
