# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections schema."""

from flask_babel import lazy_gettext as _
from luqum.exceptions import ParseError
from luqum.parser import parser as luqum_parser
from marshmallow import Schema, ValidationError, fields, validate
from marshmallow_utils.fields import SanitizedUnicode


def validate_search_query(query):
    """Validate a search query using luqum parser."""
    try:
        luqum_parser.parse(query)
    except ParseError as e:
        raise ValidationError(str(e)) from e


class SlugField(SanitizedUnicode):
    """Reusable slug field with validation."""

    def __init__(self, **kwargs):
        """Initialize slug field with standard validation."""
        super().__init__(
            required=True,
            validate=[
                validate.Length(min=1, max=255),
                validate.Regexp(
                    r"^[\w-]+$",
                    error=_("Slug: letters, numbers, underscores, or hyphens only."),
                ),
            ],
            **kwargs,
        )


class CollectionTreeSchema(Schema):
    """Collection tree schema."""

    slug = SlugField()
    title = SanitizedUnicode(required=True, validate=validate.Length(min=1, max=255))
    order = fields.Int(
        validate=validate.Range(min=0, error=_("Order must be non-negative."))
    )
    id = fields.Int(dump_only=True)
    community_id = fields.Str(dump_only=True)


class CollectionSchema(Schema):
    """Collection schema."""

    slug = SlugField()
    title = SanitizedUnicode(required=True, validate=validate.Length(min=1, max=255))
    depth = fields.Int(dump_only=True)
    order = fields.Int(
        validate=validate.Range(min=0, error=_("Order must be non-negative."))
    )
    id = fields.Int(dump_only=True)
    num_records = fields.Int(dump_only=True)
    search_query = fields.Str(
        required=True,
        validate=[validate_search_query],
    )


class ReorderItemSchema(Schema):
    """Schema for a single reorder item."""

    slug = fields.Str(required=True)
    order = fields.Int(
        required=True,
        validate=validate.Range(min=0, error=_("Order must be non-negative.")),
    )


class BatchReorderSchema(Schema):
    """Schema for batch reordering request."""

    order = fields.List(
        fields.Nested(ReorderItemSchema),
        required=True,
        validate=validate.Length(min=1, error=_("At least one item required.")),
    )
