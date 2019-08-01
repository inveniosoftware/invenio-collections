# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os

import pytest
from flask import Flask
from flask_babelex import Babel
from flask_breadcrumbs import Breadcrumbs
from flask_menu import Menu
from invenio_db import InvenioDB, db
from invenio_records import InvenioRecords
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from invenio_collections import InvenioCollections, current_collections
from invenio_collections.views import blueprint


@pytest.fixture()
def app(request):
    """Flask application fixture."""
    app = Flask('testapp')
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI',
                                          'sqlite://'),
        SERVER_NAME='localhost',
    )
    Babel(app)
    Menu(app)
    Breadcrumbs(app)
    InvenioDB(app)
    InvenioCollections(app)
    InvenioRecords(app)

    app.register_blueprint(blueprint)

    with app.app_context():
        if str(db.engine.url) != 'sqlite://' and \
                not database_exists(str(db.engine.url)):
            create_database(str(db.engine.url))
        db.create_all()

    def teardown():
        with app.app_context():
            if str(db.engine.url) != 'sqlite://':
                drop_database(str(db.engine.url))

    request.addfinalizer(teardown)

    with app.app_context():
        db.create_all()

    return app
