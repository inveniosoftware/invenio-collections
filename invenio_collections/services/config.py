# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-FileCopyrightText: 2025 Northwestern University.
# SPDX-License-Identifier: MIT
"""Collections service config."""

from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_permissions.policies import BasePermissionPolicy
from invenio_records_resources.services import EndpointLink
from invenio_records_resources.services.base import ServiceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig

from ..api import Collection, CollectionTree
from .results import CollectionItem, CollectionList
from .schema import CollectionSchema, CollectionTreeSchema


class CollectionsPermissionPolicy(BasePermissionPolicy):
    """Default permission policy - allows system processes only.

    Override via ``COLLECTIONS_PERMISSION_POLICY`` configuration key.
    """

    can_read = [SystemProcess()]
    can_manage_collections = [SystemProcess()]


class CollectionServiceConfig(ServiceConfig, ConfiguratorMixin):
    """Collections service configuration."""

    result_item_cls = CollectionItem
    result_list_cls = CollectionList
    service_id = "collections"
    permission_policy_cls = FromConfig(
        "COLLECTIONS_PERMISSION_POLICY", default=CollectionsPermissionPolicy
    )
    schema = CollectionSchema
    collection_cls = Collection
    collection_tree_cls = CollectionTree
    tree_schema = CollectionTreeSchema

    links_item = {
        "search": EndpointLink(
            "collections.search_records",
            params=["id"],
            vars=lambda obj, vars: vars.update(id=obj.id),
        ),
    }
