/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { i18next } from "@translations/invenio_collections/i18next";
import CollectionTreeManager from "./CollectionTreeManager";

/**
 * CollectionTrees component
 * Renders a list of collection trees associated with a community
 * @component
 * @param {object} props - component props
 * @param {object} props.community - community data
 * @param {object} props.permissions - permissions data
 * @returns {JSX.Element} - rendered component
 */
class CollectionTrees extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    const { community, permissions, maxCollectionDepth } = this.props;

    return (
      <Overridable id="CollectionTrees" {...this.props}>
        <CollectionTreeManager
          community={community}
          permissions={permissions}
          maxCollectionDepth={maxCollectionDepth}
          emptyMessage={i18next.t("There are no sections.")}
        />
      </Overridable>
    );
  }
}

CollectionTrees.propTypes = {
  community: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
};

export default CollectionTrees;
