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

from flask import Blueprint, current_app, render_template

from .models import Collection
from .utils import slugify

blueprint = Blueprint(
    'invenio_collections',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/collection/', methods=['GET', 'POST'])
@blueprint.route('/collection/<name>', methods=['GET', 'POST'])
def collection(name=None):
    """Render the collection page.

    It renders it either with a collection specific template (aka
    collection_{collection_name}.html) or with the default collection
    template (collection.html).
    """
    if name is None:
        collection = Collection.query.get_or_404(1)
    else:
        collection = Collection.query.filter(
            Collection.name == name).first_or_404()

    # TODO add breadcrumbs
    # breadcrumbs = current_breadcrumbs + collection.breadcrumbs(ln=g.ln)[1:]
    return render_template([
        'invenio_collections/collection_{0}.html'.format(collection.id),
        'invenio_collections/collection_{0}.html'.format(slugify(name, '_')),
        current_app.config['COLLECTIONS_DEFAULT_TEMPLATE']
    ], collection=collection)
