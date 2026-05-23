# SPDX-FileCopyrightText: 2025 Ubiquity Press.
# SPDX-License-Identifier: MIT

"""Helper proxy to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy

current_collections = LocalProxy(lambda: current_app.extensions["invenio-collections"])
