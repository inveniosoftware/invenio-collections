# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 CERN.
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_collections import InvenioCollections


def test_version():
    """Test version import."""
    from invenio_collections import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioCollections(app)
    assert "invenio-collections" in app.extensions

    app = Flask("testapp")
    ext = InvenioCollections()
    assert "invenio-collections" not in app.extensions
    ext.init_app(app)
    assert "invenio-collections" in app.extensions
