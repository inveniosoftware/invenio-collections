# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""DoJSON collection related rules."""

from __future__ import absolute_import

from dojson import utils
from dojson.contrib.marc21 import marc21
from dojson.contrib.to_marc21 import to_marc21


@marc21.over('collections', '^980..')
@utils.for_each_value
@utils.filter_values
def collections(record, key, value):
    """Parse custom MARC tag 980."""
    return {
        'primary': value.get('a'),
        'secondary': value.get('b'),
        'deleted': value.get('c'),
    }


@to_marc21.over('980', '^collections$')
@utils.reverse_for_each_value
@utils.filter_values
def reverse_collections(self, key, value):
    """Reverse colections field to custom MARC tag 980."""
    return {
        'a': value.get('primary'),
        'b': value.get('secondary'),
        'c': value.get('deleted'),
    }
