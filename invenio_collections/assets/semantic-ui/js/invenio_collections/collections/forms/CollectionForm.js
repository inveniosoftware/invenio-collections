// This file is part of Invenio-Collections
// Copyright (C) 2026 CERN.
//
// Invenio-Collections is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import { Button, Form, Grid, Message } from "semantic-ui-react";
import { BaseForm, FieldLabel, TextField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_collections/i18next";
import { generateSlug } from "../Configs";

const CollectionFormInner = ({
  handleCancel,
  onFormReady,
  onTest,
  testQueryResult,
  testQuerySuccess,
  testQueryHits,
  error,
  slugGeneration,
  community,
  parentQuery,
}) => {
  const {
    isSubmitting,
    isValid,
    handleSubmit,
    setFieldValue,
    handleChange,
    handleBlur,
    values,
    touched,
    errors,
  } = useFormikContext();

  useEffect(() => {
    onFormReady?.({ isSubmitting, isValid, handleSubmit, handleCancel });
    // handleSubmit/handleCancel are stable refs; only re-notify parent
    // when the values that affect button state change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isValid, isSubmitting]);

  const buildFullSearchQuery = (currentQuery) => {
    if (parentQuery && currentQuery) {
      return `(${parentQuery}) AND (${currentQuery})`;
    }
    return currentQuery || parentQuery || "";
  };

  return (
    <div className="communities-collection">
      <Message hidden={error === ""} negative>
        <Grid container>
          <Grid.Column width={15} textAlign="left">
            <strong>{error}</strong>
          </Grid.Column>
        </Grid>
      </Message>
      <Grid>
        <Grid.Row>
          <Grid.Column as="section" mobile={16} tablet={16} computer={16}>
            <TextField
              required
              fluid
              fieldPath="title"
              label={
                <FieldLabel htmlFor="title" icon="header" label={i18next.t("Title")} />
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
                <FieldLabel htmlFor="slug" icon="linkify" label={i18next.t("Slug")} />
              }
            />
            <Form.Field required>
              <FieldLabel
                htmlFor="search_query"
                icon="search"
                label={i18next.t("Search Query")}
              />
              <Form.Group>
                <Form.Input
                  id="search_query"
                  name="search_query"
                  value={values.search_query}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.search_query && errors.search_query}
                  width={13}
                />
                <Form.Field width={3}>
                  <Button
                    type="button"
                    fluid
                    onClick={(e) => {
                      e.preventDefault();
                      onTest(values);
                    }}
                  >
                    {i18next.t("Test Query")}
                  </Button>
                </Form.Field>
              </Form.Group>
            </Form.Field>
          </Grid.Column>
        </Grid.Row>
      </Grid>

      {testQueryResult !== null && (
        <Message
          hidden={testQueryResult === null}
          positive={testQuerySuccess === true && testQueryResult > 0}
          neutral={testQuerySuccess === true && testQueryResult === 0}
          negative={testQuerySuccess === false}
          className="rel-mb-2"
        >
          {testQuerySuccess === true
            ? i18next.t("Total Hits: ") + testQueryResult
            : testQueryResult}
          {testQuerySuccess === true && testQueryHits.length > 0 && (
            <div className="rel-mt-1">
              <em>
                {i18next.t("Showing")} {testQueryHits.length}{" "}
                {i18next.t("example results:")}
              </em>
            </div>
          )}
          {testQuerySuccess === true && (
            <Message.List>
              {testQueryHits.map((hit, index) => (
                <Message.Item key={index}>{hit["metadata"]["title"]}</Message.Item>
              ))}
            </Message.List>
          )}
          {testQuerySuccess === true && testQueryResult > 0 && community && (
            <div className="rel-mt-1">
              <Button
                as="a"
                href={`/communities/${community.slug}/records?q=${encodeURIComponent(
                  buildFullSearchQuery(values.search_query)
                )}`}
                target="_blank"
                rel="noopener noreferrer"
                icon="external"
                content={i18next.t("View Full Results")}
                size="small"
              />
            </div>
          )}
        </Message>
      )}
    </div>
  );
};

CollectionFormInner.propTypes = {
  handleCancel: PropTypes.func.isRequired,
  onFormReady: PropTypes.func,
  onTest: PropTypes.func.isRequired,
  testQueryResult: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  testQuerySuccess: PropTypes.bool,
  testQueryHits: PropTypes.array,
  error: PropTypes.string,
  slugGeneration: PropTypes.bool,
  community: PropTypes.object,
  parentQuery: PropTypes.string,
};

CollectionFormInner.defaultProps = {
  onFormReady: undefined,
  testQueryResult: null,
  testQuerySuccess: null,
  testQueryHits: [],
  error: "",
  slugGeneration: false,
  community: null,
  parentQuery: null,
};

const CollectionForm = ({
  initialValues,
  validationSchema,
  onSubmit,
  onTest,
  handleCancel,
  testQueryResult,
  testQuerySuccess,
  testQueryHits,
  error,
  slugGeneration,
  community,
  parentQuery,
  onFormReady,
}) => (
  <BaseForm
    onSubmit={onSubmit}
    formik={{
      initialValues,
      validationSchema,
      validateOnChange: false,
      validateOnBlur: false,
    }}
  >
    <CollectionFormInner
      handleCancel={handleCancel}
      onFormReady={onFormReady}
      onTest={onTest}
      testQueryResult={testQueryResult}
      testQuerySuccess={testQuerySuccess}
      testQueryHits={testQueryHits}
      error={error}
      slugGeneration={slugGeneration}
      community={community}
      parentQuery={parentQuery}
    />
  </BaseForm>
);

CollectionForm.propTypes = {
  initialValues: PropTypes.object.isRequired,
  validationSchema: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onTest: PropTypes.func.isRequired,
  handleCancel: PropTypes.func.isRequired,
  testQueryResult: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  testQuerySuccess: PropTypes.bool,
  testQueryHits: PropTypes.array,
  error: PropTypes.string,
  slugGeneration: PropTypes.bool,
  community: PropTypes.object,
  parentQuery: PropTypes.string,
  onFormReady: PropTypes.func,
};

CollectionForm.defaultProps = {
  testQueryResult: null,
  testQuerySuccess: null,
  testQueryHits: [],
  error: "",
  slugGeneration: false,
  community: null,
  parentQuery: null,
  onFormReady: undefined,
};

export default CollectionForm;
