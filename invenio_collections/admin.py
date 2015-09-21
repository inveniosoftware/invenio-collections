# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Admin interface for managin collections."""

from __future__ import absolute_import

from invenio_ext.admin.views import ModelView
from invenio_ext.sqlalchemy import db

from wtforms import TextField

from .models import Collection, Collectionname


class CollectionAdmin(ModelView):

    """Configuration of collection admin interface."""

    _can_create = True
    _can_edit = True
    _can_delete = True

    acc_view_action = 'cfgwebsearch'
    acc_edit_action = 'cfgwebsearch'
    acc_delete_action = 'cfgwebsearch'

    column_list = (
        'name', 'dbquery',
    )
    column_searchable_list = ('name', 'dbquery')

    form_columns = ('name', 'dbquery')
    form_overrides = dict(dbquery=TextField)

    page_size = 100

    def __init__(self, model, session, **kwargs):
        super(CollectionAdmin, self).__init__(
            model, session, **kwargs
        )


def register_admin(app, admin):
    """Called on app initialization to register administration interface."""
    category = "Collections"
    admin.category_icon_classes[category] = "fa fa-th-list"
    admin.add_view(CollectionAdmin(
        Collection, db.session,
        name='Collections', category=category
    ))
