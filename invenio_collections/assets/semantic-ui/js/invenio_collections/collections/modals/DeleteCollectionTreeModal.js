// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Modal } from "semantic-ui-react";
import { i18next } from "@translations/invenio_collections/i18next";
import DeleteCollectionTreeAction from "../actions/DeleteCollectionTreeAction";

const DeleteCollectionTreeModal = ({ open, onClose, onSuccess, collectionTree, collectionApi }) => (
  <Modal open={open} onClose={onClose} size="large">
    <Modal.Header>{i18next.t("Delete section")}</Modal.Header>
    <DeleteCollectionTreeAction
      collectionTree={collectionTree}
      hasCollections={collectionTree?.collections?.length > 0}
      onSuccess={onSuccess}
      handleCancel={onClose}
      collectionApi={collectionApi}
      confirmationMessage={i18next.t(
        "Are you sure you want to delete this section? This action cannot be undone."
      )}
    />
  </Modal>
);

DeleteCollectionTreeModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
  collectionTree: PropTypes.object,
  collectionApi: PropTypes.object.isRequired,
};

DeleteCollectionTreeModal.defaultProps = {
  collectionTree: null,
};

export default DeleteCollectionTreeModal;
