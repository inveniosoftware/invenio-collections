# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
# -*- coding: utf-8 -*-
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Test dojson."""

import pkg_resources

try:
    pkg_resources.get_distribution('dojson')
except pkg_resources.DistributionNotFound:
    pass
else:
    from dojson.contrib.marc21 import marc21
    from dojson.contrib.to_marc21 import to_marc21

    def test_invenio_collection_marc21_tag():
        """Test invenio-collection marc21 tag."""
        source = {'980__': [{'a': 'colla'}, {'b': 'collb'}]}
        data = marc21.do(source)

        assert data['collections'][0]['primary'] == 'colla'
        assert data['collections'][1]['secondary'] == 'collb'

        original = to_marc21.do(data)
        assert source['980__'] == list(original['980__'])
