/*
 * This file is part of Invenio-Collections.
 * Copyright (C) 2026 CERN.
 *
 * Invenio-Collections is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_collections/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { withCancel } from "react-invenio-forms";
import { Button, Grid, Icon, Message, Header } from "semantic-ui-react";
import ReorderableList from "./components/ReorderableList";
import { communityErrorSerializer } from "../api/serializers";
import { CollectionsContext } from "../api/CollectionsContextProvider";
import CollectionTreeBrowseView from "./components/CollectionTreeBrowseView";
import PlaceholderLoader from "./components/PlaceholderLoader";
import {
  CollectionTreeFormModal,
  CollectionFormModal,
  DeleteCollectionTreeModal,
  DeleteCollectionModal,
} from "./modals";

class CollectionTreeManager extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: false,
      data: {},
      expandedTrees: {},
      // Collection tree (section) modals
      showNewTreeModal: false,
      showEditTreeModal: false,
      showDeleteTreeModal: false,
      treeToEdit: null,
      // Collection modals
      showNewCollectionModal: false,
      showChildCollectionModal: false,
      showEditCollectionModal: false,
      showDeleteCollectionModal: false,
      selectedTreeSlug: null,
      selectedTreeTitle: null,
      selectedCollectionSlug: null,
      collectionData: null,
      collectionToDelete: null,
      parentCollectionSlug: null,
      parentCollectionTitle: null,
      parentCollectionQuery: null,
      // Drag state
      draggedTreeIndex: null,
      draggedOverTreeIndex: null,
      isReorderingTrees: false,
      reorderTreesError: null,
    };
  }

  componentDidMount() {
    this.fetchData();
  }

  componentWillUnmount() {
    this.cancellableFetch && this.cancellableFetch.cancel();
  }

  static contextType = CollectionsContext;

  fetchData = async () => {
    const { maxCollectionDepth } = this.props;
    this.setState({ isLoading: true });
    const { api } = this.context;
    this.cancellableFetch = withCancel(api.getCollectionTrees(maxCollectionDepth));
    try {
      const response = await this.cancellableFetch.promise;
      this.setState({ data: response.data, isLoading: false });
    } catch (error) {
      if (error === "UNMOUNTED") return;
      this.setState({ isLoading: false });
      console.error(communityErrorSerializer(error));
    }
  };

  // ── Tree (section) modal handlers ──────────────────────────────────────────

  openNewTreeModal = () => this.setState({ showNewTreeModal: true });
  closeNewTreeModal = () => this.setState({ showNewTreeModal: false });
  handleNewTreeSuccess = () => {
    this.closeNewTreeModal();
    this.fetchData();
  };

  openEditTreeModal = (tree) =>
    this.setState({ showEditTreeModal: true, treeToEdit: tree });
  closeEditTreeModal = () =>
    this.setState({ showEditTreeModal: false, treeToEdit: null });
  handleEditTreeSuccess = () => {
    this.closeEditTreeModal();
    this.fetchData();
  };

  openDeleteTreeModal = (tree) =>
    this.setState({ showDeleteTreeModal: true, treeToEdit: tree });
  closeDeleteTreeModal = () =>
    this.setState({ showDeleteTreeModal: false, treeToEdit: null });
  handleDeleteTreeSuccess = () => {
    this.closeDeleteTreeModal();
    this.fetchData();
  };

  // ── Collection modal handlers ───────────────────────────────────────────────

  openNewCollectionModal = (treeId, treeSlug, treeTitle) => {
    this.setState({
      showNewCollectionModal: true,
      selectedTreeSlug: treeSlug || null,
      selectedTreeTitle: treeTitle || null,
    });
  };

  closeNewCollectionModal = () => {
    this.setState({
      showNewCollectionModal: false,
      selectedTreeSlug: null,
      selectedTreeTitle: null,
    });
  };

  handleNewCollectionSuccess = () => {
    this.closeNewCollectionModal();
    this.fetchData();
  };

  openChildCollectionModal = (treeSlug, treeTitle, parentSlug, parentTitle) => {
    const { maxCollectionDepth } = this.props;
    const { data } = this.state;
    const collectionTrees = Object.values(data);
    const tree = collectionTrees.find((t) => t.slug === treeSlug);
    let parentCollection = null;

    if (tree) {
      const findCollection = (collections, slug) => {
        for (const col of collections) {
          if (col.slug === slug) return col;
          if (col.children && col.children.length > 0) {
            const found = findCollection(col.children, slug);
            if (found) return found;
          }
        }
        return null;
      };
      parentCollection = findCollection(tree.collections, parentSlug);
    }

    if (parentCollection && parentCollection.depth >= maxCollectionDepth) {
      console.warn(
        `Cannot add child to collection at depth ${parentCollection.depth}. Maximum allowed depth is ${maxCollectionDepth}.`
      );
      return;
    }

    this.setState({
      showChildCollectionModal: true,
      selectedTreeSlug: treeSlug,
      selectedTreeTitle: treeTitle,
      parentCollectionSlug: parentSlug,
      parentCollectionTitle: parentTitle,
      parentCollectionQuery: parentCollection ? parentCollection.search_query : null,
    });
  };

  closeChildCollectionModal = () => {
    this.setState({
      showChildCollectionModal: false,
      selectedTreeSlug: null,
      selectedTreeTitle: null,
      parentCollectionSlug: null,
      parentCollectionTitle: null,
      parentCollectionQuery: null,
    });
  };

  handleChildCollectionSuccess = () => {
    this.closeChildCollectionModal();
    this.fetchData();
  };

  openEditCollectionModal = (treeSlug, treeTitle, collection) => {
    const { data } = this.state;
    const collectionTrees = Object.values(data);
    const tree = collectionTrees.find((t) => t.slug === treeSlug);
    const parentCollection = tree
      ? this.findParentCollection(tree.collections, collection.slug)
      : null;

    this.setState({
      showEditCollectionModal: true,
      selectedTreeSlug: treeSlug,
      selectedTreeTitle: treeTitle,
      selectedCollectionSlug: collection.slug,
      collectionData: collection,
      parentCollectionTitle: parentCollection ? parentCollection.title : null,
      parentCollectionQuery: parentCollection ? parentCollection.search_query : null,
    });
  };

  closeEditCollectionModal = () => {
    this.setState({
      showEditCollectionModal: false,
      selectedTreeSlug: null,
      selectedTreeTitle: null,
      selectedCollectionSlug: null,
      collectionData: null,
      parentCollectionTitle: null,
      parentCollectionQuery: null,
    });
  };

  handleEditCollectionSuccess = () => {
    this.closeEditCollectionModal();
    this.fetchData();
  };

  openDeleteCollectionModal = (treeSlug, collection) => {
    this.setState({
      showDeleteCollectionModal: true,
      selectedTreeSlug: treeSlug,
      selectedCollectionSlug: collection.slug,
      collectionToDelete: collection,
    });
  };

  closeDeleteCollectionModal = () => {
    this.setState({
      showDeleteCollectionModal: false,
      selectedTreeSlug: null,
      selectedCollectionSlug: null,
      collectionToDelete: null,
    });
  };

  handleDeleteCollectionSuccess = () => {
    this.closeDeleteCollectionModal();
    this.fetchData();
  };

  // ── Helpers ─────────────────────────────────────────────────────────────────

  findParentCollection = (collections, targetSlug) => {
    for (const collectionGroup of collections) {
      const collectionsArray = Object.values(collectionGroup).filter(
        (item) => typeof item === "object" && item !== null && item.slug
      );
      const targetCollection = collectionsArray.find((col) => col.slug === targetSlug);
      if (targetCollection) {
        if (targetCollection.depth === 0) return null;
        const parent = collectionsArray.find(
          (col) => col.depth === targetCollection.depth - 1
        );
        return parent || null;
      }
    }
    return null;
  };

  // ── Drag handlers ───────────────────────────────────────────────────────────

  toggleTreeExpansion = (treeId) => {
    this.setState((prevState) => ({
      expandedTrees: {
        ...prevState.expandedTrees,
        [treeId]: !prevState.expandedTrees[treeId],
      },
    }));
  };

  handleTreeDragStart = (e, index) => {
    this.setState({ draggedTreeIndex: index });
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/html", e.currentTarget);
  };

  handleTreeDragOver = (e, index) => {
    const { draggedTreeIndex, draggedOverTreeIndex } = this.state;
    if (draggedTreeIndex === null) return;
    e.preventDefault();
    e.stopPropagation();
    e.dataTransfer.dropEffect = "move";
    if (index !== draggedOverTreeIndex) {
      this.setState({ draggedOverTreeIndex: index });
    }
  };

  handleTreeDragEnd = async (e) => {
    e.stopPropagation();
    const { draggedTreeIndex, draggedOverTreeIndex, data } = this.state;
    this.setState({ draggedTreeIndex: null, draggedOverTreeIndex: null });

    if (
      draggedTreeIndex === null ||
      draggedOverTreeIndex === null ||
      draggedTreeIndex === draggedOverTreeIndex
    ) {
      return;
    }

    const trees = Object.values(data).sort((a, b) => (a.order || 0) - (b.order || 0));
    const [reorderedTree] = trees.splice(draggedTreeIndex, 1);
    trees.splice(draggedOverTreeIndex, 0, reorderedTree);

    const reorderedData = {};
    trees.forEach((tree, index) => {
      reorderedData[tree.slug] = { ...tree, order: (index + 1) * 10 };
    });
    this.setState({
      data: reorderedData,
      reorderTreesError: null,
      isReorderingTrees: true,
    });

    try {
      const orderPayload = {
        order: trees.map((tree, index) => ({
          slug: tree.slug,
          order: (index + 1) * 10,
        })),
      };
      const { api } = this.context;
      await api.batchReorderTrees(orderPayload);
    } catch (error) {
      console.error("Failed to update tree order:", error);
      this.setState({
        data,
        reorderTreesError: i18next.t("Failed to save new order. Please try again."),
      });
    } finally {
      this.setState({ isReorderingTrees: false });
    }
  };

  // ── Render helpers ──────────────────────────────────────────────────────────

  renderCollectionTrees() {
    const { data, expandedTrees, draggedTreeIndex, draggedOverTreeIndex } = this.state;
    const { community, maxCollectionDepth } = this.props;

    const sortedTrees = Object.values(data).sort(
      (a, b) => (a.order || 0) - (b.order || 0)
    );

    return sortedTrees.map((collectionTree, index) => {
      const isExpanded = expandedTrees[collectionTree.id] || false;
      const collections = collectionTree.collections || [];
      const isDraggingThis = draggedTreeIndex === index;
      const isDraggedOver =
        draggedOverTreeIndex === index && draggedTreeIndex !== index;

      return (
        <div
          key={collectionTree.id}
          className={`collection-tree-section rel-mb-2 ${
            isDraggingThis ? "dragging" : ""
          } ${isDraggedOver ? "drag-over" : ""}`}
          onDragOver={(e) => this.handleTreeDragOver(e, index)}
        >
          <Grid verticalAlign="middle" className="rel-mb-1">
            <Grid.Column width={1} textAlign="center">
              <div className="category-controls">
                <Icon
                  name="bars"
                  className={`tree-drag-handle ${isDraggingThis ? "grabbing" : ""}`}
                  draggable
                  onDragStart={(e) => this.handleTreeDragStart(e, index)}
                  onDragEnd={this.handleTreeDragEnd}
                />
                <Icon
                  name={isExpanded ? "chevron down" : "chevron right"}
                  className="category-toggle"
                  onClick={() => this.toggleTreeExpansion(collectionTree.id)}
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
                  this.openNewCollectionModal(
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
                onClick={() => this.openEditTreeModal(collectionTree)}
              >
                <Icon name="edit" /> {i18next.t("Edit section")}
              </Button>
              <Button
                negative
                size="small"
                icon="trash"
                title={i18next.t("Delete section")}
                onClick={() => this.openDeleteTreeModal(collectionTree)}
              />
            </Grid.Column>
          </Grid>

          {isExpanded && (
            <div className="collection-tree-content">
              <CollectionTreeBrowseView
                collectionTree={collectionTree}
                collections={collections}
                onAddCollection={this.openNewCollectionModal}
                onAddChildCollection={this.openChildCollectionModal}
                onEditCollection={this.openEditCollectionModal}
                onDeleteCollection={this.openDeleteCollectionModal}
                onEditTree={this.openEditTreeModal}
                onDeleteTree={this.openDeleteTreeModal}
                community={community}
                showHeader={false}
                maxCollectionDepth={maxCollectionDepth}
              />
            </div>
          )}
        </div>
      );
    });
  }

  render() {
    const {
      isLoading,
      data,
      isReorderingTrees,
      reorderTreesError,
      treeToEdit,
      showNewTreeModal,
      showEditTreeModal,
      showDeleteTreeModal,
      showNewCollectionModal,
      showChildCollectionModal,
      showEditCollectionModal,
      showDeleteCollectionModal,
      selectedTreeSlug,
      selectedTreeTitle,
      selectedCollectionSlug,
      collectionData,
      collectionToDelete,
      parentCollectionSlug,
      parentCollectionTitle,
      parentCollectionQuery,
    } = this.state;
    const { emptyMessage, community, maxCollectionDepth } = this.props;
    const { api } = this.context;

    return (
      <React.Fragment>
        <Grid>
          <Grid.Row>
            <Grid.Column width={12}>
              <h2>{i18next.t("Collections")}</h2>
              <p className="text-muted">
                {i18next.t("Collections must be organized into sections.")}
              </p>
            </Grid.Column>
            <Grid.Column width={4} textAlign="right">
              <Button positive onClick={this.openNewTreeModal}>
                <Icon name="plus" /> {i18next.t("New section")}
              </Button>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <PlaceholderLoader isLoading={isLoading}>
                {Object.keys(data).length === 0 ? (
                  <Message icon="info" header={emptyMessage} />
                ) : (
                  <ReorderableList
                    isSaving={isReorderingTrees}
                    error={reorderTreesError}
                  >
                    {this.renderCollectionTrees()}
                  </ReorderableList>
                )}
              </PlaceholderLoader>
            </Grid.Column>
          </Grid.Row>
        </Grid>

        <CollectionTreeFormModal
          open={showNewTreeModal}
          onClose={this.closeNewTreeModal}
          onSuccess={this.handleNewTreeSuccess}
          collectionTree={{}}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <CollectionTreeFormModal
          open={showEditTreeModal}
          onClose={this.closeEditTreeModal}
          onSuccess={this.handleEditTreeSuccess}
          collectionTree={treeToEdit || {}}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <DeleteCollectionTreeModal
          open={showDeleteTreeModal}
          onClose={this.closeDeleteTreeModal}
          onSuccess={this.handleDeleteTreeSuccess}
          collectionTree={treeToEdit}
          collectionApi={api}
        />

        <CollectionFormModal
          open={showNewCollectionModal}
          onClose={this.closeNewCollectionModal}
          onSuccess={this.handleNewCollectionSuccess}
          community={community}
          collectionTreeSlug={selectedTreeSlug}
          treeTitle={selectedTreeTitle}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <CollectionFormModal
          open={showChildCollectionModal}
          onClose={this.closeChildCollectionModal}
          onSuccess={this.handleChildCollectionSuccess}
          community={community}
          collectionTreeSlug={selectedTreeSlug}
          parentCollectionSlug={parentCollectionSlug}
          parentCollectionTitle={parentCollectionTitle}
          parentQuery={parentCollectionQuery}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <CollectionFormModal
          open={showEditCollectionModal}
          onClose={this.closeEditCollectionModal}
          onSuccess={this.handleEditCollectionSuccess}
          community={community}
          collectionTreeSlug={selectedTreeSlug}
          collectionSlug={selectedCollectionSlug}
          collectionData={collectionData}
          treeTitle={selectedTreeTitle}
          parentCollectionTitle={parentCollectionTitle}
          parentQuery={parentCollectionQuery}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <DeleteCollectionModal
          open={showDeleteCollectionModal}
          onClose={this.closeDeleteCollectionModal}
          onSuccess={this.handleDeleteCollectionSuccess}
          collectionTreeSlug={selectedTreeSlug}
          collection={collectionToDelete}
          collectionApi={api}
        />
      </React.Fragment>
    );
  }
}

CollectionTreeManager.propTypes = {
  community: PropTypes.object.isRequired,
  maxCollectionDepth: PropTypes.number.isRequired,
  emptyMessage: PropTypes.string.isRequired,
};

export default CollectionTreeManager;
