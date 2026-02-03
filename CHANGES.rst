..
    Copyright (C) 2015 CERN.
    Copyright (C) 2025 Ubiquity Press.
    Copyright (C) 2025-2026 Graz University of Technology.

    Invenio-Collections is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

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
