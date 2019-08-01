# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
