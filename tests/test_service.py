# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test suite for the collections service."""

import uuid

import pytest
from invenio_access.permissions import system_identity

from invenio_collections.api import Collection, CollectionTree
from invenio_collections.errors import (
    CollectionHasChildren,
    CollectionNotFound,
    CollectionTreeHasCollections,
    CollectionTreeNotFound,
    DuplicateSlugError,
)


@pytest.fixture
def add_collections(app, db, community):
    """Create collections on demand."""

    def _inner():
        """Add collections to the app."""
        # Create unique slugs to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        tree = CollectionTree.create(
            title="Tree 1",
            order=10,
            namespace_id=community.id,
            slug=f"tree-1-{unique_id}",
        )
        c1 = Collection.create(
            title="Collection 1",
            search_query="metadata.title:foo",
            slug="collection-1",
            ctree=tree,
        )
        c2 = Collection.create(
            title="Collection 2",
            search_query="metadata.title:bar",
            slug="collection-2",
            ctree=tree,
            parent=c1,
        )
        return [c1, c2]

    return _inner


def test_collections_read(app, db, add_collections, collections_service, community):
    """Test collections service."""
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]

    # Read by id
    res = collections_service.read(identity=system_identity, id_=c0.id)
    assert res._collection.id == c0.id

    # Read by slug
    res = collections_service.read(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug=c0.collection_tree.slug,
        slug=c0.slug,
    )
    assert res._collection.id == c0.id


def test_collections_create(app, db, collections_service, community):
    """Test collection creation via service."""
    tree = CollectionTree.create(
        title="Tree for Create Test",
        order=10,
        namespace_id=community.id,
        slug="tree-create-test",
    )
    collection = collections_service.create(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="tree-create-test",
        data={
            "slug": "my-collection",
            "title": "My Collection",
            "search_query": "*:*",
        },
    )

    # Get the API object, just for the sake of testing
    collection = collection._collection

    assert collection.title == "My Collection"
    assert collection.collection_tree.id == tree.id

    read_collection = collections_service.read(
        identity=system_identity, id_=collection.id
    )
    assert read_collection._collection.id == collection.id
    assert read_collection._collection.title == "My Collection"


def test_collections_add(app, db, collections_service, add_collections, community):
    """Test adding a collection to another via service."""
    collections = add_collections()
    c1 = collections[0]
    c2 = collections[1]

    c3 = collections_service.add(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug=c1.collection_tree.slug,
        slug=c2.slug,
        data={
            "slug": "collection-3",
            "title": "Collection 3",
            "search_query": "metadata.title:baz",
        },
    )

    # Get the API object, just for the sake of testing
    c3 = c3._collection

    # Read the collection
    res = collections_service.read(identity=system_identity, id_=c3.id)
    assert res._collection.id == c3.id
    assert res._collection.title == "Collection 3"

    # Read the parent collection
    res = collections_service.read(identity=system_identity, id_=c2.id)
    assert res.to_dict()[c2.id]["children"] == [c3.id]


def test_collections_results(app, db, add_collections, collections_service, community):
    """Test collection results.

    The goal is to test the format returned by the service, based on the required depth.
    """
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]
    c3 = collections_service.add(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug=c0.collection_tree.slug,
        slug=c1.slug,
        data={
            "slug": "collection-3",
            "title": "Collection 3",
            "search_query": "metadata.title:baz",
        },
    )
    # Read the collection tree up to depth 2
    res = collections_service.read(identity=system_identity, id_=c0.id, depth=2)
    r_dict = res.to_dict()

    tree_slug = c0.collection_tree.slug
    expected = {
        "root": c0.id,
        c0.id: {
            "breadcrumbs": [
                {
                    "link": None,
                    "slug": "collection-1",
                    "title": "Collection 1",
                }
            ],
            "children": [c1.id],
            "depth": 0,
            "id": c0.id,
            "links": {
                "search": f"https://127.0.0.1:5000/api/collections/{c0.id}/records",
            },
            "num_records": 0,
            "order": c0.order,
            "search_query": str(c0.search_query),
            "slug": "collection-1",
            "title": "Collection 1",
        },
        c1.id: {
            "children": [],
            "depth": 1,
            "id": c1.id,
            "links": {
                "search": f"https://127.0.0.1:5000/api/collections/{c1.id}/records",
            },
            "num_records": 0,
            "order": c1.order,
            "search_query": str(c1.search_query),
            "slug": "collection-2",
            "title": "Collection 2",
        },
    }
    assert expected == r_dict

    # Read the collection tree up to depth 3
    res = collections_service.read(identity=system_identity, id_=c0.id, depth=3)
    r_dict = res.to_dict()

    # Get the API object, just for the sake of testing
    c3 = c3._collection
    expected = {
        "root": c0.id,
        c0.id: {
            "breadcrumbs": [
                {
                    "link": None,
                    "slug": "collection-1",
                    "title": "Collection 1",
                }
            ],
            "children": [c1.id],
            "depth": 0,
            "id": c0.id,
            "links": {
                "search": f"https://127.0.0.1:5000/api/collections/{c0.id}/records",
            },
            "num_records": 0,
            "order": c0.order,
            "search_query": str(c0.search_query),
            "slug": "collection-1",
            "title": "Collection 1",
        },
        c1.id: {
            "children": [c3.id],
            "depth": 1,
            "id": c1.id,
            "links": {
                "search": f"https://127.0.0.1:5000/api/collections/{c1.id}/records",
            },
            "num_records": 0,
            "order": c1.order,
            "search_query": str(c1.search_query),
            "slug": "collection-2",
            "title": "Collection 2",
        },
        c3.id: {
            "children": [],
            "depth": 2,
            "id": c3.id,
            "links": {
                "search": f"https://127.0.0.1:5000/api/collections/{c3.id}/records",
            },
            "num_records": 0,
            "order": c3.order,
            "search_query": str(c3.search_query),
            "slug": "collection-3",
            "title": "Collection 3",
        },
    }

    assert expected == r_dict


