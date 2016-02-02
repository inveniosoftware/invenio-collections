# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Admin views for invenio-accounts."""

from flask import current_app, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.fields import DateTimeField
from flask_login import login_user, logout_user
from werkzeug.local import LocalProxy

from .models import Collection


def _(x):
    """Identity."""
    return x


class CollectionView(ModelView):
    """Flask-Admin view to manage users."""

    can_view_details = True
    can_delete = False

    list_all = (
        'id', 'name', 'left', 'right', 'dbquery', 'level', 'tree_id'
    )

    column_list = list_all

    column_list = \
        form_columns = \
        column_searchable_list = \
        column_sortable_list = \
        column_details_list = \
        list_all

    column_filters = ('id', 'name', 'tree_id', 'level')

    column_default_sort = ('left', True)

    column_labels = {
        'dbquery': _('Search Query'),
    }


collection_adminview = {
    'model': Collection,
    'modelview': CollectionView,
    'category': _('Collections'),
}

__all__ = ('collection_adminview',)
