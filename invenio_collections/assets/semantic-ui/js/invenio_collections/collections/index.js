/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import { OverridableContext, overrideStore } from "react-overridable";
import { CollectionsContextProvider } from "../api/CollectionsContextProvider";
import CollectionTrees from "./CollectionTrees";

const domContainer = document.getElementById("invenio-collections-app");
const community = JSON.parse(domContainer.dataset.community);
const permissions = JSON.parse(domContainer.dataset.permissions);
const maxCollectionDepth = JSON.parse(domContainer.dataset.maxCollectionDepth);
const overriddenComponents = overrideStore.getAll();

createRoot(domContainer).render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CollectionsContextProvider community={community}>
      <CollectionTrees
        community={community}
        permissions={permissions}
        maxCollectionDepth={maxCollectionDepth}
      />
    </CollectionsContextProvider>
  </OverridableContext.Provider>
);