def test_update(app, db, add_collections, collections_service):
    """Test updating a collection."""
    collections = add_collections()
    c0 = collections[0]

    # Update by ID
    collections_service.update(
        system_identity,
        c0.id,
        data={
            "slug": "new-slug",
            "title": "Updated Title",
            "search_query": "metadata.title:updated",
        },
    )

    res = collections_service.read(
        identity=system_identity,
        id_=c0.id,
    )

    assert res.to_dict()[c0.id]["slug"] == "new-slug"
    assert res.to_dict()[c0.id]["title"] == "Updated Title"

    # Update by object
    collections_service.update(
        system_identity,
        c0,
        data={
            "slug": "new-slug-2",
            "title": "Updated Title 2",
            "search_query": "metadata.title:updated2",
        },
    )

    res = collections_service.read(
        identity=system_identity,
        id_=c0.id,
    )
    assert res.to_dict()[c0.id]["slug"] == "new-slug-2"
    assert res.to_dict()[c0.id]["title"] == "Updated Title 2"


def test_read_many(app, db, add_collections, collections_service):
    """Test reading multiple collections."""
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]

    # Read two collections
    res = collections_service.read_many(
        system_identity,
        ids_=[c0.id, c1.id],
        depth=0,
    )

    res = res.to_dict()
    assert len(res) == 2
    assert res[0]["root"] == c0.id
    assert res[1]["root"] == c1.id


def test_read_all(app, db, add_collections, collections_service):
    """Test reading all collections."""
    collections = add_collections()
    c0 = collections[0]
    c1 = collections[1]

    # Read all collections
    res = collections_service.read_all(system_identity, depth=0)

    res = res.to_dict()
    # At least our 2 collections should be in the result
    assert len(res) >= 2
    # Find our collections in the result
    collection_ids = [r["root"] for r in res]
    assert c0.id in collection_ids
    assert c1.id in collection_ids


def test_read_invalid(app, db, collections_service):
    """Test reading a non-existing collection."""
    with pytest.raises(ValueError):
        collections_service.read(
            identity=system_identity,
        )


def test_create_tree(app, db, collections_service, community):
    """Test creating a collection tree via service."""
    tree = collections_service.create_tree(
        identity=system_identity,
        namespace_id=community.id,
        data={
            "slug": "test-tree",
            "title": "Test Tree",
            "order": 1,
        },
    )

    assert tree._tree.slug == "test-tree"
    assert tree._tree.title == "Test Tree"
    assert tree._tree.order == 1
    assert str(tree._tree.namespace_id) == str(community.id)


def test_read_tree(app, db, collections_service, community):
    """Test reading a collection tree via service."""
    # Create a tree first
    tree = CollectionTree.create(
        title="Read Tree",
        slug="read-tree",
        namespace_id=community.id,
        order=1,
    )

    # Read by slug
    result = collections_service.read_tree(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="read-tree",
    )

    assert result._tree.id == tree.id
    assert result._tree.slug == "read-tree"
    assert result._tree.title == "Read Tree"


def test_update_tree(app, db, collections_service, community):
    """Test updating a collection tree via service."""
    # Create a tree first
    tree = CollectionTree.create(
        title="Original Title",
        slug="update-tree",
        namespace_id=community.id,
        order=1,
    )

    # Update the tree
    updated = collections_service.update_tree(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="update-tree",
        data={
            "title": "Updated Title",
            "slug": "update-tree",
            "order": 5,
        },
    )

    assert updated._tree.title == "Updated Title"
    assert updated._tree.order == 5


def test_delete_tree_without_cascade(app, db, collections_service, community):
    """Test deleting a tree with collections fails without cascade."""

    # Create tree and collection
    tree = CollectionTree.create(
        title="Tree to Delete",
        slug="delete-tree",
        namespace_id=community.id,
        order=1,
    )
    Collection.create(
        title="Collection in Tree",
        search_query="*:*",
        slug="collection",
        ctree=tree,
    )

    # Try to delete without cascade should fail
    with pytest.raises(CollectionTreeHasCollections):
        collections_service.delete_tree(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug="delete-tree",
            cascade=False,
        )


