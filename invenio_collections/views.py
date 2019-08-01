# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
