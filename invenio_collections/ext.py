# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module for organizing metadata into collections."""

from __future__ import absolute_import, print_function

from . import config
from .cli import collections as collections_cmd
from .receivers import update_collections


class _AppState(object):
    """State for storing collections."""

    def __init__(self, app, cache=None):
        """Initialize state."""
        self.app = app
        self.cache = cache

    @property
    def collections(self):
        """Get list of collections."""
        # if cache server is configured, load collection from there
        if self.cache:
            return self.cache.get(
                self.app.config['COLLECTIONS_CACHE_KEY'])

    @collections.setter
    def collections(self, values):
        """Set list of collections."""
        # if cache server is configured, save collection list
        if self.cache:
            self.cache.set(
                self.app.config['COLLECTIONS_CACHE_KEY'], values)


class InvenioCollections(object):
    """Invenio-Collections extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        """Flask application initialization."""
        self.init_config(app)
        state = _AppState(app=app, cache=kwargs.get('cache'))
        app.extensions['invenio-collections'] = state
        app.cli.add_command(collections_cmd)

        if app.config['COLLECTIONS_REGISTER_RECORD_SIGNALS']:
            from invenio_records import signals
            signals.before_record_insert.connect(update_collections)
            signals.before_record_update.connect(update_collections)

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            "COLLECTIONS_BASE_TEMPLATE",
            app.config.get("BASE_TEMPLATE",
                           "invenio_collections/base.html"))
        for k in dir(config):
            if k.startswith('COLLECTIONS_'):
                app.config.setdefault(k, getattr(config, k))
