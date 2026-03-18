// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Modal } from "semantic-ui-react";
import { i18next } from "@translations/invenio_collections/i18next";
import DeleteCollectionAction from "../actions/DeleteCollectionAction";

const DeleteCollectionModal = ({
  open,
  onClose,
  onSuccess,
  collectionTreeSlug,
  collection,
  collectionApi,
}) => (
  <Modal open={open} onClose={onClose} size="large">
    <Modal.Header>{i18next.t("Delete Collection")}</Modal.Header>
    <DeleteCollectionAction
      collectionTreeSlug={collectionTreeSlug}
      collectionSlug={collection?.slug}
      hasChildren={collection?.children?.length > 0}
      onSuccess={onSuccess}
      handleCancel={onClose}
      collectionApi={collectionApi}
      confirmationMessage={i18next.t(
        "Are you sure you want to delete this collection? This action cannot be undone."
      )}
    />
  </Modal>
);

DeleteCollectionModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
  collectionTreeSlug: PropTypes.string,
  collection: PropTypes.object,
  collectionApi: PropTypes.object.isRequired,
};

DeleteCollectionModal.defaultProps = {
  collectionTreeSlug: null,
  collection: null,
};

export default DeleteCollectionModal;
