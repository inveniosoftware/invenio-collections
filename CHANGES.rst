..
    Copyright (C) 2015-2026 CERN.
    Copyright (C) 2025 Ubiquity Press.
    Copyright (C) 2025-2026 Graz University of Technology.

    Invenio-Collections is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version v8.1.1 (released 2026-04-28)

- fix: correct URL for collection

Version v8.1.0 (released 2026-04-08)

- breaking(ext): service and resource initialization removed from
  ``InvenioCollections.init_app``. Consuming modules (e.g.
  ``invenio-rdm-records``, ``invenio-app-rdm``) are now responsible for
  constructing and wiring ``CollectionsService`` and ``CollectionsResource``
- breaking(service): ``CollectionsService.__init__`` now requires a
  ``records_service`` keyword argument. The hard dependency on
  ``invenio-rdm-records`` proxy is removed
- breaking(resource): ``CollectionsResourceConfig`` no longer includes the
  ``UIJSONSerializer`` response handler. RDM-specific serialization is
  provided by ``RDMCollectionsResourceConfig`` in ``invenio-rdm-records``
- breaking(tasks): ``update_collections_size`` Celery task and its registration
   moved to ``invenio_rdm_records.collections.tasks``
- breaking(entrypoints): ``invenio_base.api_blueprints`` entry point removed.
  Blueprint registration is now the responsibility of the consuming module
- breaking(dependencies): ``invenio-rdm-records`` removed from package
  dependencies

Version v8.0.2 (released 2026-04-02)

- chore(translations): populate boilderplate for translations

Version v8.0.1 (released 2026-04-02)

- fix(translations): add package-lock.json so the pypi-publish workflow
  can run ``npm ci`` in the translations directory

Version v8.0.0 (released 2026-04-02)

- breaking(api): rename ``community_id`` to ``namespace_id`` across the service,
  resource, and data model to decouple collections from invenio-communities;
  includes an Alembic migration to rename the column
- breaking(config): permission policy is now resolved via
  ``COLLECTIONS_PERMISSION_POLICY``; standalone deployments fall back to a
  system-process-only default
- feat(service): add tree and collection reordering endpoints with batch
  update support
- feat(service): enforce configurable limits on trees per namespace,
  collections per tree, and maximum nesting depth
- feat(ui): add full CRUD settings UI for managing collection trees and
  collections, including create, edit, delete, reorder, and drag-and-drop
- feat(ui): add i18n infrastructure and translation scaffolding
- feat(ui): add ESLint with ``@inveniosoftware/eslint-config-invenio`` and
  JS linter GitHub Actions job
- fix(results): include ``slug`` in breadcrumb data so templates can build
  URLs without relying on ``self_html``

Version v7.0.0 (released 2026-03-20)

- change(setup): upgrade invenio-rdm-records, invenio-checks

Version v6.0.0 (released 2026-03-18)

- change(setup): upgrade invenio-rdm-records, communities, jobs

Version v5.0.1 (released 2026-03-17)

- fix(setup):  remove unused administration dependency

Version v5.0.0 (released 2026-03-10)

- change(setup): upgrade invenio-collections, invenio-rdm-records

Version v4.0.0 (released 2026-02-03)

- chore(black): update formatting to >= 26.0
- chore(setup): bump dependencies
- refactor: use Timestamp from db
- refactor!: replace Link usage by EndpointLink

Version v3.0.1 (released 2025-12-15)

- revert alembic revision_id to invenio-rdm-records

Version v3.0.0 (released 2025-12-12)

- chore(pyproject): bump major versions of invenio-communities and invenio-rdm-records

Version v2.1.0 (released 2025-10-21)

- setup: bump major dependencies

Version v2.0.0 (released 2025-09-24)

- installation: bump communities and rdm-records

Version 1.0.0 (release 2025-08-01)

- setup: bump major dependencies

Version 0.5.0 (release 2025-06-03)

- setup: bump major dependencies
- fix(tests): add configuration

Version 0.4.0 (release 2025-05-30)
-----------------------------------

- Package refactoring for Invenio RDM
- Migrate collection content from Invenio-RDM-Records

Version 1.0.0a4 (released 2017-09-04)
-------------------------------------

- Package refactoring for Invenio 3.

Version 0.3.0 (released 2015-10-09)
-----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Moves automatically loaded rule for MARC field 980 to
  contrib/dojson.py and adds the corresponding entry point for it so
  dojson can collect it.

Version 0.2.0 (released 2015-10-05)
-----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Removes `recordext/functions` folder in favor of `invenio-records`.
- Removes legacy search extensions.
- Deprecates usage of `restricted_collection_cache`.
- Replaces legacy DataCachers with functions decorated by memoize
  method from Flask-Cache.  (#7)

New features
~~~~~~~~~~~~

- Ports get_permitted_restricted_collections function from
  `invenio_search` package.
- Adds simple admin interface to edit collection name and query. (#1)

Bug fixes
~~~~~~~~~

- Upgrades invenio-base minimum version to 0.3.0 and fixes an
  incorrect import.
- Removes calls to PluginManager consider_setuptools_entrypoints()
  removed in PyTest 2.8.0.
- Adds validation for collection names. Validation will be performed
  each time the name is set. (#10)
- Adds missing `invenio_base` dependency.
- Moves upgrade recipes into the right folder to be auto discovered.

Version 0.1.2 (released 2015-09-04)
-----------------------------------

- Adds `_collections` key upon record update.
- Adds missing `invenio_access` dependency and amends past upgrade
  recipes following its separation into standalone package.

Version 0.1.1 (released 2015-08-25)
-----------------------------------

- Adds missing `invenio_upgrader` dependency and amends past upgrade
  recipes following its separation into standalone package.

Version 0.1.0 (released 2015-08-19)
-----------------------------------

- Initial public release.
