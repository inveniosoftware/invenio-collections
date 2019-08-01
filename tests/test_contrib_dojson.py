# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
