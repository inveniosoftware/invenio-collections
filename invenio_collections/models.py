# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2011, 2012, 2013, 2014, 2015 CERN.
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

"""Database models for collections."""

from invenio_db import db
from sqlalchemy_mptt.mixins import BaseNestedSets


class Collection(db.Model, BaseNestedSets):
    """Collection model, defined as a tree node."""

    __tablename__ = 'collection'

    def __repr__(self):
        """Return class representation."""
        return ('Collection <id: {0.id}, name: {0.name}, '
                'dbquery: {0.dbquery}>'.format(self))

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, index=True, nullable=False)

    dbquery = db.Column(db.Text, nullable=True)

    reference = db.Column(db.Integer, db.ForeignKey('collection.id'))

__all__ = ('Collection', )
