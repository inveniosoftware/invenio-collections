# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 CERN.
# Copyright (C) 2025 Ubiquity Press.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Collections configuration."""

COLLECTIONS_MAX_DEPTH = 1
"""Maximum depth for collection hierarchies.

Depth 0 = root collections
Depth 1 = children of root
Depth 2 = grandchildren (not allowed by default)

Setting this to 1 allows 2 levels: root + children only.
Setting this to 2 would allow 3 levels: root + children + grandchildren.
"""

COLLECTIONS_MAX_TREES = 10
"""Maximum number of collection trees allowed per community.

Set to 0 for unlimited trees.
Default: 10
"""

COLLECTIONS_MAX_COLLECTIONS_PER_TREE = 100
"""Maximum number of collections allowed per tree.

This counts all collections in a tree, regardless of depth.
Set to 0 for unlimited collections.
Default: 100
"""
