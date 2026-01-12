# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service."""

import os

from flask import current_app, url_for
from invenio_communities.communities.records.api import Community
from invenio_db.uow import ModelDeleteOp
from invenio_rdm_records.proxies import current_community_records_service
from invenio_records_resources.services import (
    LinksTemplate,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.uow import ModelCommitOp, unit_of_work
from invenio_search.engine import dsl
from sqlalchemy.exc import IntegrityError

from ..api import Collection, CollectionTree
from ..errors import (
    CollectionHasChildren,
    CollectionTreeHasCollections,
    DuplicateSlugError,
    LogoNotFoundError,
)
from .results import (
    CollectionItem,
    CollectionList,
    CollectionTreeItem,
    CollectionTreeList,
)
from .schema import validate_search_query


class CollectionsService(Service):
    """Collections service."""

    def __init__(self, config):
        """Instantiate the service with the given config."""
        self.config = config

    collection_cls = Collection

    def _resolve_community_id(self, community_id):
        """Resolve community slug or UUID to UUID string.

        Args:
            community_id: Either a community slug (string) or UUID (string/UUID object)

        Returns:
            str: The community UUID as a string
        """
        if not community_id:
            return None

        # Resolve using Community.pid system field
        community = Community.pid.resolve(community_id)
        return str(community.id)

    def _resolve_tree_and_community(
        self, tree_id=None, tree_slug=None, community_id=None
    ):
        """Resolve tree and community ID.

        Resolves the collection tree using either tree_id or tree_slug+community_id.
        If community_id is not provided, it will be extracted from the resolved tree.

        Args:
            tree_id: The tree ID (optional).
            tree_slug: The tree slug (optional).
            community_id: The community ID (optional).

        Returns:
            tuple: (tree, community_id) where community_id is guaranteed to be resolved
        """
        if community_id:
            community_id = self._resolve_community_id(community_id)

        ctree = self.collection_tree_cls.resolve(
            id_=tree_id, slug=tree_slug, community_id=community_id
        )

        # Get community_id from tree if not provided
        if not community_id and ctree.community:
            community_id = str(ctree.community.id)

        return ctree, community_id

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
        community_id=None,
        tree_slug=None,
        tree_id=None,
        uow=None,
        **kwargs,
    ):
        """Create a new collection.

        The created collection will be added to the collection tree as a root collection (no parent).
        If a parent is needed, use the ``add`` method.

        Args:
            identity: The identity of the user.
            data: The collection data.
            community_id: The community ID (required if using tree_slug).
            tree_slug: The tree slug (either this or tree_id is required).
            tree_id: The tree ID (either this or tree_slug is required).
            uow: Unit of work instance.
        """
        if not tree_slug and not tree_id:
            raise ValueError("Either tree_slug or tree_id must be provided")

        ctree, community_id = self._resolve_tree_and_community(
            tree_id=tree_id, tree_slug=tree_slug, community_id=community_id
        )

        self.require_permission(identity, "update", community_id=community_id)

        data, _ = self.collection_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )

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
        community_id=None,
        tree_slug=None,
        tree_id=None,
        depth=2,
        **kwargs,
    ):
        """Get a collection by ID or slug.

        To resolve by slug, either tree_id or tree_slug+community_id must be provided.

        Args:
            identity: The identity of the user.
            id_: The collection ID.
            slug: The collection slug.
            community_id: The community ID (required if using tree_slug).
            tree_slug: The tree slug.
            tree_id: The tree ID.
            depth: Maximum depth for fetching nested collections (default: 2).
        """
        if community_id:
            community_id = self._resolve_community_id(community_id)

        if id_:
            collection = self.collection_cls.read(id_=id_, depth=depth)
        elif slug and (tree_slug or tree_id):
            ctree = CollectionTree.resolve(
                id_=tree_id, slug=tree_slug, community_id=community_id
            )
            collection = self.collection_cls.read(
                slug=slug, ctree_id=ctree.id, depth=depth
            )
        else:
            raise ValueError(
                "Either id_ or slug with (tree_id or tree_slug+community_id) must be provided."
            )

        if collection.community:
            self.require_permission(
                identity, "read", community_id=collection.community.id
            )

        return CollectionItem(
            identity,
            collection,
            self.collection_schema,
            self.links_item_tpl,
        )

    def list_trees(self, identity, community_id, **kwargs):
        """Get the trees of a community.

        Args:
            identity: The identity of the user.
            community_id: The community ID (required).
        """
        self.require_permission(identity, "read", community_id=community_id)

        community_id = self._resolve_community_id(community_id)

        if not community_id:
            raise ValueError("Community ID must be provided.")
        res = CollectionTree.get_community_trees(community_id, **kwargs)
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
        community_id=None,
        tree_slug=None,
        tree_id=None,
        uow=None,
        **kwargs,
    ):
        """Add a subcollection to a collection.

        Args:
            identity: The identity of the user.
            slug: The parent collection slug (required).
            data: The new subcollection data (required).
            community_id: The community ID (required if using tree_slug).
            tree_slug: The tree slug (either this or tree_id is required).
            tree_id: The tree ID (either this or tree_slug is required).
            uow: Unit of work instance.
        """
        if not tree_slug and not tree_id:
            raise ValueError("Either tree_slug or tree_id must be provided")

        ctree, community_id = self._resolve_tree_and_community(
            tree_id=tree_id, tree_slug=tree_slug, community_id=community_id
        )

        self.require_permission(identity, "update", community_id=community_id)

        data, _ = self.collection_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )

        collection = self.collection_cls.read(slug=slug, ctree_id=ctree.id)

        new_collection = self.collection_cls.create(parent=collection, **data, **kwargs)

        uow.register(ModelCommitOp(new_collection.model))

        return CollectionItem(
            identity, new_collection, self.collection_schema, self.links_item_tpl
        )

    @unit_of_work()
    def update(self, identity, collection_or_id, data=None, uow=None):
        """Update a collection.

        Args:
            identity: The identity of the user.
            collection_or_id: The collection object or ID (required).
            data: The updated collection data.
            uow: Unit of work instance.
        """
        if isinstance(collection_or_id, int):
            collection = self.collection_cls.read(id_=collection_or_id)
        else:
            collection = collection_or_id
        self.require_permission(
            identity, "update", community_id=collection.community.id
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
        community_id=None,
        ctree_id=None,
        cascade=False,
        uow=None,
    ):
        """Delete a collection.

        Args:
            identity: The identity of the user.
            slug: The collection slug (required).
            tree_slug: The tree slug (either this or ctree_id required).
            community_id: The community ID (required if using tree_slug).
            ctree_id: The tree ID (either this or tree_slug+community_id required).
            cascade: Whether to delete child collections (default: False).
            uow: Unit of work instance.
        """
        ctree, community_id = self._resolve_tree_and_community(
            tree_id=ctree_id, tree_slug=tree_slug, community_id=community_id
        )

        self.require_permission(identity, "update", community_id=community_id)

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

        if collection.community:
            res = current_community_records_service.search(
                identity,
                community_id=collection.community.id,
                extra_filter=collection.query,
                params=params,
            )
        else:
            raise NotImplementedError(
                "Search for collections without community not supported."
            )
        return res

    def search_test_collection_records(
        self,
        identity,
        tree_slug,
        community_id,
        slug=None,
        data=None,
        params=None,
    ):
        """Search records for a new collection. Either with parent collections or not.

        Args:
            identity: The identity of the user.
            tree_slug: The tree slug (required).
            community_id: The community ID (required).
            slug: The collection slug (optional, for testing with existing collection).
            data: Additional data containing search_query (optional).
            params: Search parameters (optional).
        """
        if not tree_slug:
            raise ValueError("tree_slug is required")
        if not community_id:
            raise ValueError("community_id is required")

        self.require_permission(identity, "read", community_id=community_id)

        community_id = self._resolve_community_id(community_id)

        search_query = data.get("search_query") if data else None

        if search_query:
            validate_search_query(search_query)

        ctree = self.collection_tree_cls.resolve(
            slug=tree_slug, community_id=community_id
        )

        if slug:
            collection = self.collection_cls.read(slug=slug, ctree_id=ctree.id)
            if search_query:
                new_search_query = collection.add_test_query(search_query)
            else:
                # No additional query, use collection's existing query
                new_search_query = collection.query
        else:
            if search_query:
                new_search_query = dsl.Q("query_string", query=search_query)
            else:
                # No query at all, return all records in community
                new_search_query = None

        params = params or {}

        if ctree.community:
            res = current_community_records_service.search(
                identity,
                community_id=ctree.community.id,
                extra_filter=new_search_query,
                params=params,
            )
        else:
            raise NotImplementedError(
                "Search for collections without community not supported."
            )

        return res

    def read_tree(
        self, identity, community_id=None, tree_slug=None, ctree_id=None, depth=2
    ):
        """Read a collection tree.

        Args:
            identity: The identity of the user.
            community_id: The community ID (required if using tree_slug).
            tree_slug: The tree slug (either this or ctree_id required).
            ctree_id: The tree ID (either this or tree_slug required).
            depth: Maximum depth for fetching nested collections (default: 2).
        """
        if community_id:
            community_id = self._resolve_community_id(community_id)

        ctree = self.collection_tree_cls.resolve(
            community_id=community_id, slug=tree_slug, id_=ctree_id, depth=depth
        )

        # Get community_id from tree if not provided
        if not community_id and ctree.community:
            community_id = str(ctree.community.id)

        self.require_permission(identity, "read", community_id=community_id)

        return CollectionTreeItem(
            identity,
            ctree,
            self.links_item_tpl,
            self.collection_tree_schema,
            self.collection_schema,
        )

    @unit_of_work()
    def create_tree(self, identity, data, community_id, uow=None):
        """Create new collection tree.

        Args:
            identity: The identity of the user.
            data: The collection tree data.
            community_id: The community ID (required).
            uow: Unit of work instance.
        """
        if not community_id:
            raise ValueError("community_id is required")

        self.require_permission(identity, "update", community_id=community_id)

        community_id = self._resolve_community_id(community_id)

        valid_data, errors = self.collection_tree_schema.load(
            data, context={"identity": identity}, raise_errors=True
        )

        item = self.collection_tree_cls.create(community_id=community_id, **valid_data)
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
        self, identity, data, tree_slug=None, tree_id=None, community_id=None, uow=None
    ):
        """Update a collection tree.

        Args:
            identity: The identity of the user.
            data: The collection tree data to update.
            tree_slug: The slug of the tree to update.
            tree_id: The ID of the tree to update.
            community_id: The community ID (required if using tree_slug).
            uow: Unit of work instance.
        """
        if not tree_slug and not tree_id:
            raise ValueError("Either tree_slug or tree_id must be provided")

        ctree, community_id = self._resolve_tree_and_community(
            tree_id=tree_id, tree_slug=tree_slug, community_id=community_id
        )

        self.require_permission(identity, "update", community_id=community_id)

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
        community_id=None,
        ctree_id=None,
        cascade=False,
        uow=None,
    ):
        """Delete a collection tree.

        Args:
            identity: The identity of the user.
            tree_slug: The tree slug (either this or ctree_id required).
            community_id: The community ID (required if using tree_slug).
            ctree_id: The tree ID (either this or tree_slug+community_id required).
            cascade: Whether to delete all collections in tree (default: False).
            uow: Unit of work instance.
        """
        ctree, community_id = self._resolve_tree_and_community(
            tree_id=ctree_id, tree_slug=tree_slug, community_id=community_id
        )

        self.require_permission(identity, "update", community_id=community_id)

        if ctree.collections:
            if not cascade:
                raise CollectionTreeHasCollections()

            ctree.delete_all_collections()

        uow.register(ModelDeleteOp(ctree.model))

        return True
