# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create collections tables."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '97faa437d867'
down_revision = 'ce7adcbe1c6c'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        'collection',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('dbquery', sa.Text(), nullable=True),
        sa.Column('rgt', sa.Integer(), nullable=False),
        sa.Column('lft', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('tree_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['parent_id'], ['collection.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'collection_level_idx', 'collection', ['level'], unique=False
    )
    op.create_index('collection_lft_idx', 'collection', ['lft'], unique=False)
    op.create_index('collection_rgt_idx', 'collection', ['rgt'], unique=False)
    op.create_index(
        op.f('ix_collection_name'), 'collection', ['name'], unique=True
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(op.f('ix_collection_name'), table_name='collection')
    op.drop_index('collection_rgt_idx', table_name='collection')
    op.drop_index('collection_lft_idx', table_name='collection')
    op.drop_index('collection_level_idx', table_name='collection')
    op.drop_table('collection')
