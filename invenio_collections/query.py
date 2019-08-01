# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Query parser."""

import pypeg2
from invenio_query_parser.walkers.match_unit import MatchUnit

from .utils import parser, query_walkers


class Query(object):
    """Query object."""

    def __init__(self, query):
        """Init."""
        self._query = query

    @property
    def query(self):
        """Parse query string using given grammar.

        :returns: AST that represents the query in the given grammar.
        """
        tree = pypeg2.parse(self._query, parser(), whitespace="")
        for walker in query_walkers():
            tree = tree.accept(walker)
        return tree

    def match(self, record):
        """Check if the record match the query.

        :param record: Record to test.
        :returns: True if record match the query.
        """
        return self.query.accept(MatchUnit(record))
