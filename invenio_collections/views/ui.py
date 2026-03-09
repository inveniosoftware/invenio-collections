# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2026 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI blueprint for invenio-collections (registers template folder only)."""

from flask import Blueprint


def create_ui_blueprint(app):
    """Create UI blueprint to register template folder with Flask."""
    return Blueprint(
        "invenio_collections_ui",
        __name__,
        template_folder="../templates",
    )
