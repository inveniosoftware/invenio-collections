# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-FileCopyrightText: 2025 Ubiquity Press
# SPDX-License-Identifier: MIT

"""Create collections branch."""

# revision identifiers, used by Alembic.
revision = "1748509182"
down_revision = None
branch_labels = ("invenio_collections",)
depends_on = "dbdbc1b19cf2"


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
