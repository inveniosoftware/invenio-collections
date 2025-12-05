# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Northwestern University.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Blueprint of Mock Module."""

from flask import Blueprint


def create_ui_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "invenio_app_rdm_communities",
        __name__,
    )

    @blueprint.route(
        "/communities/<pid_value>/collections/<tree_slug>/<collection_slug>"
    )
    def community_collection(id):
        return "community collection"

    return blueprint
