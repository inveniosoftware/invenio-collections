// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Button, Grid, Icon, Header } from "semantic-ui-react";
import { i18next } from "@translations/invenio_collections/i18next";
import CollectionTreeBrowseView from "./CollectionTreeBrowseView";

const CollectionTreeSection = ({
  collectionTree,
  index,
  isExpanded,
  isDragging,
  isDraggedOver,
  community,
  maxCollectionDepth,
  onDragStart,
  onDragOver,
  onDragEnd,
  onToggleExpansion,
  onOpenModal,
  onAddCollection,
  onAddChildCollection,
  onEditCollection,
  onDeleteCollection,
}) => {
  const collections = collectionTree.collections || [];

  return (
    <div
      className={`collection-tree-section rel-mb-2 ${isDragging ? "dragging" : ""} ${
        isDraggedOver ? "drag-over" : ""
      }`}
      onDragOver={(e) => onDragOver(e, index)}
    >
      <Grid verticalAlign="middle" className="rel-mb-1">
        <Grid.Column width={1} textAlign="center">
          <div className="category-controls">
            <Icon
              name="bars"
              className={`tree-drag-handle ${isDragging ? "grabbing" : ""}`}
              draggable
              onDragStart={(e) => onDragStart(e, index)}
              onDragEnd={onDragEnd}
            />
            <Icon
              name={isExpanded ? "chevron down" : "chevron right"}
              className="category-toggle"
              onClick={() => onToggleExpansion(collectionTree.id)}
            />
          </div>
        </Grid.Column>
        <Grid.Column width={9}>
          <Header as="h2" className="category-header">
            {collectionTree.title}
          </Header>
        </Grid.Column>
        <Grid.Column width={6} textAlign="right">
          <Button
            positive
            size="small"
            onClick={() =>
              onAddCollection(
                collectionTree.id,
                collectionTree.slug,
                collectionTree.title
              )
            }
          >
            <Icon name="plus" /> {i18next.t("New collection")}
          </Button>
          <Button
            size="small"
            onClick={() => onOpenModal("editTree", { tree: collectionTree })}
          >
            <Icon name="edit" /> {i18next.t("Edit section")}
          </Button>
          <Button
            negative
            size="small"
            icon="trash"
            title={i18next.t("Delete section")}
            onClick={() => onOpenModal("deleteTree", { tree: collectionTree })}
          />
        </Grid.Column>
      </Grid>

      {isExpanded && (
        <div className="collection-tree-content">
          <CollectionTreeBrowseView
            collectionTree={collectionTree}
            collections={collections}
            onAddCollection={onAddCollection}
            onAddChildCollection={onAddChildCollection}
            onEditCollection={onEditCollection}
            onDeleteCollection={onDeleteCollection}
            onEditTree={(tree) => onOpenModal("editTree", { tree })}
            onDeleteTree={(tree) => onOpenModal("deleteTree", { tree })}
            community={community}
            showHeader={false}
            maxCollectionDepth={maxCollectionDepth}
          />
        </div>
      )}
    </div>
  );
};

CollectionTreeSection.propTypes = {
  collectionTree: PropTypes.shape({
    id: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    collections: PropTypes.array,
  }).isRequired,
  index: PropTypes.number.isRequired,
  isExpanded: PropTypes.bool.isRequired,
  isDragging: PropTypes.bool.isRequired,
  isDraggedOver: PropTypes.bool.isRequired,
  community: PropTypes.object,
  maxCollectionDepth: PropTypes.number.isRequired,
  onDragStart: PropTypes.func.isRequired,
  onDragOver: PropTypes.func.isRequired,
  onDragEnd: PropTypes.func.isRequired,
  onToggleExpansion: PropTypes.func.isRequired,
  onOpenModal: PropTypes.func.isRequired,
  onAddCollection: PropTypes.func.isRequired,
  onAddChildCollection: PropTypes.func.isRequired,
  onEditCollection: PropTypes.func.isRequired,
  onDeleteCollection: PropTypes.func.isRequired,
};

CollectionTreeSection.defaultProps = {
  community: null,
};

export default CollectionTreeSection;
