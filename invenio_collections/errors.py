# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2026 KTH Royal Institute of Technology.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Errors for collections module."""

from invenio_i18n import gettext as _


class CollectionError(Exception):
    """Base class for collection errors."""


class CollectionNotFound(CollectionError):
    """Collection not found error."""


class CollectionTreeNotFound(CollectionError):
    """Collection tree not found error."""


class InvalidQuery(CollectionError):
    """Query syntax is invalid."""


class LogoNotFoundError(CollectionError):
    """Logo not found error."""


class CollectionTreeHasCollections(CollectionError):
    """Collection tree contains collections."""


class CollectionHasChildren(CollectionError):
    """Collection has children collections."""


class DuplicateSlugError(CollectionError):
    """Slug already exists in this context."""


class MaxDepthExceeded(CollectionError):
    """Collection exceeds maximum allowed depth."""

    def __init__(self, current_depth, max_depth):
        """Initialize the error with depth information."""
        self.current_depth = current_depth
        self.max_depth = max_depth
        super().__init__(
            _(
                "Cannot create collection at depth %(current_depth)s. "
                "Maximum depth is %(max_depth)s (allowing depths 0-%(max_depth)s).",
                current_depth=current_depth + 1,
                max_depth=max_depth,
            )
        )


class MaxTreesExceeded(CollectionError):
    """Maximum number of trees exceeded for this namespace."""

    def __init__(self, current_count, max_trees):
        """Initialize the error with tree count information."""
        self.current_count = current_count
        self.max_trees = max_trees
        super().__init__(
            _(
                "Cannot create category. Namespace already has %(current_count)s categories. "
                "Maximum allowed is %(max_trees)s.",
                current_count=current_count,
                max_trees=max_trees,
            )
        )


class MaxCollectionsExceeded(CollectionError):
    """Maximum number of collections exceeded for this tree."""

    def __init__(self, current_count, max_collections):
        """Initialize the error with collection count information."""
        self.current_count = current_count
        self.max_collections = max_collections
        super().__init__(
            _(
                "Cannot create collection. Category already has %(current_count)s collections. "
                "Maximum allowed is %(max_collections)s.",
                current_count=current_count,
                max_collections=max_collections,
            )
        )
