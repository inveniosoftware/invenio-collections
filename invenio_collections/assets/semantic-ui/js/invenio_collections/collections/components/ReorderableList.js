// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Dimmer, Loader, Message } from "semantic-ui-react";
import { i18next } from "@translations/invenio_collections/i18next";

const ReorderableList = ({ isSaving, error, children }) => (
  <>
    {error && (
      <Message negative className="rel-mb-1">
        {error}
      </Message>
    )}
    <Dimmer.Dimmable dimmed={isSaving}>
      <Dimmer active={isSaving} inverted>
        <Loader>{i18next.t("Saving order...")}</Loader>
      </Dimmer>
      {children}
    </Dimmer.Dimmable>
  </>
);

ReorderableList.propTypes = {
  isSaving: PropTypes.bool,
  error: PropTypes.string,
  children: PropTypes.node.isRequired,
};

ReorderableList.defaultProps = {
  isSaving: false,
  error: null,
};

export default ReorderableList;
