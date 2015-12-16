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

"""Invenio Collections configuration."""

from __future__ import unicode_literals

import pkg_resources

COLLECTIONS_DELETED_RECORDS = '{dbquery} AND NOT collection:"DELETED"'
"""Enhance collection query to exclude deleted records."""

COLLECTIONS_QUERY_PARSER = 'invenio_query_parser.parser:Main'

COLLECTIONS_QUERY_WALKERS = [
    'invenio_query_parser.walkers.pypeg_to_ast:PypegConverter',
]

COLLECTIONS_CACHE_KEY = 'DynamicCollections::'
"""Key prefix added before all keys in cache server."""

COLLECTIONS_REGISTER_RECORD_SIGNALS = True
"""Catch record insert/update signals and update the `_collections` field."""

try:
    pkg_resources.get_distribution('invenio_search')

    from invenio_search.config import \
        SEARCH_QUERY_PARSER as COLLECTIONS_QUERY_PARSER, \
        SEARCH_QUERY_WALKERS as COLLECTIONS_QUERY_WALKERS
except pkg_resources.DistributionNotFound:  # pragma: no cover
    pass

COLLECTIONS_USE_PERCOLATOR = False
"""Define which percolator you want to use.

Default value is `False` to use the internal percolator.
You can also set True to use elasticsearch to provide percolator resolver."""