def test_delete_tree_with_cascade(app, db, collections_service, community):
    """Test deleting a tree with collections succeeds with cascade."""
    # Create tree and collection
    tree = CollectionTree.create(
        title="Tree to Delete",
        slug="delete-tree-cascade",
        namespace_id=community.id,
        order=1,
    )
    collection = Collection.create(
        title="Collection in Tree",
        search_query="*:*",
        slug="collection",
        ctree=tree,
    )

    # Delete with cascade should succeed
    collections_service.delete_tree(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="delete-tree-cascade",
        cascade=True,
    )

    # Verify tree and collection are deleted

    with pytest.raises(CollectionTreeNotFound):
        CollectionTree.resolve(slug="delete-tree-cascade", namespace_id=community.id)

    with pytest.raises(CollectionNotFound):
        Collection.read(id_=collection.id)


def test_list_trees(app, db, collections_service, community):
    """Test listing all trees for a community."""
    # Create multiple trees
    tree1 = CollectionTree.create(
        title="Tree 1 for List",
        slug="tree-list-1",
        namespace_id=community.id,
        order=1,
    )
    tree2 = CollectionTree.create(
        title="Tree 2 for List",
        slug="tree-list-2",
        namespace_id=community.id,
        order=2,
    )

    # List trees
    result = collections_service.list_trees(
        identity=system_identity,
        namespace_id=community.id,
    )

    trees_dict = result.to_dict()
    assert len(trees_dict) >= 2
    tree_slugs = [t["slug"] for t in trees_dict.values()]
    assert "tree-list-1" in tree_slugs
    assert "tree-list-2" in tree_slugs


def test_duplicate_collection_slug_same_tree(app, db, collections_service, community):
    """Test that duplicate collection slug in same tree raises error."""

    tree = CollectionTree.create(
        title="Duplicate Test Tree",
        slug="tree-duplicate-test",
        namespace_id=community.id,
        order=1,
    )

    # Create first collection
    collections_service.create(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug="tree-duplicate-test",
        data={
            "slug": "duplicate-slug",
            "title": "First Collection",
            "search_query": "*:*",
        },
    )

    # Try to create second collection with same slug in same tree
    with pytest.raises(DuplicateSlugError):
        collections_service.create(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug="tree-duplicate-test",
            data={
                "slug": "duplicate-slug",
                "title": "Second Collection",
                "search_query": "*:*",
            },
        )


def test_duplicate_tree_slug_same_community(app, db, collections_service, community):
    """Test that duplicate tree slug in same community raises error."""

    # Create first tree
    collections_service.create_tree(
        identity=system_identity,
        namespace_id=community.id,
        data={
            "slug": "duplicate-tree",
            "title": "First Tree",
            "order": 1,
        },
    )

    # Try to create second tree with same slug in same community
    with pytest.raises(DuplicateSlugError):
        collections_service.create_tree(
            identity=system_identity,
            namespace_id=community.id,
            data={
                "slug": "duplicate-tree",
                "title": "Second Tree",
                "order": 2,
            },
        )


def test_collection_not_found(app, db, collections_service, community):
    """Test that reading non-existent collection raises error."""

    tree = CollectionTree.create(
        title="Not Found Test Tree",
        slug="tree-not-found-test",
        namespace_id=community.id,
        order=1,
    )

    with pytest.raises(CollectionNotFound):
        collections_service.read(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug="tree-not-found-test",
            slug="non-existent",
        )


def test_collection_tree_not_found(app, db, collections_service, community):
    """Test that reading non-existent tree raises error."""

    with pytest.raises(CollectionTreeNotFound):
        collections_service.read_tree(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug="non-existent-tree",
        )


def test_delete_collection_with_children_no_cascade(
    app, db, add_collections, collections_service, community
):
    """Test that deleting collection with children fails without cascade."""

    collections = add_collections()
    parent = collections[0]  # Has children

    with pytest.raises(CollectionHasChildren):
        collections_service.delete(
            identity=system_identity,
            namespace_id=community.id,
            tree_slug=parent.collection_tree.slug,
            slug=parent.slug,
            cascade=False,
        )


def test_delete_collection_with_children_cascade(
    app, db, add_collections, collections_service, community
):
    """Test that deleting collection with children succeeds with cascade."""
    collections = add_collections()
    parent = collections[0]
    child = collections[1]
    parent_id = parent.id
    child_id = child.id

    # Delete with cascade
    collections_service.delete(
        identity=system_identity,
        namespace_id=community.id,
        tree_slug=parent.collection_tree.slug,
        slug=parent.slug,
        cascade=True,
    )

    # Verify both are deleted

    with pytest.raises(CollectionNotFound):
        Collection.read(id_=parent_id)

    with pytest.raises(CollectionNotFound):
        Collection.read(id_=child_id)
