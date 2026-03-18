// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { Formik } from "formik";
import { Button, Form, Grid, Message, Divider } from "semantic-ui-react";
import { FieldLabel, TextField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_collections/i18next";
import { generateSlug } from "../Configs";

const CollectionTreeFormInner = ({
  isSubmitting,
  isValid,
  handleSubmit,
  setFieldValue,
  handleCancel,
  error,
  slugGeneration,
  onFormReady,
}) => {
  useEffect(() => {
    onFormReady?.({ isSubmitting, isValid, handleSubmit, handleCancel });
  }, [isValid, isSubmitting, handleSubmit, handleCancel, onFormReady]);

  return (
    <Form onSubmit={handleSubmit} className="communities-collection-tree">
      <Message hidden={error === ""} negative>
        <Grid container>
          <Grid.Column width={15} textAlign="left">
            <strong>{error}</strong>
          </Grid.Column>
        </Grid>
      </Message>
      <Grid>
        <Grid.Row>
          <Grid.Column
            as="section"
            mobile={16}
            tablet={16}
            computer={16}
            className="rel-pb-2"
          >
            <TextField
              required
              fluid
              fieldPath="title"
              label={
                <FieldLabel
                  htmlFor="title"
                  icon="group"
                  label={i18next.t("Title")}
                />
              }
              onChange={
                slugGeneration
                  ? (event, { value }) => {
                      setFieldValue("title", value);
                      setFieldValue("slug", generateSlug(value));
                    }
                  : (event, { value }) => {
                      setFieldValue("title", value);
                    }
              }
            />
            <TextField
              required
              fluid
              fieldPath="slug"
              label={
                <FieldLabel
                  htmlFor="slug"
                  icon="group"
                  label={i18next.t("Slug")}
                />
              }
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Form>
  );
};

const CollectionTreeForm = ({
  initialValues,
  validationSchema,
  onSubmit,
  handleCancel,
  error,
  slugGeneration,
  onFormReady,
}) => (
  <Formik
    initialValues={initialValues}
    validationSchema={validationSchema}
    onSubmit={onSubmit}
    validateOnChange={false}
    validateOnBlur={false}
  >
    {({ isSubmitting, isValid, handleSubmit, setFieldValue }) => (
      <CollectionTreeFormInner
        isSubmitting={isSubmitting}
        isValid={isValid}
        handleSubmit={handleSubmit}
        setFieldValue={setFieldValue}
        handleCancel={handleCancel}
        error={error}
        slugGeneration={slugGeneration}
        onFormReady={onFormReady}
      />
    )}
  </Formik>
);

CollectionTreeForm.propTypes = {
  initialValues: PropTypes.object.isRequired,
  validationSchema: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  handleCancel: PropTypes.func.isRequired,
  error: PropTypes.string,
  slugGeneration: PropTypes.bool,
  onFormReady: PropTypes.func,
};

CollectionTreeForm.defaultProps = {
  error: "",
  slugGeneration: false,
};

export default CollectionTreeForm;
