# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections service config."""

from invenio_communities.permissions import CommunityPermissionPolicy
from invenio_records_resources.services import EndpointLink
from invenio_records_resources.services.base import ServiceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig

from .results import CollectionItem, CollectionList
from .schema import CollectionSchema


class CollectionServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Collections service configuration."""

    result_item_cls = CollectionItem
    result_list_cls = CollectionList
    service_id = "collections"
    permission_policy_cls = FromConfig(
        "COMMUNITIES_PERMISSION_POLICY", default=CommunityPermissionPolicy
    )
    schema = CollectionSchema

    links_item = {
        "search": EndpointLink(
            "collections.search_records",
            params=["id"],
            vars=lambda obj, vars: vars.update(id=obj.id),
        ),
        # So far there are no UI endpoints outside the community one.
        # When that changes, revisit this.
        "self_html": EndpointLink(
            # This perhaps illustrate the need for invenio-app-rdm to
            # be the place where this config is set/finalized, so that the core
            # of this ServiceConfig can be more generic. Alternatively,
            # bring the UI endpoint to this repo and let its template be
            # overridden in invenio-app-rdm
            "invenio_app_rdm_communities.community_collection",
            params=["pid_value", "tree_slug", "collection_slug"],
            # obj is a collection
            vars=lambda obj, vars: vars.update(
                {
                    # pid_value of the community
                    "pid_value": obj.community.slug,
                    "tree_slug": obj.collection_tree.slug,
                    "collection_slug": obj.slug,
                }
            ),
            when=lambda coll, ctx: coll.community,
        ),
    }
