# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Minimal Flask application example for development.

1. In this example, we will need to convert from XML to MARC21 so we will use
   DoJson tool. You need to install it from Pypi.

.. code-block:: console

    $ pip install dojson


2. You will also need Invenio-Search in order to perform searches inside the
   records.

.. code-block:: console

    $ pip install invenio-search>=1.0.0a3


2. Create the database and tables:

.. code-block:: console

    $ cd examples
    $ flask -a app.py db init
    $ flask -a app.py db create

You can find the database in `examples/app.db`.


3. Create a root collection using the CLI. This collection will become
   the root of new tree by default:

.. code-block:: console

    $ flask -a app.py collections create demo


4. Create a sub-collection with a query to show only the collections of
   'primary' INSTITUTE:

.. code-block:: console

    $ flask -a app.py collections create institutes -p demo \
      -q 'collections.primary:INSTITUTE'


5. Create a sub-collection with a query to show only the nuclear research
   centers whose parent is `institutes`:

.. code-block:: console

    $ flask -a app.py collections create experiments -p institutes \
      -q 'citation_references_note.name_of_source:Experimentelle'


6. Look for a MARC21 file. In our case, we are going to use `authority.xml`
   which is included in the package `invenio_records`.

.. code-block:: console

    $ demomarc21pathname=$(echo "from __future__ import print_function; \
      import pkg_resources; \
      print(pkg_resources.resource_filename('invenio_records', \
      'data/marc21/authority.xml'))" | python)


7. Transform the file `authority.xml` (Path stored in `demomarc21pathname`
   variable) from MARC21 to a json file:

.. code-block:: console

    $ dojson -i $demomarc21pathname -l marcxml do marc21 > records.json


8. Load the file in the application importing the json file:

.. code-block:: console

    $ flask -a app.py records create < records.json


9. Launch the web server:

.. code-block:: console

    $ flask -a app.py run


10. Open in a browser the URL `http://127.0.0.1:5000/?collection=COLLECTION`
   where `COLLECTION` is the name of some collection previously created
   (`demo`, `institutes`, `experiments`)
"""

from __future__ import absolute_import, print_function

import os

from flask import Flask, jsonify, request
from flask_cli import FlaskCLI
from invenio_db import InvenioDB
from invenio_records import InvenioRecords
from invenio_search import InvenioSearch

from invenio_collections import InvenioCollections
from invenio_collections.models import Collection

# Create Flask application
app = Flask(__name__)
app.config.update(
    SEARCH_ELASTIC_KEYWORD_MAPPING={None: ['_all']},
    SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI',
                                      'sqlite:///app.db'),
)

FlaskCLI(app)
InvenioDB(app)
InvenioRecords(app)
InvenioCollections(app)
search = InvenioSearch(app)


# Checking that the register record signal is enabled in collections.
assert app.config.get('COLLECTIONS_REGISTER_RECORD_SIGNALS')


@app.route('/', methods=['GET'])
def index():
    """Query Elasticsearch using "collection" param in query string."""
    collection_names = request.values.getlist('collection')

    # Validation of collection names.
    collections = Collection.query
    if collection_names:
        collections = collections.filter(
            Collection.name.in_(collection_names))
    assert len(collection_names) == collections.count()

    response = search.client.search(
        body={
            'query': {
                'filtered': {
                    'filter': {
                        'terms': {
                            '_collections': collection_names
                        }
                    }
                }
            }
        }
    )
    return jsonify(**response)
