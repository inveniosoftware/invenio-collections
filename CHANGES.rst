..
    This file is part of Invenio.
    Copyright (C) 2015 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

Changes
=======

Version 0.1.0 (released TBD)
----------------------------

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
