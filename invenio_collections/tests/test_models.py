# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""Model test cases."""

from invenio_base.wrappers import lazy_import

from invenio_testing import InvenioTestCase

Collection = lazy_import('invenio_collections.models:Collection')
cfg = lazy_import('invenio_base.globals:cfg')


class ModelsTestCase(InvenioTestCase):

    """Test model classes."""

    def test_collection_name_validation(self):
        """Test Collection class' name validation."""
        c = Collection()
        test_name = cfg['CFG_SITE_NAME'] + ' - not site name'

        # Name can't contain '/' characters
        with self.assertRaises(ValueError):
            c.name = 'should/error'

        # Name should equal the site name if the collection is a root
        c.id = 1
        self.assertTrue(c.is_root)
        with self.assertWarns(UserWarning):
            c.name = test_name
        # Root node's name can equal site name
        try:
            with self.assertWarns(UserWarning):
                c.name = cfg['CFG_SITE_NAME']
        except AssertionError:
            pass

        # Name can't equal the site name if not root collection
        c.id = 2
        self.assertFalse(c.is_root)
        with self.assertRaises(ValueError):
            c.name = cfg['CFG_SITE_NAME']

        # Assigning should work in other cases
        c.name = test_name
        self.assertEquals(c.name, test_name)
