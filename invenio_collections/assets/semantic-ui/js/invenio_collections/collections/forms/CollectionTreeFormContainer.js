// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _cloneDeep from "lodash/cloneDeep";
import _defaultsDeep from "lodash/defaultsDeep";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { withCancel } from "react-invenio-forms";
import { communityErrorSerializer } from "../../api/serializers";
import { removeEmptyValues } from "../utils";
import { COLLECTION_TREE_VALIDATION_SCHEMA } from "../Configs";
import CollectionTreeForm from "./CollectionTreeForm";

/**
 * Container for creating or editing a collection tree (section).
 *
 * Edit mode is detected automatically: when `collectionTree` has an `id`
 * the form updates the existing tree; otherwise it creates a new one.
 */
class CollectionTreeFormContainer extends Component {
  state = {
    error: "",
  };

  componentWillUnmount() {
    this.cancellableSubmit && this.cancellableSubmit.cancel();
  }

  isEditing = () => {
    const { collectionTree } = this.props;
    return !!collectionTree?.id;
  };

  getInitialValues = () => {
    const { collectionTree } = this.props;
    return {
      ..._defaultsDeep(collectionTree, { id: "", title: "", slug: "" }),
    };
  };

  serializeValues = (values) => removeEmptyValues(_cloneDeep(values));

  setGlobalError = (error) => {
    const { message } = communityErrorSerializer(error);
    this.setState({ error: message });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    const { collectionTree, maxCollectionDepth, collectionApi, onSuccess } = this.props;

    const apiCall = this.isEditing()
      ? collectionApi.updateCollectionTree(collectionTree.slug, {
          title: values.title,
          slug: values.slug,
        })
      : collectionApi.createCollectionTree(
          this.serializeValues(values),
          maxCollectionDepth
        );

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
      onFormReady,
      handleCancel,
      slugGeneration: slugGenerationProp,
    } = this.props;
    const { error } = this.state;
    const slugGeneration = slugGenerationProp ?? !this.isEditing();

    return (
      <CollectionTreeForm
        initialValues={this.getInitialValues()}
        validationSchema={COLLECTION_TREE_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
        handleCancel={handleCancel}
        error={error}
        slugGeneration={slugGeneration}
        onFormReady={onFormReady}
      />
    );
  }
}

CollectionTreeFormContainer.propTypes = {
  collectionTree: PropTypes.object.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
  onSuccess: PropTypes.func,
  handleCancel: PropTypes.func,
  slugGeneration: PropTypes.bool,
  collectionApi: PropTypes.object.isRequired,
  onFormReady: PropTypes.func,
};

CollectionTreeFormContainer.defaultProps = {
  onSuccess: () => {},
  handleCancel: () => {},
  slugGeneration: undefined,
  onFormReady: undefined,
};

export default CollectionTreeFormContainer;
