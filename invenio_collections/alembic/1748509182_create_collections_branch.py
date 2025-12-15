#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
# Copyright (C) 2025 Ubiquity Press
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create collections branch."""

# revision identifiers, used by Alembic.
revision = "1748509182"
down_revision = None
branch_labels = ("invenio_collections",)
depends_on = "ff9bec971d30"


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
