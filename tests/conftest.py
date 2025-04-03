# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 CERN.
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#
"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_app.factory import create_app as _create_app


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return _create_app
