// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Container, Header, Icon, Label, Dropdown } from "semantic-ui-react";
import { getActionMenuOptions } from "./CollectionActionMenu";
import NestedCollectionItem from "./NestedCollectionItem";
import { buildCollectionUrl } from "../Configs";

/**
 * Renders a single direct child collection row including drag handle,
 * title, record count, action menu, and any grandchildren below it.
 */
const CollectionChildItem = ({
  childSlug,
  index,
  allCollections,
  onEdit,
  onDelete,
  onAddChild,
  maxCollectionDepth,
  treeSlug,
  community,
  draggedChildIndex,
  draggedOverChildIndex,
  onDragStart,
  onDragEnd,
  onDragOver,
}) => {
  const child = allCollections[childSlug];
  if (!child) return null;

  const { title, num_records: numRecords, children: childChildren } = child;

  const childActionMenuOptions = getActionMenuOptions(
    child,
    maxCollectionDepth,
    onEdit,
    onDelete,
    onAddChild
  );

  const collectionUrl = buildCollectionUrl(child, treeSlug, community);

  const isChildDragging = draggedChildIndex === index;
  const isChildDraggedOver =
    draggedOverChildIndex === index && draggedChildIndex !== index;

  return (
    <div key={childSlug}>
      <Container
        className={`mb-0 mt-0 collection-child-item ${
          isChildDragging ? "dragging" : ""
        } ${isChildDraggedOver ? "drag-over" : ""}`}
        onDragOver={(e) => onDragOver(e, index)}
      >
        <div className="child-collection-row">
          <Icon
            name="bars"
            className={`child-drag-handle ${isChildDragging ? "grabbing" : ""}`}
            draggable
            onDragStart={(e) => onDragStart(e, index)}
            onDragEnd={onDragEnd}
            tabIndex={0}
            role="button"
          />
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
              {childActionMenuOptions.map((option) => (
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
      {childChildren && childChildren.length > 0 && (
        <div className="nested-children">
          {childChildren.map((grandchildSlug) => {
            const grandchild = allCollections[grandchildSlug];
            if (!grandchild) return null;

            return (
              <NestedCollectionItem
                key={grandchildSlug}
                collection={grandchild}
                allCollections={allCollections}
                onEdit={onEdit}
                onDelete={onDelete}
                onAddChild={onAddChild}
                maxCollectionDepth={maxCollectionDepth}
                treeSlug={treeSlug}
                community={community}
                nestingLevel={1}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};

CollectionChildItem.propTypes = {
  childSlug: PropTypes.string.isRequired,
  index: PropTypes.number.isRequired,
  allCollections: PropTypes.object.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  onAddChild: PropTypes.func.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
  treeSlug: PropTypes.string,
  community: PropTypes.object,
  draggedChildIndex: PropTypes.number,
  draggedOverChildIndex: PropTypes.number,
  onDragStart: PropTypes.func.isRequired,
  onDragEnd: PropTypes.func.isRequired,
  onDragOver: PropTypes.func.isRequired,
};

CollectionChildItem.defaultProps = {
  treeSlug: null,
  community: null,
  draggedChildIndex: null,
  draggedOverChildIndex: null,
};

export default CollectionChildItem;
