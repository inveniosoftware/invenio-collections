# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test suite for collection limits."""

import pytest
from invenio_access.permissions import system_identity

from invenio_collections.api import Collection, CollectionTree
from invenio_collections.errors import MaxCollectionsExceeded, MaxTreesExceeded
from invenio_collections.proxies import current_collections


@pytest.fixture()
def collections_service():
    """Get collections service fixture."""
    return current_collections.service


def test_max_trees_limit(app, db, collections_service, community, community_owner):
    """Test that tree creation respects the maximum trees limit."""
    # Set a low limit for testing
    app.config["COLLECTIONS_MAX_TREES"] = 2

    # Create first tree - should succeed
    tree1 = collections_service.create_tree(
        identity=system_identity,
        namespace_id=community.id,
        data={"slug": "tree-1", "title": "Tree 1"},
    )
    assert tree1._tree.slug == "tree-1"

    # Create second tree - should succeed
    tree2 = collections_service.create_tree(
        identity=system_identity,
        namespace_id=community.id,
        data={"slug": "tree-2", "title": "Tree 2"},
    )
    assert tree2._tree.slug == "tree-2"

    # Try to create third tree - should fail
    with pytest.raises(MaxTreesExceeded) as exc_info:
        collections_service.create_tree(
            identity=system_identity,
            namespace_id=community.id,
            data={"slug": "tree-3", "title": "Tree 3"},
        )

    assert exc_info.value.current_count == 2
    assert exc_info.value.max_trees == 2
    assert "Cannot create category" in str(exc_info.value)
    assert "already has 2 categories" in str(exc_info.value)


def test_max_collections_limit(
    app, db, collections_service, community, community_owner
):
    """Test that collection creation respects the maximum collections limit."""
    # Set a low limit for testing
    app.config["COLLECTIONS_MAX_COLLECTIONS_PER_TREE"] = 3

    # Create a tree
    tree = CollectionTree.create(
        title="Test Tree",
        order=10,
        namespace_id=community.id,
        slug="test-tree",
    )

    # Create first collection - should succeed
    coll1 = collections_service.create(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="test-tree",
        data={
            "slug": "collection-1",
            "title": "Collection 1",
            "search_query": "metadata.title:test1",
        },
    )
    assert coll1._collection.slug == "collection-1"

    # Create second collection - should succeed
    coll2 = collections_service.create(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="test-tree",
        data={
            "slug": "collection-2",
            "title": "Collection 2",
            "search_query": "metadata.title:test2",
        },
    )
    assert coll2._collection.slug == "collection-2"

    # Create third collection - should succeed
    coll3 = collections_service.create(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="test-tree",
        data={
            "slug": "collection-3",
            "title": "Collection 3",
            "search_query": "metadata.title:test3",
        },
    )
    assert coll3._collection.slug == "collection-3"

    # Try to create fourth collection - should fail
    with pytest.raises(MaxCollectionsExceeded) as exc_info:
        collections_service.create(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug="test-tree",
            data={
                "slug": "collection-4",
                "title": "Collection 4",
                "search_query": "metadata.title:test4",
            },
        )

    assert exc_info.value.current_count == 3
    assert exc_info.value.max_collections == 3
    assert "Cannot create collection" in str(exc_info.value)
    assert "already has 3 collections" in str(exc_info.value)


def test_max_collections_limit_with_subcollections(
    app, db, collections_service, community, community_owner
):
    """Test that subcollection creation also respects the limit."""
    # Set a low limit for testing
    app.config["COLLECTIONS_MAX_COLLECTIONS_PER_TREE"] = 2

    # Create a tree
    tree = CollectionTree.create(
        title="Test Tree",
        order=10,
        namespace_id=community.id,
        slug="test-tree-sub",
    )

    # Create parent collection
    parent = collections_service.create(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="test-tree-sub",
        data={
            "slug": "parent",
            "title": "Parent Collection",
            "search_query": "metadata.title:parent",
        },
    )

    # Create child collection
    child = collections_service.add(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="test-tree-sub",
        slug="parent",
        data={
            "slug": "child",
            "title": "Child Collection",
            "search_query": "metadata.title:child",
        },
    )
    assert child._collection.slug == "child"

    # Try to create another collection (would be 3rd) - should fail
    with pytest.raises(MaxCollectionsExceeded):
        collections_service.create(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug="test-tree-sub",
            data={
                "slug": "collection-3",
                "title": "Collection 3",
                "search_query": "metadata.title:test3",
            },
        )


def test_unlimited_trees(app, db, collections_service, community, community_owner):
    """Test that setting max trees to 0 allows unlimited trees."""
    # Set to unlimited
    app.config["COLLECTIONS_MAX_TREES"] = 0

    # Create multiple trees - all should succeed
    for i in range(15):
        tree = collections_service.create_tree(
            identity=system_identity,
            namespace_id=community.id,
            data={"slug": f"tree-{i}", "title": f"Tree {i}"},
        )
        assert tree._tree.slug == f"tree-{i}"


def test_unlimited_collections(
    app, db, collections_service, community, community_owner
):
    """Test that setting max collections to 0 allows unlimited collections."""
    # Set to unlimited
    app.config["COLLECTIONS_MAX_COLLECTIONS_PER_TREE"] = 0

    # Create a tree
    tree = CollectionTree.create(
        title="Unlimited Test Tree",
        order=10,
        namespace_id=community.id,
        slug="unlimited-tree",
    )

    # Create multiple collections - all should succeed
    for i in range(15):
        coll = collections_service.create(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug="unlimited-tree",
            data={
                "slug": f"collection-{i}",
                "title": f"Collection {i}",
                "search_query": f"metadata.title:test{i}",
            },
        )
        assert coll._collection.slug == f"collection-{i}"


def test_error_messages(app, db, collections_service, community, community_owner):
    """Test that error messages contain the correct information."""
    # Test tree limit error message
    app.config["COLLECTIONS_MAX_TREES"] = 1

    tree1 = collections_service.create_tree(
        identity=system_identity,
        namespace_id=community.id,
        data={"slug": "tree-1", "title": "Tree 1"},
    )

    try:
        collections_service.create_tree(
            identity=system_identity,
            namespace_id=community.id,
            data={"slug": "tree-2", "title": "Tree 2"},
        )
        pytest.fail("Should have raised MaxTreesExceeded")
    except MaxTreesExceeded as e:
        assert e.current_count == 1
        assert e.max_trees == 1
        assert "Namespace already has 1 categories" in str(e)
        assert "Maximum allowed is 1" in str(e)

    # Test collection limit error message
    app.config["COLLECTIONS_MAX_COLLECTIONS_PER_TREE"] = 1

    tree2 = CollectionTree.create(
        title="Test Tree 2",
        order=10,
        namespace_id=community.id,
        slug="test-tree-2",
    )

    coll1 = collections_service.create(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="test-tree-2",
        data={
            "slug": "collection-1",
            "title": "Collection 1",
            "search_query": "metadata.title:test1",
        },
    )

    try:
        collections_service.create(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug="test-tree-2",
            data={
                "slug": "collection-2",
                "title": "Collection 2",
                "search_query": "metadata.title:test2",
            },
        )
        pytest.fail("Should have raised MaxCollectionsExceeded")
    except MaxCollectionsExceeded as e:
        assert e.current_count == 1
        assert e.max_collections == 1
        assert "Category already has 1 collections" in str(e)
        assert "Maximum allowed is 1" in str(e)
