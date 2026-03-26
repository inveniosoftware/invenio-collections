// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _isArray from "lodash/isArray";
import _isBoolean from "lodash/isBoolean";
import _isEmpty from "lodash/isEmpty";
import _isNull from "lodash/isNull";
import _isNumber from "lodash/isNumber";
import _isObject from "lodash/isObject";
import _mapValues from "lodash/mapValues";
import _pickBy from "lodash/pickBy";

/**
 * Recursively find a collection by slug within a nested collections array.
 */
export const findCollectionBySlug = (collections, slug) => {
  for (const col of collections) {
    if (col.slug === slug) return col;
    if (col.children && col.children.length > 0) {
      const found = findCollectionBySlug(col.children, slug);
      if (found) return found;
    }
  }
  return null;
};

/**
 * Find the parent of a collection identified by targetSlug within a collection tree.
 * Returns null if the collection is at depth 0 or not found.
 */
export const findParentCollection = (collections, targetSlug) => {
  for (const collectionGroup of collections) {
    const collectionsArray = Object.values(collectionGroup).filter(
      (item) => typeof item === "object" && item !== null && item.slug
    );
    const targetCollection = collectionsArray.find((col) => col.slug === targetSlug);
    if (targetCollection) {
      if (targetCollection.depth === 0) return null;
      const parent = collectionsArray.find(
        (col) => col.depth === targetCollection.depth - 1
      );
      return parent || null;
    }
  }
  return null;
};

/**
 * Remove empty values from an object or array recursively
 */
export const removeEmptyValues = (obj) => {
  if (_isArray(obj)) {
    let mappedValues = obj.map((value) => removeEmptyValues(value));
    return mappedValues.filter((value) => {
      if (_isBoolean(value) || _isNumber(value)) {
        return value;
      }
      return !_isEmpty(value);
    });
  } else if (_isObject(obj)) {
    let mappedValues = _mapValues(obj, (value) => removeEmptyValues(value));
    return _pickBy(mappedValues, (value) => {
      if (_isArray(value) || _isObject(value)) {
        return !_isEmpty(value);
      }
      return !_isNull(value);
    });
  }
  return _isNumber(obj) || _isBoolean(obj) || obj ? obj : null;
};
