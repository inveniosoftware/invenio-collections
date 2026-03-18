// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_collections/i18next";

/**
 * Build action menu options for a collection.
 *
 * @param {Object} collection - The collection object
 * @param {number} maxCollectionDepth - Maximum allowed collection depth
 * @param {Function} onEdit - Edit callback
 * @param {Function} onDelete - Delete callback
 * @param {Function} onAddChild - Add child callback
 * @returns {Array} Array of action menu option objects
 */
export const getActionMenuOptions = (
  collection,
  maxCollectionDepth,
  onEdit,
  onDelete,
  onAddChild
) => [
  {
    key: "edit",
    text: i18next.t("Edit"),
    icon: "edit",
    onClick: () => onEdit(collection),
  },
  ...(collection.depth < maxCollectionDepth
    ? [
        {
          key: "add-child",
          text: i18next.t("Add Child"),
          icon: "plus",
          onClick: () => onAddChild(collection),
        },
      ]
    : []),
  {
    key: "delete",
    text: i18next.t("Delete"),
    icon: "trash",
    onClick: () => onDelete(collection),
  },
];
