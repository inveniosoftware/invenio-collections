# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""CLI tests."""
from __future__ import absolute_import, print_function

from click.testing import CliRunner
from flask_cli import ScriptInfo
from invenio_db import db

from invenio_collections.cli import collections as cmd
from invenio_collections.models import Collection


def test_cli(app):
    """Test CLI."""
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    # Test collection creation.
    with runner.isolated_filesystem():
        result = runner.invoke(cmd, ['create', 'Root'], obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            root = Collection.query.filter_by(name='Root').one()
            assert 1 == root.id
            assert root.dbquery is None

        result = runner.invoke(cmd, ['create', 'Root'], obj=script_info)
        assert 0 != result.exit_code

        result = runner.invoke(cmd, ['create', 'CollCycle', '-p', 'CollCycle'],
                               obj=script_info)
        assert 0 != result.exit_code

        result = runner.invoke(cmd, ['create', 'Coll', '-p', 'not-exist'],
                               obj=script_info)
        assert 0 != result.exit_code

        result = runner.invoke(cmd, ['create', 'verbose', '-v'],
                               obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            first = Collection.query.filter_by(name='verbose').one()

        result = runner.invoke(cmd, ['create', 'First', '--parent', 'Root'],
                               obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            first = Collection.query.filter_by(name='First').one()
            assert root.id == first.parent_id

        result = runner.invoke(cmd, ['create', 'Second'],
                               obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            second = Collection.query.filter_by(name='Second').one()
            assert second.parent_id is None

        result = runner.invoke(cmd, ['create', 'Third', '-q', 'title:Fuu',
                                     '--parent', 'Root'], obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            third = Collection.query.filter_by(name='Third').one()
            assert root.id == third.parent_id
            assert 'title:Fuu' == third.dbquery

        result = runner.invoke(cmd, ['attach', 'Second'],
                               obj=script_info)
        assert 0 != result.exit_code

        result = runner.invoke(cmd, ['attach', 'Second', 'Root'],
                               obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            second = Collection.query.filter_by(name='Second').one()
            assert root.id == second.parent_id
            assert root.id == second.tree_id

        result = runner.invoke(cmd, ['attach', 'verbose', 'Root', '-v'],
                               obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            verbose = Collection.query.filter_by(name='verbose').one()
            assert root.id == verbose.parent_id
            assert root.id == verbose.tree_id

        result = runner.invoke(cmd, ['attach', 'Third', 'Second', '-n'],
                               obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            third = Collection.query.filter_by(name='Third').one()
            assert root.id == third.parent_id
            assert root.id == third.tree_id

        result = runner.invoke(cmd, ['attach', 'Third', 'Second'],
                               obj=script_info)
        assert 0 == result.exit_code

        with app.app_context():
            second = Collection.query.filter_by(name='Second').one()
            third = Collection.query.filter_by(name='Third').one()
            assert second.id == third.parent_id
            assert root.id == third.tree_id

        result = runner.invoke(cmd, ['attach', 'Third', 'not-exist'],
                               obj=script_info)
        assert 0 != result.exit_code


def test_tree(app):
    """Test CLI tree."""
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    #                               a
    #                             (None)
    #            +------------------+--------------------+
    #            |                                       |
    #            b                                       e
    #         (None)                        (title:Test2 OR title:Test3)
    #     +------+-----+                    +------------+------------+
    #     |            |                    |            |            |
    #     c            d                    f            g            h
    # (title:Test0) (title:Test1)     (title:Test2)    (None)       (None)
    #                                                    |            |
    #                                                    i            j
    #                                             (title:Test3) (title:Test4)

    with runner.isolated_filesystem():
        with app.app_context():
            a = Collection(name="a")
            b = Collection(name="b", parent=a)
            e = Collection(
                name="e", dbquery="title:Test2 OR title:Test3", parent=a)
            c = Collection(name="c", dbquery="title:Test0", parent=b)
            d = Collection(name="d", dbquery="title:Test1", parent=b)
            f = Collection(name="f", dbquery="title:Test2", parent=e)
            g = Collection(name="g", parent=e)
            h = Collection(name="h", parent=e)
            i = Collection(name="i", dbquery="title:Test3", parent=g)
            j = Collection(name="j", dbquery="title:Test4", parent=h)

            for c in [a, b, c, d, e, f, g, h, i, j]:
                db.session.add(c)
            db.session.commit()

        result = runner.invoke(cmd, ['tree'], obj=script_info)
        assert 0 == result.exit_code
        aspected = (
            "Collection <id: 1, name: a, dbquery: None>\n "
            "+-- Collection <id: 2, name: b, dbquery: None>\n "
            "|   +-- Collection <id: 4, name: c, dbquery: title:Test0>\n "
            "|   +-- Collection <id: 5, name: d, dbquery: title:Test1>\n "
            "+-- Collection <id: 3, name: e, dbquery: "
            "title:Test2 OR title:Test3>\n "
            "    +-- Collection <id: 6, name: f, dbquery: title:Test2>\n "
            "    +-- Collection <id: 7, name: g, dbquery: None>\n "
            "    |   +-- Collection <id: 9, name: i, dbquery: title:Test3>\n "
            "    +-- Collection <id: 8, name: h, dbquery: None>\n "
            "        +-- Collection <id: 10, name: j, dbquery: title:Test4>\n"
        )
        assert result.output == aspected

        result = runner.invoke(cmd, ['tree', 'e'], obj=script_info)
        assert 0 == result.exit_code
        aspected = (
            "Collection <id: 3, name: e, dbquery: "
            "title:Test2 OR title:Test3>\n "
            "+-- Collection <id: 6, name: f, dbquery: title:Test2>\n "
            "+-- Collection <id: 7, name: g, dbquery: None>\n "
            "|   +-- Collection <id: 9, name: i, dbquery: title:Test3>\n "
            "+-- Collection <id: 8, name: h, dbquery: None>\n "
            "    +-- Collection <id: 10, name: j, dbquery: title:Test4>\n"
        )
        assert result.output == aspected

        result = runner.invoke(cmd, ['tree', 'e', 'd'], obj=script_info)
        assert 0 == result.exit_code
        aspected = (
            "Collection <id: 5, name: d, dbquery: title:Test1>\n"
            "Collection <id: 3, name: e, dbquery: "
            "title:Test2 OR title:Test3>\n "
            "+-- Collection <id: 6, name: f, dbquery: title:Test2>\n "
            "+-- Collection <id: 7, name: g, dbquery: None>\n "
            "|   +-- Collection <id: 9, name: i, dbquery: title:Test3>\n "
            "+-- Collection <id: 8, name: h, dbquery: None>\n "
            "    +-- Collection <id: 10, name: j, dbquery: title:Test4>\n"
        )
        assert result.output == aspected


def test_path(app):
    """Test CLI path."""
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    #                               a
    #                             (None)
    #            +------------------+--------------------+
    #            |                                       |
    #            b                                       e
    #         (None)                        (title:Test2 OR title:Test3)
    #     +------+-----+                    +------------+------------+
    #     |            |                    |            |            |
    #     c            d                    f            g            h
    # (title:Test0) (title:Test1)     (title:Test2)    (None)       (None)
    #                                                    |            |
    #                                                    i            j
    #                                             (title:Test3) (title:Test4)

    with runner.isolated_filesystem():
        with app.app_context():
            a = Collection(name="a")
            b = Collection(name="b", parent=a)
            e = Collection(
                name="e", dbquery="title:Test2 OR title:Test3", parent=a)
            c = Collection(name="c", dbquery="title:Test0", parent=b)
            d = Collection(name="d", dbquery="title:Test1", parent=b)
            f = Collection(name="f", dbquery="title:Test2", parent=e)
            g = Collection(name="g", parent=e)
            h = Collection(name="h", parent=e)
            i = Collection(name="i", dbquery="title:Test3", parent=g)
            j = Collection(name="j", dbquery="title:Test4", parent=h)

            for c in [a, b, c, d, e, f, g, h, i, j]:
                db.session.add(c)
            db.session.commit()

        result = runner.invoke(cmd, ['path'], obj=script_info)
        assert 0 != result.exit_code

        result = runner.invoke(cmd, ['path', 'not-exist'], obj=script_info)
        assert 0 != result.exit_code

        result = runner.invoke(cmd, ['path', 'a'], obj=script_info)
        assert 0 == result.exit_code
        aspected = (
            "Collection <id: 1, name: a, dbquery: None>\n"
        )
        assert result.output == aspected

        result = runner.invoke(cmd, ['path', 'e'], obj=script_info)
        assert 0 == result.exit_code
        aspected = (
            "Collection <id: 1, name: a, dbquery: None>\n "
            "+-- Collection <id: 3, name: e, dbquery: "
            "title:Test2 OR title:Test3>\n"
        )
        assert result.output == aspected

        result = runner.invoke(cmd, ['path', 'g'], obj=script_info)
        assert 0 == result.exit_code
        aspected = (
            "Collection <id: 1, name: a, dbquery: None>\n "
            "+-- Collection <id: 3, name: e, dbquery: "
            "title:Test2 OR title:Test3>\n "
            "    +-- Collection <id: 7, name: g, dbquery: None>\n"
        )
        assert result.output == aspected

        result = runner.invoke(cmd, ['path', 'i'], obj=script_info)
        assert 0 == result.exit_code
        aspected = (
            "Collection <id: 1, name: a, dbquery: None>\n "
            "+-- Collection <id: 3, name: e, dbquery: "
            "title:Test2 OR title:Test3>\n "
            "    +-- Collection <id: 7, name: g, dbquery: None>\n "
            "        +-- Collection <id: 9, name: i, dbquery: title:Test3>\n"
        )
        assert result.output == aspected


def test_delete(app):
    """Test CLI delete."""
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    #                               a
    #                             (None)
    #            +------------------+--------------------+
    #            |                                       |
    #            b                                       e
    #         (None)                        (title:Test2 OR title:Test3)
    #     +------+-----+                    +------------+------------+
    #     |            |                    |            |            |
    #     c            d                    f            g            h
    # (title:Test0) (title:Test1)     (title:Test2)    (None)       (None)
    #                                                    |            |
    #                                                    i            j
    #                                             (title:Test3) (title:Test4)

    with runner.isolated_filesystem():
        with app.app_context():
            a = Collection(name="a")
            b = Collection(name="b", parent=a)
            e = Collection(
                name="e", dbquery="title:Test2 OR title:Test3", parent=a)
            c = Collection(name="c", dbquery="title:Test0", parent=b)
            d = Collection(name="d", dbquery="title:Test1", parent=b)
            f = Collection(name="f", dbquery="title:Test2", parent=e)
            g = Collection(name="g", parent=e)
            h = Collection(name="h", parent=e)
            i = Collection(name="i", dbquery="title:Test3", parent=g)
            j = Collection(name="j", dbquery="title:Test4", parent=h)

            for c in [a, b, c, d, e, f, g, h, i, j]:
                db.session.add(c)
            db.session.commit()

            result = runner.invoke(cmd, ['delete'], obj=script_info)
            assert 0 != result.exit_code

            result = runner.invoke(cmd, ['delete', 'not-exist'],
                                   obj=script_info)
            assert 0 != result.exit_code

        with app.app_context():
            result = runner.invoke(cmd, ['delete', 'a', '-n'], obj=script_info)
            assert 0 == result.exit_code
            for coll in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
                assert Collection.query.filter_by(
                    name=coll).first() is not None
            db.session.expunge_all()

            result = runner.invoke(cmd, ['delete', 'j'], obj=script_info)
            assert 0 == result.exit_code

            db.session.expunge_all()
            for coll in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']:
                assert Collection.query.filter_by(
                    name=coll).first() is not None
            assert Collection.query.filter_by(name='j').first() is None

            result = runner.invoke(cmd, ['delete', 'e'], obj=script_info)
            assert 0 == result.exit_code
            for coll in ['a', 'b', 'c', 'd']:
                assert Collection.query.filter_by(
                    name=coll).first() is not None
            for coll in ['e', 'f', 'g', 'h', 'i', 'j']:
                assert Collection.query.filter_by(name=coll).first() is None

            result = runner.invoke(cmd, ['delete', 'c', '-v'], obj=script_info)
            assert 0 == result.exit_code
            assert Collection.query.filter_by(name='c').first() is None


def test_query(app):
    """Test query."""
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    #                               a
    #                             (None)
    #            +------------------+--------------------+
    #            |                                       |
    #            b                                       e
    #         (None)                        (title:Test2 OR title:Test3)
    #     +------+-----+                    +------------+------------+
    #     |            |                    |            |            |
    #     c            d                    f            g            h
    # (title:Test0) (title:Test1)     (title:Test2)    (None)       (None)
    #                                                    |            |
    #                                                    i            j
    #                                             (title:Test3) (title:Test4)

    with runner.isolated_filesystem():
        with app.app_context():
            a = Collection(name="a")
            b = Collection(name="b", parent=a)
            e = Collection(
                name="e", dbquery="title:Test2 OR title:Test3", parent=a)
            c = Collection(name="c", dbquery="title:Test0", parent=b)
            d = Collection(name="d", dbquery="title:Test1", parent=b)
            f = Collection(name="f", dbquery="title:Test2", parent=e)
            g = Collection(name="g", parent=e)
            h = Collection(name="h", parent=e)
            i = Collection(name="i", dbquery="title:Test3", parent=g)
            j = Collection(name="j", dbquery="title:Test4", parent=h)

            for c in [a, b, c, d, e, f, g, h, i, j]:
                db.session.add(c)
            db.session.commit()

            result = runner.invoke(cmd, ['query'], obj=script_info)
            assert 0 != result.exit_code

            result = runner.invoke(cmd, ['query', 'not-exist'],
                                   obj=script_info)
            assert 0 != result.exit_code

            colls = {'a': '\n', 'b': '\n', 'c': 'title:Test0\n',
                     'd': 'title:Test1\n', 'e': 'title:Test2 OR title:Test3\n',
                     'f': 'title:Test2\n', 'g': '\n', 'h': '\n',
                     'i': 'title:Test3\n', 'j': 'title:Test4\n'}
            for (name, query) in iter(colls.items()):
                result = runner.invoke(cmd, ['query', name],
                                       obj=script_info)
                assert 0 == result.exit_code
                assert result.output == query
