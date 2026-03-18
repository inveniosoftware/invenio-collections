// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from "react-invenio-forms";
import { CommunityLinksExtractor } from "./CommunityLinksExtractor";

const ACCEPT_JSON = { Accept: "application/json" };
const ACCEPT_JSON_CONTENT_JSON = {
  Accept: "application/json",
  "Content-Type": "application/json",
};

/**
 * API Client for community collection trees.
 *
 * It mostly uses the API links passed to it from responses.
 *
 */
export class CommunityCollectionsApi {
  #urls;

  constructor(community, LinksExtractor = CommunityLinksExtractor) {
    this.#urls = new LinksExtractor(community);
  }

  get endpoint() {
    return this.#urls.collectionTreesUrl;
  }

  /**
   * Validate tree identifier parameters.
   * @private
   * @param {string|null} treeSlug - Tree slug
   * @param {string|null} treeId - Tree ID
   * @throws {Error} If neither parameter is provided
   */
  _validateTreeIdentifier(treeSlug, treeId) {
    if (!treeSlug && !treeId) {
      throw new Error("Either treeSlug or treeId must be provided");
    }
    if (treeSlug && treeId) {
      console.warn("Both treeSlug and treeId provided; both will be sent to backend");
    }
  }

  /**
   * Build URL with query parameters.
   * @private
   * @param {string} baseUrl - Base URL
   * @param {Object} params - Query parameters to append
   * @returns {string} URL with query parameters
   */
  _buildUrl(baseUrl, params = {}) {
    const url = new URL(baseUrl, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        url.searchParams.set(key, value);
      }
    });
    return url.toString();
  }

  /**
   * List all Community Collection Trees.
   *
   * @param {number} depth - Depth of the collection tree
   * @param {object} options - Custom options
   */
  getCollectionTrees(depth, options = {}) {
    const url = this._buildUrl(this.endpoint, { depth });
    return http.get(url, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Create a new Community Collection Tree.
   *
   * @param {object} payload - Serialized Collection object
   * @param {number} depth - Depth used when fetching existing trees to compute order
   * @param {object} options - Custom options
   */
  async createCollectionTree(payload, depth, options = {}) {
    const { data } = await this.getCollectionTrees(depth, options);
    const maxOrder = Math.max(
      ...Object.values(data).map(({ order }) => order || 0),
      0
    );
    payload.order = maxOrder + 1;
    return http.post(this.endpoint, payload, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Update a Community Collection Tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  updateCollectionTree(treeSlug, payload, options = {}, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(`${this.endpoint}/${treeSlug}`, { tree_id: treeId });
    return http.put(url, payload, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Delete a Community Collection Tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   * @param {boolean} cascade - Delete all collections in the tree (default: false)
   */
  deleteCollectionTree(treeSlug, options = {}, treeId = null, cascade = false) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(`${this.endpoint}/${treeSlug}`, {
      tree_id: treeId,
      cascade: cascade ? "true" : undefined,
    });
    return http.delete(url, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Get a Community Collection Tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {number} depth - Depth of the collection tree
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  getCollectionTree(treeSlug, depth, options = {}, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(`${this.endpoint}/${treeSlug}`, {
      depth,
      tree_id: treeId,
    });
    return http.get(url, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Create a new Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} payload - Serialized Collection object
   * @param {number} depth - Depth used when fetching existing collections to compute order
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async createCollection(treeSlug, payload, depth, options = {}, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const { data } = await this.getCollectionTree(treeSlug, depth, options, treeId);
    const maxOrder = Math.max(
      ...Object.values(data.collections).map(({ order }) => order || 0),
      0
    );
    payload.order = maxOrder + 1;
    const url = this._buildUrl(`${this.endpoint}/${treeSlug}/collections`, {
      tree_id: treeId,
    });
    return http.post(url, payload, { headers: ACCEPT_JSON_CONTENT_JSON, ...options });
  }

  /**
   * Add a new Community Collection to parent collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the parent collection
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  addCollection(treeSlug, collectionSlug, payload, options = {}, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections/${collectionSlug}`,
      { tree_id: treeId }
    );
    return http.post(url, payload, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Update a Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the collection
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  updateCollection(treeSlug, collectionSlug, payload, options = {}, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections/${collectionSlug}`,
      { tree_id: treeId }
    );
    return http.put(url, payload, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Delete a Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the collection
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   * @param {boolean} cascade - Whether to delete child collections (default: false)
   */
  deleteCollection(treeSlug, collectionSlug, options = {}, treeId = null, cascade = false) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections/${collectionSlug}`,
      {
        tree_id: treeId,
        cascade: cascade ? "true" : undefined,
      }
    );
    return http.delete(url, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Get a Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the collection
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  getCollection(treeSlug, collectionSlug, options = {}, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections/${collectionSlug}`,
      { tree_id: treeId }
    );
    return http.get(url, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Preview records matching a collection search query.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the collection
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  previewCollectionRecords(treeSlug, collectionSlug, payload, options = {}, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections-records-test`,
      { test_col_slug: collectionSlug, tree_id: treeId }
    );
    return http.post(url, payload, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Preview records matching the base collection query of a tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  previewBaseCollectionRecords(treeSlug, payload, options = {}, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections-records-test`,
      { tree_id: treeId }
    );
    return http.post(url, payload, { headers: ACCEPT_JSON, ...options });
  }

  /**
   * Batch reorder collection trees.
   *
   * @param {object} orderData - Order data with format: { order: [{slug, order}, ...] }
   * @param {object} options - Custom options
   */
  batchReorderTrees(orderData, options = {}) {
    const url = `${this.endpoint}/reorder`;
    return http.post(url, orderData, { headers: ACCEPT_JSON_CONTENT_JSON, ...options });
  }

  /**
   * Batch reorder collections within a tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} orderData - Order data with format: { order: [{slug, order}, ...] }
   * @param {object} options - Custom options
   */
  batchReorderCollections(treeSlug, orderData, options = {}) {
    const url = `${this.endpoint}/${treeSlug}/collections/reorder`;
    return http.post(url, orderData, { headers: ACCEPT_JSON_CONTENT_JSON, ...options });
  }
}
