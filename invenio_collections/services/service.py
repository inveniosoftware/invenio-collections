# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service."""

import os

from flask import current_app, url_for
from invenio_db import db
from invenio_db.uow import ModelDeleteOp
from invenio_rdm_records.proxies import current_community_records_service
from invenio_records_resources.services import (
    LinksTemplate,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import ModelCommitOp, unit_of_work
from invenio_search.engine import dsl
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from ..api import Collection, CollectionTree
from ..errors import (
    CollectionHasChildren,
    CollectionNotFound,
    CollectionTreeHasCollections,
    CollectionTreeNotFound,
    DuplicateSlugError,
    LogoNotFoundError,
    MaxCollectionsExceeded,
    MaxDepthExceeded,
    MaxTreesExceeded,
)
from .results import (
    CollectionItem,
    CollectionList,
    CollectionSearchPreview,
    CollectionTreeItem,
    CollectionTreeList,
)
from .schema import BatchReorderSchema, validate_search_query


class CollectionsService(Service):
    """Collections service."""

    def __init__(self, config):
        """Instantiate the service with the given config."""
        self.config = config

    collection_cls = Collection

    def _resolve_tree(self, tree_id=None, tree_slug=None, namespace_id=None):
        """Resolve tree and namespace ID, returning (tree, namespace_id)."""
        if namespace_id:
            namespace_id = str(namespace_id)

        ctree = self.collection_tree_cls.resolve(
            id_=tree_id, slug=tree_slug, namespace_id=namespace_id
        )

        if not namespace_id and ctree.namespace_id:
            namespace_id = str(ctree.namespace_id)

        return ctree, namespace_id

    def _validate_tree_limit(self, namespace_id):
        """Raise MaxTreesExceeded if adding a new tree would exceed the configured limit."""
        max_trees = current_app.config["COLLECTIONS_MAX_TREES"]

        # 0 means unlimited
        if max_trees == 0:
            return

        # Count existing trees for this namespace
        current_count = (
            db.session.query(func.count(CollectionTree.model_cls.id))
            .filter(CollectionTree.model_cls.namespace_id == namespace_id)
            .scalar()
        )

        if current_count >= max_trees:
            raise MaxTreesExceeded(current_count, max_trees)

    def _validate_collection_limit(self, tree_id):
        """Raise MaxCollectionsExceeded if adding a collection would exceed the configured limit."""
        max_collections = current_app.config["COLLECTIONS_MAX_COLLECTIONS_PER_TREE"]

        # 0 means unlimited
        if max_collections == 0:
            return

        # Count existing collections in this tree
        current_count = (
            db.session.query(func.count(Collection.model_cls.id))
            .filter(Collection.model_cls.tree_id == tree_id)
            .scalar()
        )

        if current_count >= max_collections:
            raise MaxCollectionsExceeded(current_count, max_collections)

    @property
    def collection_schema(self):
        """Get the collection schema."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def collection_tree_cls(self):
        """Factory for creating a collection tree class."""
        return self.config.collection_tree_cls

    @property
    def collection_tree_schema(self):
        """Get the collection tree schema."""
        return ServiceSchemaWrapper(self, schema=self.config.tree_schema)

    @property
    def links_item_tpl(self):
        """Get the item links template."""
        return LinksTemplate(
            links=self.config.links_item,
            context={
                "permission_policy_cls": self.config.permission_policy_cls,
            },
        )

    @unit_of_work()
    def create(
        self,
        identity,
        data,
        namespace_id=None,
        tree_slug=None,
        tree_id=None,
        uow=None,
        **kwargs,
    ):
        """Create a new root collection in the given tree.

        To add a subcollection, use the ``add`` method instead.
        """
        if not tree_slug and not tree_id:
            raise ValueError("Either tree_slug or tree_id must be provided")

        ctree, namespace_id = self._resolve_tree(
            tree_id=tree_id, tree_slug=tree_slug, namespace_id=namespace_id
        )

        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        # Validate collection limit
        self._validate_collection_limit(ctree.id)

        data, _ = self.collection_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )

        # Auto-calculate order if not provided
        if data.get("order") is None:
            # Get max order for root collections in this tree
            max_order = (
                db.session.query(func.max(Collection.model_cls.order))
                .filter(
                    Collection.model_cls.tree_id == ctree.id,
                    Collection.model_cls.path == ",",  # Root collections only
                )
                .scalar()
            )
            # Gap of 10 leaves room to insert items between existing ones
            # without requiring a full reorder of all siblings.
            data["order"] = (max_order or 0) + 10

        collection = self.collection_cls.create(ctree=ctree, **data, **kwargs)

        uow.register(ModelCommitOp(collection.model))

        return CollectionItem(
            identity, collection, self.collection_schema, self.links_item_tpl
        )

    def read(
        self,
        identity=None,
        *,
        id_=None,
        slug=None,
        namespace_id=None,
        tree_slug=None,
        tree_id=None,
        depth=2,
        **kwargs,
    ):
        """Get a collection by ID or slug.

        To resolve by slug, either tree_id or tree_slug+namespace_id must be provided.
        """
        if namespace_id:
            namespace_id = str(namespace_id)

        if id_:
            collection = self.collection_cls.read(id_=id_, depth=depth)
        elif slug and (tree_slug or tree_id):
            ctree = CollectionTree.resolve(
                id_=tree_id, slug=tree_slug, namespace_id=namespace_id
            )
            collection = self.collection_cls.read(
                slug=slug, ctree_id=ctree.id, depth=depth
            )
        else:
            raise ValueError(
                "Either id_ or slug with (tree_id or tree_slug+namespace_id) must be provided."
            )

        tree_namespace_id = collection.collection_tree.namespace_id
        if tree_namespace_id:
            self.require_permission(
                identity, "read", namespace_id=str(tree_namespace_id)
            )

        return CollectionItem(
            identity,
            collection,
            self.collection_schema,
            self.links_item_tpl,
        )

    def list_trees(self, identity, namespace_id, **kwargs):
        """Get all collection trees for a namespace."""
        self.require_permission(identity, "read", namespace_id=namespace_id)

        namespace_id = str(namespace_id)

        if not namespace_id:
            raise ValueError("Namespace ID must be provided.")
        res = CollectionTree.get_namespace_trees(namespace_id, **kwargs)
        return CollectionTreeList(
            identity,
            res,
            self.links_item_tpl,
            self.collection_tree_schema,
            self.collection_schema,
        )

    @unit_of_work()
    def add(
        self,
        identity,
        slug,
        data,
        namespace_id=None,
        tree_slug=None,
        tree_id=None,
        uow=None,
        **kwargs,
    ):
        """Add a subcollection under the collection identified by ``slug``."""
        if not tree_slug and not tree_id:
            raise ValueError("Either tree_slug or tree_id must be provided")

        ctree, namespace_id = self._resolve_tree(
            tree_id=tree_id, tree_slug=tree_slug, namespace_id=namespace_id
        )

        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        # Validate collection limit
        self._validate_collection_limit(ctree.id)

        data, _ = self.collection_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )

        collection = self.collection_cls.read(slug=slug, ctree_id=ctree.id)

        # Validate depth limit
        max_depth = current_app.config.get("COLLECTIONS_MAX_DEPTH", 1)
        if collection.depth >= max_depth:
            raise MaxDepthExceeded(collection.depth, max_depth)

        # Auto-calculate order if not provided
        if data.get("order") is None:
            # Get max order for children of this parent
            parent_path = f"{collection.path}{collection.id},"
            max_order = (
                db.session.query(func.max(Collection.model_cls.order))
                .filter(
                    Collection.model_cls.tree_id == ctree.id,
                    Collection.model_cls.path == parent_path,
                )
                .scalar()
            )
            # Gap of 10 leaves room to insert items between existing ones
            # without requiring a full reorder of all siblings.
            data["order"] = (max_order or 0) + 10

        new_collection = self.collection_cls.create(parent=collection, **data, **kwargs)

        uow.register(ModelCommitOp(new_collection.model))

        return CollectionItem(
            identity, new_collection, self.collection_schema, self.links_item_tpl
        )

    @unit_of_work()
    def update(
        self,
        identity,
        collection_or_id=None,
        data=None,
        slug=None,
        tree_slug=None,
        namespace_id=None,
        uow=None,
    ):
        """Update a collection."""
        if collection_or_id is not None:
            if isinstance(collection_or_id, int):
                collection = self.collection_cls.read(id_=collection_or_id)
            else:
                collection = collection_or_id
        elif slug and tree_slug:
            ctree, namespace_id = self._resolve_tree(
                tree_slug=tree_slug, namespace_id=namespace_id
            )
            collection = self.collection_cls.read(slug=slug, ctree_id=ctree.id)
        else:
            raise ValueError(
                "Either collection_or_id or slug+tree_slug must be provided."
            )

        # Resolve namespace for permission check
        namespace_id = (
            str(collection.collection_tree.namespace_id)
            if collection.collection_tree.namespace_id
            else None
        )
        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        data = data or {}

        valid_data, errors = self.collection_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )

        res = collection.update(**valid_data)

        uow.register(ModelCommitOp(res.model))

        return CollectionItem(
            identity, collection, self.collection_schema, self.links_item_tpl
        )

    @unit_of_work()
    def delete(
        self,
        identity,
        slug,
        tree_slug=None,
        namespace_id=None,
        ctree_id=None,
        cascade=False,
        uow=None,
    ):
        """Delete a collection, optionally cascading to its direct children."""
        ctree, namespace_id = self._resolve_tree(
            tree_id=ctree_id, tree_slug=tree_slug, namespace_id=namespace_id
        )

        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        collection = self.collection_cls.read(slug=slug, ctree_id=ctree.id)

        if collection.children:
            if not cascade:
                raise CollectionHasChildren()

            for child in collection.children:
                uow.register(ModelDeleteOp(child.model))

        uow.register(ModelDeleteOp(collection.model))

        return True

    def read_logo(self, identity, slug):
        """Read a collection logo.

        TODO: implement logos as files in the database. For now, we just check if the file exists as a static file.
        """
        logo_path = f"images/collections/{slug}.jpg"
        _exists = os.path.exists(os.path.join(current_app.static_folder, logo_path))
        if _exists:
            return url_for("static", filename=logo_path)
        raise LogoNotFoundError()

    def read_many(self, identity, ids_, depth=2):
        """Get many collections.

        Args:
            identity: The identity of the user.
            ids_: List of collection IDs (required).
            depth: Maximum depth for fetching nested collections (default: 2).
        """
        self.require_permission(identity, "read")

        if ids_ is None:
            raise ValueError("IDs must be provided.")

        if ids_ == []:
            raise ValueError("Use read_all to get all collections.")

        res = self.collection_cls.read_many(ids_, depth=depth)
        return CollectionList(
            identity, res, self.collection_schema, None, self.links_item_tpl
        )

    def read_all(self, identity, depth=2):
        """Get all collections.

        Args:
            identity: The identity of the user.
            depth: Maximum depth for fetching nested collections (default: 2).
        """
        self.require_permission(identity, "read")
        res = self.collection_cls.read_all(depth=depth)
        return CollectionList(
            identity, res, self.collection_schema, None, self.links_item_tpl
        )

    def search_collection_records(self, identity, collection_or_id, params=None):
        """Search records in a collection.

        Args:
            identity: The identity of the user.
            collection_or_id: The collection object or ID (required).
            params: Additional search parameters.
        """
        params = params or {}

        if isinstance(collection_or_id, int):
            collection = self.collection_cls.read(id_=collection_or_id)
        else:
            collection = collection_or_id

        collection_namespace_id = collection.collection_tree.namespace_id
        if collection_namespace_id:
            res = current_community_records_service.search(
                identity,
                community_id=str(collection_namespace_id),
                extra_filter=collection.query,
                params=params,
            )
        else:
            raise NotImplementedError(
                "Search for collections without namespace not supported."
            )
        return res

    def preview_collection_records(
        self,
        identity,
        tree_slug,
        namespace_id,
        slug=None,
        data=None,
        params=None,
    ):
        """Search records for a new collection. Either with parent collections or not.

        Args:
            identity: The identity of the user.
            tree_slug: The tree slug (required).
            namespace_id: The namespace UUID (required).
            slug: The collection slug (optional, for testing with existing collection).
            data: Additional data containing search_query (optional).
            params: Search parameters (optional).
        """
        if not tree_slug:
            raise ValueError("tree_slug is required")
        if not namespace_id:
            raise ValueError("namespace_id is required")

        self.require_permission(identity, "read", namespace_id=namespace_id)

        namespace_id = str(namespace_id)

        search_query = data.get("search_query") if data else None

        if search_query:
            validate_search_query(search_query)

        ctree = self.collection_tree_cls.resolve(
            slug=tree_slug, namespace_id=namespace_id
        )

        if slug:
            collection = self.collection_cls.read(slug=slug, ctree_id=ctree.id)
            if search_query:
                new_search_query = collection.extend_query(search_query)
            else:
                # No additional query, use collection's existing query
                new_search_query = collection.query
        else:
            if search_query:
                new_search_query = dsl.Q("query_string", query=search_query)
            else:
                # No query at all, return all records in namespace
                new_search_query = None

        params = params or {}

        if ctree.namespace_id:
            res = current_community_records_service.search(
                identity,
                community_id=str(ctree.namespace_id),
                extra_filter=new_search_query,
                params=params,
            )
        else:
            raise NotImplementedError(
                "Search for collections without namespace not supported."
            )

        return CollectionSearchPreview(res)

    def read_tree(
        self, identity, namespace_id=None, tree_slug=None, ctree_id=None, depth=2
    ):
        """Read a collection tree.

        Args:
            identity: The identity of the user.
            namespace_id: The namespace UUID (required if using tree_slug).
            tree_slug: The tree slug (either this or ctree_id required).
            ctree_id: The tree ID (either this or tree_slug required).
            depth: Maximum depth for fetching nested collections (default: 2).
        """
        if namespace_id:
            namespace_id = str(namespace_id)

        ctree = self.collection_tree_cls.resolve(
            namespace_id=namespace_id, slug=tree_slug, id_=ctree_id, depth=depth
        )

        # Get namespace_id from tree if not provided
        if not namespace_id and ctree.namespace_id:
            namespace_id = str(ctree.namespace_id)

        self.require_permission(identity, "read", namespace_id=namespace_id)

        return CollectionTreeItem(
            identity,
            ctree,
            self.links_item_tpl,
            self.collection_tree_schema,
            self.collection_schema,
        )

    @unit_of_work()
    def create_tree(self, identity, data, namespace_id, uow=None):
        """Create new collection tree.

        Args:
            identity: The identity of the user.
            data: The collection tree data.
            namespace_id: The namespace UUID (required).
            uow: Unit of work instance.
        """
        if not namespace_id:
            raise ValueError("namespace_id is required")

        namespace_id = str(namespace_id)

        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        # Validate tree limit
        self._validate_tree_limit(namespace_id)

        valid_data, errors = self.collection_tree_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )

        # Auto-calculate order if not provided
        if valid_data.get("order") is None:
            # Get max order for trees in this namespace
            max_order = (
                db.session.query(func.max(CollectionTree.model_cls.order))
                .filter(CollectionTree.model_cls.namespace_id == namespace_id)
                .scalar()
            )
            # Gap of 10 leaves room to insert items between existing ones
            # without requiring a full reorder of all siblings.
            valid_data["order"] = (max_order or 0) + 10

        item = self.collection_tree_cls.create(namespace_id=namespace_id, **valid_data)
        uow.register(ModelCommitOp(item.model))

        return CollectionTreeItem(
            identity,
            item,
            self.links_item_tpl,
            self.collection_tree_schema,
            self.collection_schema,
        )

    @unit_of_work()
    def update_tree(
        self, identity, data, tree_slug=None, tree_id=None, namespace_id=None, uow=None
    ):
        """Update a collection tree.

        Args:
            identity: The identity of the user.
            data: The collection tree data to update.
            tree_slug: The slug of the tree to update.
            tree_id: The ID of the tree to update.
            namespace_id: The namespace UUID (required if using tree_slug).
            uow: Unit of work instance.
        """
        if not tree_slug and not tree_id:
            raise ValueError("Either tree_slug or tree_id must be provided")

        ctree, namespace_id = self._resolve_tree(
            tree_id=tree_id, tree_slug=tree_slug, namespace_id=namespace_id
        )

        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        valid_data, errors = self.collection_tree_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )
        item = ctree.update(**valid_data)

        uow.register(ModelCommitOp(item.model))

        return CollectionTreeItem(
            identity,
            item,
            self.links_item_tpl,
            self.collection_tree_schema,
            self.collection_schema,
        )

    @unit_of_work()
    def delete_tree(
        self,
        identity,
        tree_slug=None,
        namespace_id=None,
        ctree_id=None,
        cascade=False,
        uow=None,
    ):
        """Delete a collection tree.

        Args:
            identity: The identity of the user.
            tree_slug: The tree slug (either this or ctree_id required).
            namespace_id: The namespace UUID (required if using tree_slug).
            ctree_id: The tree ID (either this or tree_slug+namespace_id required).
            cascade: Whether to delete all collections in tree (default: False).
            uow: Unit of work instance.
        """
        ctree, namespace_id = self._resolve_tree(
            tree_id=ctree_id, tree_slug=tree_slug, namespace_id=namespace_id
        )

        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        if ctree.collections:
            if not cascade:
                raise CollectionTreeHasCollections()

            ctree.delete_all_collections()

        uow.register(ModelDeleteOp(ctree.model))

        return True

    @unit_of_work()
    def reorder_trees(self, identity, namespace_id, data, uow=None):
        """Batch reorder collection trees.

        Args:
            identity: The identity of the user.
            namespace_id: The namespace UUID (required).
            data: The reorder data containing list of {slug, order} items.
            uow: Unit of work instance.

        Returns:
            dict: Response with updated count and items list.
        """
        namespace_id = str(namespace_id)

        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        # Validate schema
        valid_data = BatchReorderSchema().load(data)

        # Update in transaction
        updated = []
        for item in valid_data["order"]:
            tree_model = self.collection_tree_cls.model_cls.get_by_slug(
                item["slug"], namespace_id
            )

            if not tree_model:
                raise CollectionTreeNotFound(
                    f"Collection tree '{item['slug']}' not found"
                )

            tree = self.collection_tree_cls(tree_model)
            tree.update(order=item["order"])
            updated.append(tree)

        # Register all updated trees
        for tree in updated:
            uow.register(ModelCommitOp(tree.model))

        # Return response
        return {
            "updated": len(updated),
            "items": [
                {
                    "slug": tree.slug,
                    "title": tree.title,
                    "order": tree.order,
                    "id": tree.id,
                    "namespace_id": str(tree.namespace_id),
                }
                for tree in updated
            ],
        }

    @unit_of_work()
    def reorder_collections(self, identity, namespace_id, tree_slug, data, uow=None):
        """Batch reorder collections within a tree.

        Args:
            identity: The identity of the user.
            namespace_id: The namespace UUID (required).
            tree_slug: The tree slug (required).
            data: The reorder data containing list of {slug, order} items.
            uow: Unit of work instance.

        Returns:
            dict: Response with updated count and items list.
        """
        namespace_id = str(namespace_id)

        self.require_permission(
            identity, "manage_collections", namespace_id=namespace_id
        )

        # Validate tree exists and get it as API object
        try:
            ctree = self.collection_tree_cls.resolve(
                slug=tree_slug, namespace_id=namespace_id
            )
        except CollectionTreeNotFound:
            raise CollectionTreeNotFound(f"Collection tree '{tree_slug}' not found")

        # Validate schema
        valid_data = BatchReorderSchema().load(data)

        # Update in transaction
        updated = []
        for item in valid_data["order"]:
            collection_model = Collection.model_cls.get_by_slug(item["slug"], ctree.id)

            if not collection_model:
                raise CollectionNotFound(f"Collection '{item['slug']}' not found")

            collection = Collection(collection_model)
            collection.update(order=item["order"])
            updated.append(collection)

        # Register all updated collections
        for collection in updated:
            uow.register(ModelCommitOp(collection.model))

        # Return response
        return {
            "updated": len(updated),
            "items": [
                {
                    "slug": collection.slug,
                    "title": collection.title,
                    "order": collection.order,
                    "id": collection.id,
                }
                for collection in updated
            ],
        }
