# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

from invenio_records import signals
from sqlalchemy.event import contains, listen, remove

from . import config


class _AppState(object):
    """State for storing collections."""

    def __init__(self, app, cache=None):
        """Initialize state."""
        self.app = app
        self.cache = cache
        if self.app.config['COLLECTIONS_REGISTER_RECORD_SIGNALS']:
            self.register_signals()

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

    def register_signals(self):
        """Register signals."""
        from .models import Collection
        from .receivers import CollectionUpdater

        if self.app.config['COLLECTIONS_USE_PERCOLATOR']:
            from .percolator import collection_inserted_percolator, \
                collection_removed_percolator, \
                collection_updated_percolator
            # Register collection signals to update percolators
            listen(Collection, 'after_insert',
                   collection_inserted_percolator)
            listen(Collection, 'after_update',
                   collection_updated_percolator)
            listen(Collection, 'after_delete',
                   collection_removed_percolator)
        # Register Record signals to update record['_collections']
        self.update_function = CollectionUpdater(app=self.app)
        signals.before_record_insert.connect(self.update_function,
                                             weak=False)
        signals.before_record_update.connect(self.update_function,
                                             weak=False)

    def unregister_signals(self):
        """Unregister signals."""
        from .models import Collection
        from .percolator import collection_inserted_percolator, \
            collection_removed_percolator, collection_updated_percolator
        # Unregister Record signals
        if hasattr(self, 'update_function'):
            signals.before_record_insert.disconnect(self.update_function)
            signals.before_record_update.disconnect(self.update_function)
        # Unregister collection signals
        if contains(Collection, 'after_insert',
                    collection_inserted_percolator):
            remove(Collection, 'after_insert', collection_inserted_percolator)
            remove(Collection, 'after_update', collection_updated_percolator)
            remove(Collection, 'after_delete', collection_removed_percolator)


class InvenioCollections(object):
    """Invenio-Collections extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        """Flask application initialization."""
        from .cli import collections as collections_cmd

        self.init_config(app)
        state = _AppState(app=app, cache=kwargs.get('cache'))
        app.extensions['invenio-collections'] = state
        app.cli.add_command(collections_cmd)

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            "COLLECTIONS_BASE_TEMPLATE",
            app.config.get("BASE_TEMPLATE",
                           "invenio_collections/base.html"))
        for k in dir(config):
            if k.startswith('COLLECTIONS_'):
                app.config.setdefault(k, getattr(config, k))
