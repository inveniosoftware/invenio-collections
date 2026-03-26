// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { Grid, Header, Label, Dropdown, Icon, Container } from "semantic-ui-react";
import { i18next } from "@translations/invenio_collections/i18next";
import ReorderableList from "./ReorderableList";
import { getActionMenuOptions } from "./CollectionActionMenu";
import CollectionChildItem from "./CollectionChildItem";
import { buildCollectionUrl } from "../Configs";

const CollectionItem = ({
  collection,
  allCollections,
  onEdit,
  onDelete,
  onAddChild,
  collectionApi,
  treeSlug,
  community,
  isDraggable = false,
  dragIndex = null,
  onDragStart = null,
  onDragEnd = null,
  isDragging = false,
  maxCollectionDepth,
}) => {
  const { title, num_records: numRecords, children: collectionChildren } = collection;

  const [childrenOrder, setChildrenOrder] = useState([]);
  const [draggedChildIndex, setDraggedChildIndex] = useState(null);
  const [draggedOverChildIndex, setDraggedOverChildIndex] = useState(null);
  const [isReordering, setIsReordering] = useState(false);
  const [reorderError, setReorderError] = useState(null);

  useEffect(() => {
    setChildrenOrder(collectionChildren || []);
  }, [collectionChildren]);

  const handleChildDragStart = (e, index) => {
    setDraggedChildIndex(index);
    e.dataTransfer.effectAllowed = "move";
  };

  const handleChildDragOver = (e, index) => {
    if (draggedChildIndex === null) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = "move";

    if (index !== draggedOverChildIndex) {
      setDraggedOverChildIndex(index);
    }
  };

  const handleChildDragEnd = async (e) => {
    e.stopPropagation();

    if (
      draggedChildIndex === null ||
      draggedOverChildIndex === null ||
      draggedChildIndex === draggedOverChildIndex
    ) {
      setDraggedChildIndex(null);
      setDraggedOverChildIndex(null);
      return;
    }

    const items = Array.from(childrenOrder);
    const [reorderedItem] = items.splice(draggedChildIndex, 1);
    items.splice(draggedOverChildIndex, 0, reorderedItem);

    setChildrenOrder(items);
    setDraggedChildIndex(null);
    setDraggedOverChildIndex(null);
    setReorderError(null);

    if (collectionApi && treeSlug) {
      setIsReordering(true);
      try {
        const orderPayload = {
          order: items
            .map((childId, index) => {
              const child = allCollections[childId];
              if (!child) {
                console.warn(`Child collection with id ${childId} not found`);
                return null;
              }
              return {
                slug: child.slug,
                order: (index + 1) * 10,
              };
            })
            .filter(Boolean),
        };

        await collectionApi.batchReorderCollections(treeSlug, orderPayload);
      } catch (error) {
        console.error("Failed to update child collection order:", error);
        setChildrenOrder(collectionChildren || []);
        setReorderError(i18next.t("Failed to save new order. Please try again."));
      } finally {
        setIsReordering(false);
      }
    }
  };

  const actionMenuOptions = getActionMenuOptions(
    collection,
    maxCollectionDepth,
    onEdit,
    onDelete,
    onAddChild
  );

  const parentCollectionUrl = buildCollectionUrl(collection, treeSlug, community);

  return (
    <Container className="mt-0 mb-0 rel-ml-1 collection-browse-card">
      <div className="content rel-mb-1">
        <Grid>
          <Grid.Column width={10} className="middle aligned">
            <div className="flex align-items-center">
              {isDraggable && onDragStart && (
                <Icon
                  name="bars"
                  className={`parent-drag-handle ${isDragging ? "grabbing" : ""}`}
                  draggable
                  onDragStart={(e) => onDragStart(e, dragIndex)}
                  onDragEnd={onDragEnd}
                  tabIndex={0}
                  role="button"
                />
              )}
              {parentCollectionUrl ? (
                <a
                  href={parentCollectionUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="collection-link"
                >
                  <Header as="h4" className="collection-title mt-0">
                    {title}
                  </Header>
                </a>
              ) : (
                <Header as="h4" className="collection-title theme-primary-text mt-0">
                  {title}
                </Header>
              )}
            </div>
          </Grid.Column>
          <Grid.Column width={3} className="middle aligned collection-number">
            <Label size="small">{numRecords || 0}</Label>
          </Grid.Column>
          <Grid.Column width={3} className="middle aligned" textAlign="right">
            <Dropdown
              icon="ellipsis vertical"
              floating
              button
              className="icon collection-actions-menu"
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
          </Grid.Column>
        </Grid>
      </div>

      {childrenOrder.length > 0 && (
        <div className="content">
          <ReorderableList isSaving={isReordering} error={reorderError}>
            {childrenOrder.map((childSlug, index) => (
              <CollectionChildItem
                key={childSlug}
                childSlug={childSlug}
                index={index}
                allCollections={allCollections}
                onEdit={onEdit}
                onDelete={onDelete}
                onAddChild={onAddChild}
                maxCollectionDepth={maxCollectionDepth}
                treeSlug={treeSlug}
                community={community}
                draggedChildIndex={draggedChildIndex}
                draggedOverChildIndex={draggedOverChildIndex}
                onDragStart={handleChildDragStart}
                onDragEnd={handleChildDragEnd}
                onDragOver={handleChildDragOver}
              />
            ))}
          </ReorderableList>
        </div>
      )}
    </Container>
  );
};

CollectionItem.propTypes = {
  collection: PropTypes.shape({
    id: PropTypes.string,
    slug: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    num_records: PropTypes.number,
    children: PropTypes.array,
    depth: PropTypes.number,
  }).isRequired,
  allCollections: PropTypes.object.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  onAddChild: PropTypes.func.isRequired,
  collectionApi: PropTypes.object,
  treeSlug: PropTypes.string,
  community: PropTypes.object,
  isDraggable: PropTypes.bool,
  dragIndex: PropTypes.number,
  onDragStart: PropTypes.func,
  onDragEnd: PropTypes.func,
  isDragging: PropTypes.bool,
  maxCollectionDepth: PropTypes.number.isRequired,
};

CollectionItem.defaultProps = {
  collectionApi: null,
  treeSlug: null,
  community: null,
  isDraggable: false,
  dragIndex: null,
  onDragStart: null,
  onDragEnd: null,
  isDragging: false,
};

export default CollectionItem;
