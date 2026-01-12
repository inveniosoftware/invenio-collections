# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collection resource config."""

from flask_resources import (
    HTTPJSONException,
    JSONSerializer,
    ResourceConfig,
    ResponseHandler,
    create_error_handler,
)
from invenio_rdm_records.resources.serializers import UIJSONSerializer
from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.base.config import ConfiguratorMixin
from marshmallow import fields as ma
from marshmallow.fields import Integer

from ..errors import (
    CollectionHasChildren,
    CollectionNotFound,
    CollectionTreeHasCollections,
    CollectionTreeNotFound,
    DuplicateSlugError,
)


class CollectionsResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Configuration for the Collection resource."""

    blueprint_name = "collections"

    routes = {
        "search-records": "/collections/<id>/records",
        "list": "/communities/<pid_value>/collections",
        "list-collection-trees": "/communities/<pid_value>/collection-trees",
        "tree-item": "/communities/<pid_value>/collection-trees/<tree_slug>",
        "list-tree-collections": "/communities/<pid_value>/collection-trees/<tree_slug>/collections",
        "list-tree-collections-test-records": "/communities/<pid_value>/collection-trees/<tree_slug>/collections-records-test",
        "collection-item": "/communities/<pid_value>/collection-trees/<tree_slug>/collections/<col_slug>",
        "collection-records": "/communities/<pid_value>/collection-trees/<tree_slug>/collections/<col_slug>/records",
    }

    request_view_args = {
        "id": Integer(),
        "pid_value": ma.Str(),
        "tree_slug": ma.Str(),
        "col_slug": ma.Str(),
    }

    request_extra_args = {
        "depth": ma.Int(),
        "cascade": ma.Bool(),
        "test_col_slug": ma.Str(),
    }

    request_search_args = SearchRequestArgsSchema
    error_handlers = {
        CollectionNotFound: create_error_handler(
            HTTPJSONException(code=404, description="Collection was not found.")
        ),
        CollectionTreeNotFound: create_error_handler(
            HTTPJSONException(code=404, description="Collection tree was not found.")
        ),
        CollectionTreeHasCollections: create_error_handler(
            HTTPJSONException(
                code=400,
                description="Cannot delete collection tree until all collections have been deleted.",
            )
        ),
        CollectionHasChildren: create_error_handler(
            HTTPJSONException(
                code=400,
                description="Cannot delete collection until all children have been deleted.",
            )
        ),
        DuplicateSlugError: create_error_handler(
            HTTPJSONException(
                code=409,
                description="A collection with this slug already exists in this context.",
            )
        ),
    }
    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            UIJSONSerializer(), headers=etag_headers
        ),
    }
