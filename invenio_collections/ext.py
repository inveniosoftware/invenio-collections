# SPDX-FileCopyrightText: 2015 CERN.
# SPDX-FileCopyrightText: 2025 Ubiquity Press.
# SPDX-License-Identifier: MIT

"""Invenio module for organizing metadata into collections."""

from . import config


class InvenioCollections(object):
    """Invenio-Collections extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
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
