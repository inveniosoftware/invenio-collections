// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import PropTypes from "prop-types";
import { Button, Modal } from "semantic-ui-react";
import { i18next } from "@translations/invenio_collections/i18next";
import CollectionTreeFormContainer from "../forms/CollectionTreeFormContainer";

/**
 * Modal for creating or editing a collection tree (section).
 * Edit mode is detected automatically: when `collectionTree` has an `id`
 * the form updates the existing tree; otherwise it creates a new one.
 */
const CollectionTreeFormModal = ({
  open,
  onClose,
  onSuccess,
  collectionTree,
  maxCollectionDepth,
  collectionApi,
}) => {
  const [formState, setFormState] = useState(null);

  const isEditing = !!collectionTree?.id;
  const title = isEditing ? i18next.t("Edit section") : i18next.t("Create new section");

  return (
    <Modal open={open} onClose={onClose} size="large">
      <Modal.Header>{title}</Modal.Header>
      <Modal.Content className="pb-0">
        <CollectionTreeFormContainer
          collectionTree={collectionTree}
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

CollectionTreeFormModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
  collectionTree: PropTypes.object.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
  collectionApi: PropTypes.object.isRequired,
};

export default CollectionTreeFormModal;
