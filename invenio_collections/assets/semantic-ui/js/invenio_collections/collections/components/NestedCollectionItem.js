// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useEffect, memo } from "react";
import PropTypes from "prop-types";
import { Container, Header, Label, Dropdown } from "semantic-ui-react";
import { getActionMenuOptions } from "./CollectionActionMenu";
import { buildCollectionUrl } from "../Configs";

/**
 * Recursive component for rendering nested child collections.
 * Displays collection information with edit/delete/add actions and
 * recursively renders all descendant collections with visual indentation.
 *
 * Wrapped with React.memo so that re-renders are skipped when props haven't
 * changed. This matters because the parent re-renders on every drag event and
 * collections can be deeply nested.
 */
const NestedCollectionItem = memo(
  ({
    collection,
    allCollections,
    onEdit,
    onDelete,
    onAddChild,
    maxCollectionDepth,
    treeSlug,
    community,
    nestingLevel = 1,
  }) => {
    const { title, num_records: numRecords, children } = collection;

    const [childrenOrder, setChildrenOrder] = useState([]);

    useEffect(() => {
      setChildrenOrder(children || []);
    }, [children]);

    const actionMenuOptions = getActionMenuOptions(
      collection,
      maxCollectionDepth,
      onEdit,
      onDelete,
      onAddChild
    );

    const collectionUrl = buildCollectionUrl(collection, treeSlug, community);

    return (
      <div className="nested-collection-item" data-nesting-level={nestingLevel}>
        <Container className="mb-0 mt-0 collection-child-item">
          <div className="child-collection-row">
            <div className="child-collection-content">
              {collectionUrl ? (
                <a
                  href={collectionUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="collection-link truncated"
                  title={title}
                >
                  <Header as="h5" className="truncated">
                    {title}
                  </Header>
                </a>
              ) : (
                <Header as="h5" className="theme-primary-text truncated" title={title}>
                  {title}
                </Header>
              )}
              <Label size="tiny" className="child-collection-label text-muted ml-1">
                ({numRecords || 0})
              </Label>
            </div>
            <Dropdown
              icon="ellipsis vertical"
              floating
              button
              className="child-collection-actions icon mini collection-actions-menu"
            >
              <Dropdown.Menu direction="left">
                {actionMenuOptions.map((option) => (
                  <Dropdown.Item
                    key={option.key}
                    icon={option.icon}
                    text={option.text}
                    onClick={option.onClick}
                  />
                ))}
              </Dropdown.Menu>
            </Dropdown>
          </div>
        </Container>

        {childrenOrder.length > 0 && (
          <div className="nested-children">
            {childrenOrder.map((childSlug) => {
              const child = allCollections[childSlug];
              if (!child) return null;

              return (
                <NestedCollectionItem
                  key={childSlug}
                  collection={child}
                  allCollections={allCollections}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onAddChild={onAddChild}
                  maxCollectionDepth={maxCollectionDepth}
                  treeSlug={treeSlug}
                  community={community}
                  nestingLevel={nestingLevel + 1}
                />
              );
            })}
          </div>
        )}
      </div>
    );
  }
);

NestedCollectionItem.displayName = "NestedCollectionItem";

NestedCollectionItem.propTypes = {
  collection: PropTypes.object.isRequired, // The collection to render
  allCollections: PropTypes.object.isRequired, // Map of all collections by slug
  onEdit: PropTypes.func.isRequired, // Callback when edit is clicked
  onDelete: PropTypes.func.isRequired, // Callback when delete is clicked
  onAddChild: PropTypes.func.isRequired, // Callback when add child is clicked
  maxCollectionDepth: PropTypes.number.isRequired, // Maximum allowed collection depth
  treeSlug: PropTypes.string,
  community: PropTypes.object,
  nestingLevel: PropTypes.number, // Current nesting level for indentation
};

export default NestedCollectionItem;
