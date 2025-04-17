# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 CERN.
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for organizing metadata into collections."""

from invenio_collections.resources.config import CollectionsResourceConfig
from invenio_collections.resources.resource import CollectionsResource
from invenio_collections.services.config import CollectionServiceConfig
from invenio_collections.services.service import CollectionsService

from . import config


class InvenioCollections(object):
    """Invenio-Collections extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.service = None
        self.resource = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        self.init_resources(app)
        app.extensions["invenio-collections"] = self

    def init_config(self, app):
        """Initialize configuration."""
        # Use theme's base template if theme is installed
        if "BASE_TEMPLATE" in app.config:
            app.config.setdefault(
                "COLLECTIONS_BASE_TEMPLATE",
                app.config["BASE_TEMPLATE"],
            )
        for k in dir(config):
            if k.startswith("COLLECTIONS_"):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Init services."""
        self.service = CollectionsService(config=CollectionServiceConfig.build(app))

    def init_resources(self, app):
        """Init resources."""
        self.resource = CollectionsResource(
            service=self.service, config=CollectionsResourceConfig.build(app)
        )
