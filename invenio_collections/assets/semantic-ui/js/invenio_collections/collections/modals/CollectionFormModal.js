// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import PropTypes from "prop-types";
import { Button, Modal } from "semantic-ui-react";
import { i18next } from "@translations/invenio_collections/i18next";
import CollectionFormContainer from "../forms/CollectionFormContainer";

/**
 * Modal for creating, adding a child, or editing a collection.
 * Mode is determined by props (mirrors CollectionFormContainer logic):
 * - Edit:  `collectionSlug` is set
 * - Child: `parentCollectionSlug` is set (no `collectionSlug`)
 * - Root:  neither is set
 */
const CollectionFormModal = ({
  open,
  onClose,
  onSuccess,
  community,
  collectionTreeSlug,
  collectionSlug,
  collectionData,
  parentCollectionSlug,
  parentCollectionTitle,
  treeTitle,
  parentQuery,
  maxCollectionDepth,
  collectionApi,
}) => {
  const [formState, setFormState] = useState(null);

  const getTitle = () => {
    if (collectionSlug) {
      const context = parentCollectionTitle || treeTitle;
      return context
        ? `${i18next.t("Edit collection in")} ${context}`
        : i18next.t("Edit collection");
    }
    if (parentCollectionSlug) {
      return parentCollectionTitle
        ? `${i18next.t("Add child collection in")} ${parentCollectionTitle}`
        : i18next.t("Add child collection");
    }
    return treeTitle
      ? `${i18next.t("Create new collection in")} ${treeTitle}`
      : i18next.t("Create new collection");
  };

  return (
    <Modal open={open} onClose={onClose} size="large">
      <Modal.Header>{getTitle()}</Modal.Header>
      <Modal.Content className="pb-0">
        <CollectionFormContainer
          community={community}
          collectionTreeSlug={collectionTreeSlug}
          collectionSlug={collectionSlug}
          collectionData={collectionData}
          parentCollectionSlug={parentCollectionSlug}
          parentQuery={parentQuery}
          maxCollectionDepth={maxCollectionDepth}
          onSuccess={onSuccess}
          handleCancel={onClose}
          collectionApi={collectionApi}
          onFormReady={setFormState}
        />
      </Modal.Content>
      <Modal.Actions className="flex justify-space-between">
        <Button onClick={onClose}>{i18next.t("Cancel")}</Button>
        <Button
          primary
          disabled={!formState?.isValid || formState?.isSubmitting}
          loading={formState?.isSubmitting}
          onClick={() => formState?.handleSubmit()}
        >
          {i18next.t("Save")}
        </Button>
      </Modal.Actions>
    </Modal>
  );
};

CollectionFormModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
  collectionTreeSlug: PropTypes.string.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
  collectionApi: PropTypes.object.isRequired,
  community: PropTypes.object,
  collectionSlug: PropTypes.string,
  collectionData: PropTypes.object,
  parentCollectionSlug: PropTypes.string,
  parentCollectionTitle: PropTypes.string,
  treeTitle: PropTypes.string,
  parentQuery: PropTypes.string,
};

CollectionFormModal.defaultProps = {
  community: null,
  collectionSlug: null,
  collectionData: null,
  parentCollectionSlug: null,
  parentCollectionTitle: null,
  treeTitle: null,
  parentQuery: null,
};

export default CollectionFormModal;
