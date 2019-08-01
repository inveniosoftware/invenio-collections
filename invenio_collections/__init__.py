# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for organizing metadata into collections."""

from __future__ import absolute_import, print_function

from .ext import InvenioCollections
from .proxies import current_collections
from .version import __version__

__all__ = ('__version__', 'InvenioCollections', 'current_collections')
