"""Mock extension for collections tests."""

from unittest.mock import MagicMock

from flask import current_app
from werkzeug.local import LocalProxy

from invenio_collections.resources.config import CollectionsResourceConfig
from invenio_collections.resources.resource import CollectionsResource
from invenio_collections.services.config import CollectionServiceConfig
from invenio_collections.services.service import CollectionsService

current_mock_collections = LocalProxy(
    lambda: current_app.extensions["mock-collections"]
)


class MockCollectionsExt:
    """Mock extension that wires the collections service and resource."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize service and resource on the collections extension."""
        self.service = CollectionsService(
            config=CollectionServiceConfig.build(app),
            records_service=MagicMock(),
        )
        self.resource = CollectionsResource(
            service=self.service,
            config=CollectionsResourceConfig.build(app),
        )

        app.extensions["mock-collections"] = self


def create_bp(app):
    """Create the collections API blueprint."""
    return app.extensions["mock-collections"].resource.as_blueprint()
