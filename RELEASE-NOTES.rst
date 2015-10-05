============================
 Invenio-Collections v0.2.0
============================

Invenio-Collections v0.2.0 was released on October 5, 2015.

About
-----

Invenio module for organizing metadata into collections.

*This is an experimental developer preview release.*

Incompatible changes
--------------------

- Removes `recordext/functions` folder in favor of `invenio-records`.
- Removes legacy search extensions.
- Deprecates usage of `restricted_collection_cache`.
- Replaces legacy DataCachers with functions decorated by memoize
  method from Flask-Cache.  (#7)

New features
------------

- Ports get_permitted_restricted_collections function from
  `invenio_search` package.
- Adds simple admin interface to edit collection name and query. (#1)

Bug fixes
---------

- Upgrades invenio-base minimum version to 0.3.0 and fixes an
  incorrect import.
- Removes calls to PluginManager consider_setuptools_entrypoints()
  removed in PyTest 2.8.0.
- Adds validation for collection names. Validation will be performed
  each time the name is set. (#10)
- Adds missing `invenio_base` dependency.
- Moves upgrade recipes into the right folder to be auto discovered.

Installation
------------

   $ pip install invenio-collections==0.2.0

Documentation
-------------

   http://invenio-collections.readthedocs.org/en/v0.2.0

Happy hacking and thanks for flying Invenio-Collections.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-collections
|   URL: http://invenio-software.org
