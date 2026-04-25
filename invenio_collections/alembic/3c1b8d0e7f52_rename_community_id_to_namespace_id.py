#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Drop community FK and rename community_id to namespace_id in collection tree."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "3c1b8d0e7f52"
down_revision = "d2f434c0ac92"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    #
    # Drop the foreign key constraint on community_id if it exists.
    # Older databases will have the constraint, we have commented
    # it out in newer versions of the schema to break dependency to
    # the communities table.
    #
    op.drop_constraint(
        "fk_collections_collection_tree_community_id_communities_1eb3",
        "collections_collection_tree",
        type_="foreignkey",
        if_exists=True,
    )

    op.drop_index(
        op.f("ix_collections_collection_tree_community_id"),
        table_name="collections_collection_tree",
    )

    op.alter_column(
        "collections_collection_tree",
        "community_id",
        new_column_name="namespace_id",
    )

    op.drop_constraint(
        "uq_collections_collection_tree_slug_community_id",
        "collections_collection_tree",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_collections_collection_tree_slug_namespace_id",
        "collections_collection_tree",
        ["slug", "namespace_id"],
    )

    op.create_index(
        op.f("ix_collections_collection_tree_namespace_id"),
        "collections_collection_tree",
        ["namespace_id"],
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(
        op.f("ix_collections_collection_tree_namespace_id"),
        table_name="collections_collection_tree",
    )

    op.alter_column(
        "collections_collection_tree",
        "namespace_id",
        new_column_name="community_id",
    )

    op.drop_constraint(
        "uq_collections_collection_tree_slug_namespace_id",
        "collections_collection_tree",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_collections_collection_tree_slug_community_id",
        "collections_collection_tree",
        ["slug", "community_id"],
    )

    op.create_index(
        op.f("ix_collections_collection_tree_community_id"),
        "collections_collection_tree",
        ["community_id"],
    )

    op.create_foreign_key(
        "fk_collections_collection_tree_community_id_communities_1eb3",
        "collections_collection_tree",
        "communities_metadata",
        ["community_id"],
        ["id"],
        ondelete="SET NULL",
    )
