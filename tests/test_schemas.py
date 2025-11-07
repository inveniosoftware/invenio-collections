# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#
"""Test suite for the collections schemas."""

import pytest
from marshmallow import ValidationError

from invenio_collections.services.schema import CollectionSchema


def test_collection_schema_validation():
    """Test search query validation."""
    valid_input = {
        "slug": "col",
        "title": "Test collection",
        "order": 0,
        "search_query": "*:*",
    }

    schema = CollectionSchema()
    collection = schema.load(valid_input)
    assert valid_input == collection == schema.dump(collection)


def test_collection_schema_fail():
    """Test schema validation errors."""
    input = {
        "slug": "col",
        "title": "Test collection",
        "order": 0,
        "search_query": "*:*",
    }
    schema = CollectionSchema()
    with pytest.raises(ValidationError) as exc_info:
        input["search_query"] = "custom_fields.journal:journal.volume:'2025'"
        schema.load(input)
    assert exc_info.value.args[0] == {
        "search_query": ["Illegal character ''2025'' at position 37"]
    }

    # Set back query
    input["search_query"] = "*:*"

    with pytest.raises(ValidationError) as exc_info:
        input["slug"] = "not valid"
        schema.load(input)
    assert exc_info.value.args[0] == {
        "slug": ["The identifier should contain only letters, numbers, or dashes."]
    }
