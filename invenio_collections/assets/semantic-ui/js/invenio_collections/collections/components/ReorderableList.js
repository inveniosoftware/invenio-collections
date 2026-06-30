/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { Dimmer, Loader, Message } from "semantic-ui-react";
import { i18next } from "@translations/invenio_collections/i18next";

const ReorderableList = ({ isSaving = false, error = null, children }) => (
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

export default ReorderableList;
