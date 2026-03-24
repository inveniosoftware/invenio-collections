# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Collections schemas."""

import re

from invenio_i18n import lazy_gettext as _
from luqum.exceptions import ParseError
from luqum.parser import parser as luqum_parser
from marshmallow import Schema, ValidationError, fields, validate
from marshmallow_utils.fields import SanitizedUnicode


def _not_blank(**kwargs):
    """Returns a non-blank validation rule."""
    max_ = kwargs.get("max", "")
    return validate.Length(
        error=_(
            "Field cannot be blank or longer than {max_} characters.".format(max_=max_)
        ),
        min=1,
        **kwargs,
    )


class CollectionTreeSchema(Schema):
    """Collection tree schema."""

    slug = SanitizedUnicode(
        required=True,
        validate=[
            _not_blank(max=255),
            validate.Regexp(
                r"^[-\w]+$",
                flags=re.ASCII,
                error=_(
                    "The identifier should contain only letters, numbers, or dashes."
                ),
            ),
        ],
    )
    title = SanitizedUnicode(
        validate=[_not_blank(max=255)],
    )
    order = fields.Int()
    id = fields.Int(dump_only=True)
    community_id = fields.Str(dump_only=True)


def validate_search_query(query):
    """Validate a search query using luqum parser."""
    try:
        luqum_parser.parse(query)
    except ParseError as e:
        raise ValidationError(str(e)) from e


class CollectionSchema(Schema):
    """Collection schema."""

    slug = SanitizedUnicode(
        validate=[
            _not_blank(max=255),
            validate.Regexp(
                r"^[-\w]+$",
                flags=re.ASCII,
                error=_(
                    "The identifier should contain only letters, numbers, or dashes."
                ),
            ),
        ],
    )
    title = SanitizedUnicode(
        validate=[_not_blank(max=255)],
    )

    depth = fields.Int(dump_only=True)
    order = fields.Int()
    id = fields.Int(dump_only=True)
    num_records = fields.Int()
    search_query = fields.Str(validate=[validate_search_query])
