# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Model test cases."""

from __future__ import unicode_literals

from flask import current_app
from invenio_db import db
from invenio_records.api import Record
from mock import patch
from werkzeug.contrib.cache import SimpleCache

from invenio_collections import InvenioCollections, current_collections
from invenio_collections.models import Collection

_global_simple_cache = SimpleCache()
"""Internal importable cache."""


def test_build_cache_with_no_collections(app):
    """Test database backend."""
    with app.test_request_context():
        cache = SimpleCache()
        current_collections.cache = cache

        schema = {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'field': {'type': 'boolean'},
                'hello': {'type': 'array'},
            },
            'required': ['title'],
        }
        # A is creating `record0`
        with db.session.begin_nested():
            record0 = Record.create({'title': 'Test0', '$schema': schema})

        assert record0['_collections'] == []

        # somewhere, B add new collection `mycoll`
        with db.session.begin_nested():
            mycoll = Collection(name="mycoll", dbquery="title:Test0")
            db.session.add(mycoll)

        # reload list of collections
        record0.commit()

        # now the collection 'mycoll' should appear in `record0` of A!
        assert record0['_collections'] == ['mycoll']


def test_importable_config_variable(app):
    """Test that cache can be imported from a config variable."""
    app.config['COLLECTIONS_CACHE'] = 'test_receivers._global_simple_cache'
    ext = InvenioCollections(app)
    assert ext.cache is _global_simple_cache


def test_instance_in_config_variable(app):
    """Test that cache instance can be directly used from a config variable."""
    cache = SimpleCache()
    app.config['COLLECTIONS_CACHE'] = cache
    ext = InvenioCollections(app)
    assert ext.cache is cache


def test_cache_cannot_be_overridden_if_it_was_set(app):
    """Test cache preference from a constructor over configuration."""
    first_cache = SimpleCache()
    second_cache = SimpleCache()
    app.config['COLLECTIONS_CACHE'] = second_cache
    ext = InvenioCollections(app, cache=first_cache)
    assert ext.cache is first_cache
