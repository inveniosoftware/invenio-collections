# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 CERN.
# Copyright (C) 2025 Ubiquity Press.
# Copyright (C) 2025 Graz University of Technology.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#
"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import uuid

import pytest
from invenio_app.factory import create_app as _create_app

from tests.mock_module.ext import current_mock_collections


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_base.blueprints": [
            "mock_module = tests.mock_module.blueprint:create_ui_blueprint",
        ],
        "invenio_base.api_blueprints": [
            "mock_module = tests.mock_module.ext:create_bp",
        ],
        "invenio_base.apps": [
            "mock_collections = tests.mock_module.ext:MockCollectionsExt",
        ],
        "invenio_base.api_apps": [
            "mock_collections = tests.mock_module.ext:MockCollectionsExt",
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_app


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture."""
    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )
    # Variable not used. We set it to silent warnings
    app_config["JSONSCHEMAS_HOST"] = "not-used"
    app_config["THEME_FRONTPAGE"] = False

    # Set a higher max depth for tests that need nested collections
    app_config["COLLECTIONS_MAX_DEPTH"] = 3

    return app_config


@pytest.fixture(scope="module")
def collections_service():
    """Return the collections service."""
    return current_mock_collections.service


@pytest.fixture(scope="module")
def community():
    """A namespace identifier for collections tests."""

    class SimpleNamespace:
        id = str(uuid.uuid4())

    return SimpleNamespace()
