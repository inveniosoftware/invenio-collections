# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 CERN.
# Copyright (C) 2025 Ubiquity Press.
# Copyright (C) 2025 Graz University of Technology.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#
"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from io import BytesIO

import pytest
from invenio_access.permissions import system_identity
from invenio_app.factory import create_app as _create_app
from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_users_resources.proxies import current_users_service
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_base.blueprints": [
            "mock_module = tests.mock_module.blueprint:create_ui_blueprint",
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_app


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture."""
    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )
    # Variable not used. We set it to silent warnings
    app_config["JSONSCHEMAS_HOST"] = "not-used"
    app_config["THEME_FRONTPAGE"] = False

    return app_config


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "dataset",
            "icon": "table",
            "props": {
                "csl": "dataset",
                "datacite_general": "Dataset",
                "datacite_type": "",
                "openaire_resourceType": "21",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Dataset",
                "subtype": "",
                "type": "dataset",
                "marc21_type": "dataset",
                "marc21_subtype": "",
            },
            "title": {"en": "Dataset"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def minimal_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "pids": {},
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    }
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "publication_date": "2020-06-01",
            # because DATACITE_ENABLED is True, this field is required
            "publisher": "Acme Inc",
            "resource_type": {"id": "dataset"},
            "title": "A Romans story",
        },
    }


@pytest.fixture()
def uploader(UserFixture, app, database):
    """Uploader."""
    u = UserFixture(
        email="uploader@inveniosoftware.org",
        password="uploader",
        preferences={
            "visibility": "public",
            "email_visibility": "restricted",
        },
        active=True,
        confirmed=True,
    )
    u.create(app, database)
    current_users_service.indexer.process_bulk_queue()
    current_users_service.record_cls.index.refresh()
    database.session.commit()

    return u


@pytest.fixture(scope="function")
def record_factory(db, uploader, minimal_record, community, resource_type_v, location):
    """Creates a record that belongs to a community."""

    class RecordFactory:
        """Test record class."""

        def create_record(
            self,
            record_dict=minimal_record,
            uploader=uploader,
            community=community,
            file=None,
        ):
            """Creates new record that belongs to the same community."""
            service = current_rdm_records_service
            files_service = service.draft_files
            idty = uploader.identity
            # create draft
            if file:
                record_dict["files"] = {"enabled": True}
            draft = service.create(idty, record_dict)

            # add file to draft
            if file:
                files_service.init_files(idty, draft.id, data=[{"key": file}])
                files_service.set_file_content(
                    idty, draft.id, file, BytesIO(b"test file")
                )
                files_service.commit_file(idty, draft.id, file)

            # publish and get record
            result_item = service.publish(idty, draft.id)
            record = result_item._record
            if community:
                # add the record to the community
                community_record = community._record
                record.parent.communities.add(community_record, default=False)
                record.parent.commit()
                db.session.commit()
                service.indexer.index(record, arguments={"refresh": True})

            return record

    return RecordFactory()


@pytest.fixture(scope="module")
def community_service(app):
    """Community service."""
    return current_communities.service


@pytest.fixture(scope="module")
def minimal_community():
    """Minimal community metadata."""
    return {
        "access": {
            "visibility": "public",
            "members_visibility": "public",
            "record_submission_policy": "open",
        },
        "slug": "public",
        "metadata": {
            "title": "My Community",
        },
    }


@pytest.fixture(scope="module")
def community_owner(UserFixture, app, database):
    """Community owner."""
    u = UserFixture(
        email="community_owner@inveniosoftware.org",
        password="community_owner",
        preferences={
            "visibility": "public",
            "email_visibility": "restricted",
        },
        active=True,
        confirmed=True,
    )
    u.create(app, database)
    current_users_service.indexer.process_bulk_queue()
    current_users_service.record_cls.index.refresh()
    database.session.commit()
    return u


@pytest.fixture(scope="module")
def community(community_service, community_owner, minimal_community, location):
    """A community."""
    c = community_service.create(community_owner.identity, minimal_community)
    Community.index.refresh()
    community_owner.refresh()
    return c
