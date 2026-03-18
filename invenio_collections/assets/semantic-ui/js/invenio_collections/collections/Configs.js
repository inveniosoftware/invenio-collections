// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_collections/i18next";
import * as Yup from "yup";

export const COLLECTION_VALIDATION_SCHEMA = Yup.object({
  title: Yup.string()
    .required(i18next.t("Title is required"))
    .max(255, i18next.t("Maximum number of characters is 255")),
  slug: Yup.string()
    .required(i18next.t("Slug is required"))
    .max(100, i18next.t("Maximum number of characters is 100")),
  search_query: Yup.string().required(i18next.t("Search query is required")),
});

export const COLLECTION_TREE_VALIDATION_SCHEMA = Yup.object({
  title: Yup.string()
    .required(i18next.t("Title is required"))
    .max(255, i18next.t("Maximum number of characters is 255")),
  slug: Yup.string()
    .required(i18next.t("Slug is required"))
    .max(100, i18next.t("Maximum number of characters is 100")),
});

/**
 * Build a URL for a collection within a community namespace.
 * Uses self_html from the API links when available, falls back to
 * constructing the URL from community slug + tree slug + collection slug.
 */
export const buildCollectionUrl = (collection, treeSlug, community) => {
  if (collection.links?.self_html) {
    return collection.links.self_html;
  }
  if (community?.slug && collection.slug) {
    return `/communities/${community.slug}/collections/read/${collection.slug}`;
  }
  return null;
};

/**
 * Convert a string to a URL-friendly slug.
 * Lowercases, trims, replaces spaces and ampersands with hyphens,
 * strips non-word characters, and collapses consecutive hyphens.
 */
export const generateSlug = (text) => {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/&/g, "-and-")
    .replace(/[^\w\-]+/g, "")
    .replace(/\-\-+/g, "-");
};
