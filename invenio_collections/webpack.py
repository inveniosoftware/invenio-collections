# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

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
                "formik": "^2.4.9",
                "i18next": "^20.3.0",
                "i18next-browser-languagedetector": "^6.1.0",
                "lodash": "^4.17.0",
                "prop-types": "^15.7.0",
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "react-i18next": "^11.11.0",
                "react-invenio-forms": "^5.0.0-alpha.3",
                "semantic-ui-css": "^2.5.0",
                "semantic-ui-react": "^3.0.0-beta.2",
                "yup": "^0.32.11",
            },
            aliases={
                "@js/invenio_collections": "js/invenio_collections",
                "@translations/invenio_collections": "translations/invenio_collections",
            },
        ),
    },
)
