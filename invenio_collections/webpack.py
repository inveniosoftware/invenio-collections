# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2026 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS bundles for invenio-collections."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "invenio-collections-settings": "./js/invenio_collections/collections/index.js",
            },
            dependencies={
                "@semantic-ui-react/css-patch": "^1.0.0",
                "axios": "^1.7.7",
                "formik": "^2.1.0",
                "i18next": "^20.3.0",
                "i18next-browser-languagedetector": "^6.1.0",
                "lodash": "^4.17.0",
                "prop-types": "^15.7.0",
                "react": "^16.13.0",
                "react-dom": "^16.13.0",
                "react-i18next": "^11.11.0",
                "react-invenio-forms": "^4.0.0",
                "semantic-ui-css": "^2.4.0",
                "semantic-ui-react": "^2.1.0",
                "yup": "^0.32.11",
            },
            aliases={
                "@js/invenio_collections": "js/invenio_collections",
                "@translations/invenio_collections": "translations/invenio_collections",
            },
        ),
    },
)
