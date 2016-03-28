# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Utilities."""

from __future__ import absolute_import, print_function

import codecs
import re

import six
from flask import current_app
from werkzeug.utils import import_string

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim='-'):
    """Generate an ASCII-only slug."""
    result = []
    for word in _punct_re.split((text or '').lower()):
        result.extend(codecs.encode(word, 'ascii', 'replace').split())
    return delim.join([str(r) for r in result])


def parser():
    """Return search query parser."""
    query_parser = current_app.config['COLLECTIONS_QUERY_PARSER']
    if isinstance(query_parser, six.string_types):
        query_parser = import_string(query_parser)
        return query_parser


def query_walkers():
    """Return query walker instances."""
    return [
        import_string(walker)() if isinstance(walker, six.string_types)
        else walker() for walker in current_app.config[
            'COLLECTIONS_QUERY_WALKERS']
    ]
