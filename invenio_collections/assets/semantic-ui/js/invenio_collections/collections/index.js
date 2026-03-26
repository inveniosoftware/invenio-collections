// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { OverridableContext, overrideStore } from "react-overridable";
import { CollectionsContextProvider } from "../api/CollectionsContextProvider";
import CollectionTrees from "./CollectionTrees";

const domContainer = document.getElementById("invenio-collections-app");
const community = JSON.parse(domContainer.dataset.community);
const permissions = JSON.parse(domContainer.dataset.permissions);
const maxCollectionDepth = JSON.parse(domContainer.dataset.maxCollectionDepth);
const overriddenComponents = overrideStore.getAll();

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CollectionsContextProvider community={community}>
      <CollectionTrees
        community={community}
        permissions={permissions}
        maxCollectionDepth={maxCollectionDepth}
      />
    </CollectionsContextProvider>
  </OverridableContext.Provider>,
  domContainer
);
