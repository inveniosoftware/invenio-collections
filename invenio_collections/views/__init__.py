# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""View functions for the collections."""


def create_bp(app):
    """Create blueprint."""
    ext = app.extensions["invenio-collections"]
    return ext.resource.as_blueprint()
