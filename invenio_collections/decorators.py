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

import functools

from flask import abort, flash, g, redirect, request, url_for
from flask_login import current_user

from invenio_base.i18n import _

from .models import Collection


def check_collection(method=None, name_getter=None, default_collection=False):
    """Check collection existence and authorization for current user."""
    if method is None:
        return functools.partial(check_collection, name_getter=name_getter,
                                 default_collection=default_collection)

    def collection_name_from_request():
        """Return collection name from request arguments 'cc' or 'c'."""
        collection = request.values.get('cc')
        if collection is None and len(request.values.getlist('c')) == 1:
            collection = request.values.get('c')
        return collection

    name_getter = name_getter or collection_name_from_request

    @functools.wraps(method)
    def decorated(*args, **kwargs):
        uid = current_user.get_id()
        name = name_getter()
        if name:
            g.collection = collection = Collection.query.filter(
                Collection.name == name).first_or_404()
        elif default_collection:
            g.collection = collection = Collection.query.get_or_404(1)
        else:
            return abort(404)

        if collection.is_restricted:
            from invenio_access.engine import acc_authorize_action
            from invenio_access.local_config import VIEWRESTRCOLL
            (auth_code, auth_msg) = acc_authorize_action(
                uid,
                VIEWRESTRCOLL,
                collection=collection.name
            )
            if auth_code:
                flash(_('This collection is restricted.'), 'error')
            if auth_code and current_user.is_guest:
                return redirect(url_for('webaccount.login',
                                        referer=request.url))
            elif auth_code:
                return abort(401)

        return method(collection, *args, **kwargs)
    return decorated
