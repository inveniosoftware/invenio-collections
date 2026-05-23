# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT
"""Collection search app helpers for React-SearchKit."""

from functools import partial

from flask import current_app
from invenio_search_ui.searchconfig import search_app_config


def search_app_context():
    """Search app context."""
    return {
        "search_app_collection_config": partial(
            search_app_config,
            config_name="RDM_SEARCH",
            available_facets=current_app.config["RDM_FACETS"],
            sort_options=current_app.config["RDM_SORT_OPTIONS"],
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
            pagination_options=(10, 25, 50, 100),
        )
    }
