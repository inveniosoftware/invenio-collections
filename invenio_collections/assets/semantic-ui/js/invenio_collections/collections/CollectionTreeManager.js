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
import { Button, Grid, Icon, Message } from "semantic-ui-react";
import ReorderableList from "./components/ReorderableList";
import { communityErrorSerializer } from "../api/serializers";
import { CollectionsContext } from "../api/CollectionsContextProvider";
import CollectionTreeSection from "./components/CollectionTreeSection";
import PlaceholderLoader from "./components/PlaceholderLoader";
import {
  CollectionTreeFormModal,
  CollectionFormModal,
  DeleteCollectionTreeModal,
  DeleteCollectionModal,
} from "./modals";
import { findCollectionBySlug, findParentCollection } from "./utils";

class CollectionTreeManager extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: false,
      data: {},
      expandedTrees: {},
      activeModal: null, // { type, ...payload }
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

  // ── Modal handlers ──────────────────────────────────────────────────────────

  openModal = (type, payload = {}) => this.setState({ activeModal: { type, ...payload } });
  closeModal = () => this.setState({ activeModal: null });

  handleModalSuccess = () => {
    this.closeModal();
    this.fetchData();
  };

  openNewCollectionModal = (treeId, treeSlug, treeTitle) =>
    this.openModal("newCollection", { treeSlug: treeSlug || null, treeTitle: treeTitle || null });

  openChildCollectionModal = (treeSlug, treeTitle, parentSlug, parentTitle) => {
    const { maxCollectionDepth } = this.props;
    const { data } = this.state;
    const tree = Object.values(data).find((t) => t.slug === treeSlug);
    const parentCollection = tree
      ? findCollectionBySlug(tree.collections, parentSlug)
      : null;

    if (parentCollection && parentCollection.depth >= maxCollectionDepth) {
      console.warn(
        `Cannot add child to collection at depth ${parentCollection.depth}. Maximum allowed depth is ${maxCollectionDepth}.`
      );
      return;
    }

    this.openModal("childCollection", {
      treeSlug,
      treeTitle,
      parentCollectionSlug: parentSlug,
      parentCollectionTitle: parentTitle,
      parentCollectionQuery: parentCollection ? parentCollection.search_query : null,
    });
  };

  openEditCollectionModal = (treeSlug, treeTitle, collection) => {
    const { data } = this.state;
    const tree = Object.values(data).find((t) => t.slug === treeSlug);
    const parentCollection = tree
      ? findParentCollection(tree.collections, collection.slug)
      : null;

    this.openModal("editCollection", {
      treeSlug,
      treeTitle,
      collectionSlug: collection.slug,
      collectionData: collection,
      parentCollectionTitle: parentCollection ? parentCollection.title : null,
      parentCollectionQuery: parentCollection ? parentCollection.search_query : null,
    });
  };

  openDeleteCollectionModal = (treeSlug, collection) =>
    this.openModal("deleteCollection", {
      treeSlug,
      collectionSlug: collection.slug,
      collectionToDelete: collection,
    });

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

  render() {
    const {
      isLoading,
      data,
      expandedTrees,
      draggedTreeIndex,
      draggedOverTreeIndex,
      activeModal,
      isReorderingTrees,
      reorderTreesError,
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
              <Button positive onClick={() => this.openModal("newTree")}>
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
                    {Object.values(data)
                      .sort((a, b) => (a.order || 0) - (b.order || 0))
                      .map((collectionTree, index) => (
                        <CollectionTreeSection
                          key={collectionTree.id}
                          collectionTree={collectionTree}
                          index={index}
                          isExpanded={expandedTrees[collectionTree.id] || false}
                          isDragging={draggedTreeIndex === index}
                          isDraggedOver={
                            draggedOverTreeIndex === index && draggedTreeIndex !== index
                          }
                          community={community}
                          maxCollectionDepth={maxCollectionDepth}
                          onDragStart={this.handleTreeDragStart}
                          onDragOver={this.handleTreeDragOver}
                          onDragEnd={this.handleTreeDragEnd}
                          onToggleExpansion={this.toggleTreeExpansion}
                          onOpenModal={this.openModal}
                          onAddCollection={this.openNewCollectionModal}
                          onAddChildCollection={this.openChildCollectionModal}
                          onEditCollection={this.openEditCollectionModal}
                          onDeleteCollection={this.openDeleteCollectionModal}
                        />
                      ))}
                  </ReorderableList>
                )}
              </PlaceholderLoader>
            </Grid.Column>
          </Grid.Row>
        </Grid>

        <CollectionTreeFormModal
          open={activeModal?.type === "newTree"}
          onClose={this.closeModal}
          onSuccess={this.handleModalSuccess}
          collectionTree={{}}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <CollectionTreeFormModal
          open={activeModal?.type === "editTree"}
          onClose={this.closeModal}
          onSuccess={this.handleModalSuccess}
          collectionTree={activeModal?.tree || {}}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <DeleteCollectionTreeModal
          open={activeModal?.type === "deleteTree"}
          onClose={this.closeModal}
          onSuccess={this.handleModalSuccess}
          collectionTree={activeModal?.tree || null}
          collectionApi={api}
        />

        <CollectionFormModal
          open={activeModal?.type === "newCollection"}
          onClose={this.closeModal}
          onSuccess={this.handleModalSuccess}
          community={community}
          collectionTreeSlug={activeModal?.treeSlug || null}
          treeTitle={activeModal?.treeTitle || null}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <CollectionFormModal
          open={activeModal?.type === "childCollection"}
          onClose={this.closeModal}
          onSuccess={this.handleModalSuccess}
          community={community}
          collectionTreeSlug={activeModal?.treeSlug || null}
          parentCollectionSlug={activeModal?.parentCollectionSlug || null}
          parentCollectionTitle={activeModal?.parentCollectionTitle || null}
          parentQuery={activeModal?.parentCollectionQuery || null}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <CollectionFormModal
          open={activeModal?.type === "editCollection"}
          onClose={this.closeModal}
          onSuccess={this.handleModalSuccess}
          community={community}
          collectionTreeSlug={activeModal?.treeSlug || null}
          collectionSlug={activeModal?.collectionSlug || null}
          collectionData={activeModal?.collectionData || null}
          treeTitle={activeModal?.treeTitle || null}
          parentCollectionTitle={activeModal?.parentCollectionTitle || null}
          parentQuery={activeModal?.parentCollectionQuery || null}
          maxCollectionDepth={maxCollectionDepth}
          collectionApi={api}
        />

        <DeleteCollectionModal
          open={activeModal?.type === "deleteCollection"}
          onClose={this.closeModal}
          onSuccess={this.handleModalSuccess}
          collectionTreeSlug={activeModal?.treeSlug || null}
          collection={activeModal?.collectionToDelete || null}
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
