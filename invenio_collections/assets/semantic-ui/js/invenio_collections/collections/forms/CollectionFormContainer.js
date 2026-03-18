// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { withCancel } from "react-invenio-forms";
import { communityErrorSerializer } from "../../api/serializers";
import _cloneDeep from "lodash/cloneDeep";
import { removeEmptyValues } from "../utils";
import { COLLECTION_VALIDATION_SCHEMA } from "../Configs";
import CollectionForm from "./CollectionForm";

/**
 * Container for creating or editing a collection.
 *
 * Mode is determined by the props:
 * - Edit mode: `collectionSlug` + `collectionData` are provided.
 * - Child creation: `parentCollectionSlug` is provided (no `collectionSlug`).
 * - Root creation: neither `collectionSlug` nor `parentCollectionSlug` is set.
 */
class CollectionFormContainer extends Component {
  state = {
    error: "",
    testQueryResult: null,
    testQuerySuccess: null,
    testQueryHits: [],
  };

  componentWillUnmount() {
    this.cancellableTest && this.cancellableTest.cancel();
    this.cancellableSubmit && this.cancellableSubmit.cancel();
  }

  isEditing = () => !!this.props.collectionSlug;

  getInitialValues = () => {
    if (this.isEditing()) {
      const { collectionData } = this.props;
      return {
        title: collectionData.title,
        slug: collectionData.slug,
        search_query: collectionData.search_query,
      };
    }
    return { title: "", slug: "", search_query: "*" };
  };

  serializeValues = (values) => removeEmptyValues(_cloneDeep(values));

  setGlobalError = (error) => {
    const { message } = communityErrorSerializer(error);
    this.setState({ error: message });
  };

  onTest = async (values) => {
    const { collectionTreeSlug, collectionSlug, parentCollectionSlug, collectionApi } =
      this.props;

    const contextSlug = collectionSlug || parentCollectionSlug;
    const apiCall = contextSlug
      ? collectionApi.previewCollectionRecords(
          collectionTreeSlug,
          contextSlug,
          values
        )
      : collectionApi.previewBaseCollectionRecords(collectionTreeSlug, values);

    this.cancellableTest = withCancel(apiCall);
    try {
      const response = await this.cancellableTest.promise;
      this.setState({
        testQuerySuccess: true,
        testQueryResult: response.data.hits.total,
        testQueryHits: response.data.hits.hits,
      });
    } catch (error) {
      if (error === "UNMOUNTED") return;
      this.setState({
        testQuerySuccess: false,
        testQueryResult: error.response?.data?.message || "Network error",
      });
    }
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    const payload = this.serializeValues(values);
    const {
      collectionTreeSlug,
      collectionSlug,
      parentCollectionSlug,
      maxCollectionDepth,
      collectionApi,
      onSuccess,
    } = this.props;

    let apiCall;
    if (this.isEditing()) {
      apiCall = collectionApi.updateCollection(collectionTreeSlug, collectionSlug, payload);
    } else if (parentCollectionSlug) {
      apiCall = collectionApi.addCollection(
        collectionTreeSlug,
        parentCollectionSlug,
        payload
      );
    } else {
      apiCall = collectionApi.createCollection(
        collectionTreeSlug,
        payload,
        maxCollectionDepth
      );
    }

    this.cancellableSubmit = withCancel(apiCall);
    try {
      await this.cancellableSubmit.promise;
      onSuccess();
    } catch (error) {
      if (error === "UNMOUNTED") return;
      const { message, errors } = communityErrorSerializer(error);
      if (message) {
        this.setGlobalError(error);
      }
      if (errors) {
        errors.forEach(({ field, messages }) => setFieldError(field, messages[0]));
      }
    } finally {
      setSubmitting(false);
    }
  };

  render() {
    const {
      community,
      parentQuery,
      onFormReady,
      handleCancel,
      slugGeneration: slugGenerationProp,
    } = this.props;
    const { testQueryResult, testQuerySuccess, testQueryHits, error } = this.state;
    const slugGeneration = slugGenerationProp ?? !this.isEditing();

    return (
      <CollectionForm
        initialValues={this.getInitialValues()}
        validationSchema={COLLECTION_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
        onTest={this.onTest}
        handleCancel={handleCancel}
        testQueryResult={testQueryResult}
        testQuerySuccess={testQuerySuccess}
        testQueryHits={testQueryHits}
        error={error}
        slugGeneration={slugGeneration}
        community={community}
        parentQuery={parentQuery}
        onFormReady={onFormReady}
      />
    );
  }
}

CollectionFormContainer.propTypes = {
  collectionTreeSlug: PropTypes.string.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
  /** Slug of the collection to edit. When set, the form operates in edit mode. */
  collectionSlug: PropTypes.string,
  /** Existing collection data, required when editing. */
  collectionData: PropTypes.object,
  /** When set (and not editing), the new collection is created as a child of this slug. */
  parentCollectionSlug: PropTypes.string,
  onSuccess: PropTypes.func,
  handleCancel: PropTypes.func,
  slugGeneration: PropTypes.bool,
  collectionApi: PropTypes.object.isRequired,
  community: PropTypes.object,
  parentQuery: PropTypes.string,
  onFormReady: PropTypes.func,
};

CollectionFormContainer.defaultProps = {
  collectionSlug: null,
  collectionData: null,
  parentCollectionSlug: null,
  onSuccess: () => {},
  handleCancel: () => {},
  slugGeneration: undefined,
};

export default CollectionFormContainer;
