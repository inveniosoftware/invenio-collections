# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collection resource."""

from flask import g
from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_search_args,
    request_view_args,
)


class CollectionsResource(ErrorHandlersMixin, Resource):
    """Collection resource."""

    def __init__(self, config, service):
        """Instantiate the resource."""
        super().__init__(config)
        self.service = service

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            route("GET", routes["search-records"], self.search_records),
            route("GET", routes["list-collection-trees"], self.list_trees),
            route("GET", routes["tree-item"], self.read_tree),
            route("POST", routes["list-collection-trees"], self.create_tree),
            route("PUT", routes["tree-item"], self.update_tree),
            route("DELETE", routes["tree-item"], self.delete_tree),
            route("POST", routes["list-tree-collections"], self.create),
            route(
                "POST",
                routes["list-tree-collections-test-records"],
                self.search_base_test_records,
            ),
            route("GET", routes["collection-item"], self.read),
            route("POST", routes["collection-item"], self.add),
            route("PUT", routes["collection-item"], self.update),
            route("DELETE", routes["collection-item"], self.delete),
            route("GET", routes["collection-records"], self.search_records_by_slug),
        ]

    @request_view_args
    @request_search_args
    @response_handler(many=True)
    def search_records(self):
        """Search records in a collection."""
        id_ = resource_requestctx.view_args["id"]
        records = self.service.search_collection_records(
            g.identity,
            id_,
            params=resource_requestctx.args,
        )
        return records.to_dict(), 200

    @request_data
    @request_view_args
    @request_extra_args
    @response_handler()
    def create(self):
        """Create a new community collection."""
        item = self.service.create(
            identity=g.identity,
            data=resource_requestctx.data or {},
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            tree_id=resource_requestctx.args.get("tree_id"),
        )
        return item.to_dict(), 201

    @request_extra_args
    @request_view_args
    @response_handler()
    def read(self):
        """Read a community collection."""
        item = self.service.read(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            slug=resource_requestctx.view_args["col_slug"],
            depth=resource_requestctx.args.get("depth", 2),
            tree_id=resource_requestctx.args.get("tree_id"),
        )
        return item.to_dict(), 200

    @request_data
    @request_view_args
    @request_extra_args
    @response_handler()
    def add(self):
        """Add a new community collection under an existing one."""
        item = self.service.add(
            identity=g.identity,
            slug=resource_requestctx.view_args["col_slug"],
            data=resource_requestctx.data or {},
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            tree_id=resource_requestctx.args.get("tree_id"),
        )
        return item.to_dict(), 201

    @request_data
    @request_view_args
    @response_handler()
    def update(self):
        """Update community collection."""
        collection = self.service.read(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            slug=resource_requestctx.view_args["col_slug"],
        )
        item = self.service.update(
            identity=g.identity,
            collection_or_id=collection._collection,
            data=resource_requestctx.data or {},
        )
        return item.to_dict(), 200

    @request_extra_args
    @request_view_args
    def delete(self):
        """Delete community collection."""
        self.service.delete(
            g.identity,
            slug=resource_requestctx.view_args["col_slug"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            community_id=resource_requestctx.view_args["pid_value"],
            ctree_id=resource_requestctx.args.get("tree_id"),
            cascade=resource_requestctx.args.get("cascade", False),
        )
        return "", 204

    @request_view_args
    @request_search_args
    @response_handler(many=True)
    def search_records_by_slug(self):
        """Search records in a collection by slug."""
        collection = self.service.read(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            slug=resource_requestctx.view_args["col_slug"],
        )
        records = self.service.search_collection_records(
            g.identity, collection._collection, params=resource_requestctx.args
        )
        return records.to_dict(), 200

    def _reduced_search_output(self, result):
        """Reduce search output for testing."""
        output = {"hits": {"hits": [], "total": result["hits"]["total"]}}
        output_hits = output["hits"]["hits"]
        for hit in result.get("hits", {}).get("hits", [])[:5]:
            metadata = hit.get("metadata", {})
            item = {
                "metadata": {
                    "resource_type": metadata.get("resource_type"),
                    "title": metadata.get("title"),
                    "description": metadata.get("description"),
                    "creators": metadata.get("creators"),
                },
            }
            output_hits.append(item)
        return output

    @request_data
    @request_view_args
    @request_search_args
    @response_handler(many=True)
    def search_base_test_records(self):
        """Search records for a collection tree with or without existing collections and new search query."""
        # Extract test_col_slug and tree_id from args before passing to service
        args_dict = dict(resource_requestctx.args) if resource_requestctx.args else {}
        test_col_slug = args_dict.pop("test_col_slug", None)
        tree_id = args_dict.pop("tree_id", None)

        records = self.service.search_test_collection_records(
            g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            slug=test_col_slug,
            data=resource_requestctx.data or {},
            params=args_dict,
        )
        return self._reduced_search_output(records.to_dict()), 200

    @request_data
    @request_view_args
    @response_handler()
    def create_tree(self):
        """Create a new community collection tree."""
        item = self.service.create_tree(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            data=resource_requestctx.data or {},
        )
        return item.to_dict(), 201

    @request_extra_args
    @request_view_args
    @response_handler()
    def read_tree(self):
        """Read one particular tree."""
        item = self.service.read_tree(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            depth=resource_requestctx.args.get("depth", 2),
            ctree_id=resource_requestctx.args.get("tree_id"),
        )
        return item.to_dict(), 200

    @request_view_args
    @request_data
    @request_extra_args
    @response_handler()
    def update_tree(self):
        """Update a community tree."""
        item = self.service.update_tree(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            data=resource_requestctx.data,
            tree_id=resource_requestctx.args.get("tree_id"),
        )
        return item.to_dict(), 200

    @request_extra_args
    @request_view_args
    def delete_tree(self):
        """Delete a community tree."""
        self.service.delete_tree(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            tree_slug=resource_requestctx.view_args["tree_slug"],
            ctree_id=resource_requestctx.args.get("tree_id"),
            cascade=resource_requestctx.args.get("cascade", False),
        )
        return "", 204

    @request_extra_args
    @request_view_args
    @response_handler(many=True)
    def list_trees(self):
        """List collections for a community."""
        result = self.service.list_trees(
            identity=g.identity,
            community_id=resource_requestctx.view_args["pid_value"],
            depth=resource_requestctx.args.get("depth", 2),
        )
        return result.to_dict(), 200
