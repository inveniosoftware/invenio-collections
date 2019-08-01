# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Database models for collections."""

from invenio_db import db
from sqlalchemy.event import listen
from sqlalchemy.orm import validates
from sqlalchemy_mptt.mixins import BaseNestedSets

from .proxies import current_collections


class Collection(db.Model, BaseNestedSets):
    """Collection model, defined as a tree node."""

    __tablename__ = 'collection'

    def __repr__(self):
        """Return class representation."""
        return ('Collection <id: {0.id}, name: {0.name}, '
                'dbquery: {0.dbquery}>'.format(self))

    id = db.Column(db.Integer, primary_key=True)
    """Collection identifier."""

    name = db.Column(db.String(255), unique=True, index=True, nullable=False)
    """Collection name."""

    dbquery = db.Column(db.Text, nullable=True)
    """Query that returns all records that belong to this collection.."""

    @validates('parent_id')
    def validate_parent_id(self, key, parent_id):
        """Parent has to be different from itself."""
        id_ = getattr(self, 'id', None)
        if id_ is not None and parent_id is not None:
            assert id_ != parent_id, 'Can not be attached to itself.'
        return parent_id


def collection_removed_or_inserted(mapper, connection, target):
    """Invalidate cache on collection insert or delete."""
    current_collections.collections = None


def collection_attribute_changed(target, value, oldvalue, initiator):
    """Invalidate cache if dbquery change."""
    if value != oldvalue:
        current_collections.collections = None


# update cache with list of collections
listen(Collection, 'after_insert', collection_removed_or_inserted)
listen(Collection, 'after_delete', collection_removed_or_inserted)
listen(Collection.dbquery, 'set', collection_attribute_changed)
listen(Collection.parent_id, 'set', collection_attribute_changed)


__all__ = ('Collection', )
