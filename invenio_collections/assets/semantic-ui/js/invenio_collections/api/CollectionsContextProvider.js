/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { CommunityCollectionsApi } from "./api";
import React, { Component } from "react";
import PropTypes from "prop-types";

export const CollectionsContext = React.createContext({ api: undefined });

export class CollectionsContextProvider extends Component {
  constructor(props) {
    super(props);
    const { community } = props;
    this.apiClient = new CommunityCollectionsApi(community);
  }

  render() {
    const { children } = this.props;
    return (
      <CollectionsContext.Provider value={{ api: this.apiClient }}>
        {children}
      </CollectionsContext.Provider>
    );
  }
}

CollectionsContextProvider.propTypes = {
  community: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
};
