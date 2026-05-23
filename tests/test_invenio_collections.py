# SPDX-FileCopyrightText: 2015 CERN.
# SPDX-FileCopyrightText: 2025 Ubiquity Press.
# SPDX-License-Identifier: MIT

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
