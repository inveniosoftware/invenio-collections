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

"""Click command-line interface for collection management."""

from __future__ import absolute_import, print_function

from functools import wraps

import click
from asciitree import LeftAligned
from asciitree.traversal import AttributeTraversal as _AT
from flask_cli import with_appcontext
from invenio_db import db
from sqlalchemy.orm.exc import NoResultFound

from .errors import CollectionError
from .models import Collection


def dry_run(func):
    """Dry run: simulate sql execution."""
    @wraps(func)
    def inner(dry_run, *args, **kwargs):
        ret = func(dry_run=dry_run, *args, **kwargs)
        if not dry_run:
            db.session.commit()
        else:
            db.session.rollback()
        return ret
    return inner


class StyleMixin(object):
    """Implement get text with style."""

    def get_text(self, node):
        """Get node text representation."""
        return click.style(
            repr(node), fg='green' if node.level > 1 else 'red'
        )


class CollTraversalPathToRoot(StyleMixin):
    """Used by asciitree to render the tree if you know the path to root."""

    def __init__(self, nodes):
        """Set root of the tree."""
        self.nodes = nodes
        self.nodes.reverse()
        self.root = self.nodes[0]

    def get_children(self, node):
        """Get children."""
        #  if node in self.nodes:
        try:
            index = self.nodes.index(node) + 1
            return [self.nodes[index]]
        except IndexError:
            return []

    def get_root(self, tree):
        """Get root."""
        return self.root


class AttributeTraversal(StyleMixin, _AT):
    """Use better get_text method."""

    pass


#
# Collection management commands
#
@click.group()
def collections():
    """Collection management commands."""


@collections.command()
@click.argument('names', nargs=-1)
@with_appcontext
def tree(names):
    """Show the tree of the collection(s) specified."""
    # query
    query = Collection.query
    if names:
        query = query.filter(Collection.name.in_(names))
    else:
        query = query.filter(Collection.level == 1)
    # print tree
    tr = LeftAligned(traverse=AttributeTraversal())
    for coll in query.all():
        click.secho(tr(coll))


@collections.command()
@click.argument('name')
@with_appcontext
def path(name):
    """Print path to root."""
    try:
        coll = Collection.query.filter(Collection.name == name).one()
        tr = LeftAligned(
            traverse=CollTraversalPathToRoot(coll.path_to_root().all()))
        click.echo(tr(coll))
    except NoResultFound:
        raise click.UsageError("Collection {} not found".format(name))


@collections.command()
@click.argument('name')
@click.option('-q', '--query', default=None,
              help="Specify query for the collection")
@click.option('-p', '--parent', default=None,
              help="Parent collection name")
@click.option('-n', '--dry-run', default=False, is_flag=True)
@click.option('-v', '--verbose', default=False, is_flag=True)
@with_appcontext
@dry_run
def create(name, dry_run, verbose, query=None, parent=None):
    """Create new collection."""
    if parent is not None:
        parent = Collection.query.filter_by(name=parent).one().id
    collection = Collection(name=name, dbquery=query, parent_id=parent)
    db.session.add(collection)
    if verbose:
        click.secho("New collection: {}".format(collection))


@collections.command()
@click.argument('name')
@click.option('-n', '--dry-run', default=False, is_flag=True)
@click.option('-v', '--verbose', default=False, is_flag=True)
@with_appcontext
@dry_run
def delete(name, dry_run, verbose):
    """Delete a collection."""
    collection = Collection.query.filter_by(name=name).one()
    if verbose:
        tr = LeftAligned(traverse=AttributeTraversal())
        click.secho(tr(collection), fg="red")
    db.session.delete(collection)


@collections.command()
@click.argument('name')
@with_appcontext
def query(name):
    """Print the collection query."""
    collection = Collection.query.filter_by(name=name).one()
    click.echo(collection.dbquery)


@collections.command()
@click.argument('names', nargs=-1, required=True)
@click.argument('parent', nargs=1)
@click.option('-n', '--dry-run', default=False, is_flag=True)
@click.option('-v', '--verbose', default=False, is_flag=True)
@with_appcontext
@dry_run
def attach(names, parent, dry_run, verbose):
    """Attach collection(s) to a parent."""
    parent = Collection.query.filter_by(name=parent).one()
    collections = Collection.query.filter(Collection.name.in_(names)).all()
    for collection in collections:
        collection.move_inside(parent.id)
        if verbose:
            click.secho(
                'Collection "{0}" is being attached to "{1}".'.format(
                    collection.name, parent
                ), fg='green')
