# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Collections is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections celery tasks."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db import db

from .proxies import current_collections


@shared_task(ignore_result=True)
def update_collections_size():
    """Calculate and update the size of all the collections."""
    collections_service = current_collections.service
    res = collections_service.read_all(system_identity, depth=0)
    for citem in res:
        try:
            collection = citem._collection
            res = collections_service.search_collection_records(
                system_identity, collection
            )
            # Update num_records directly on the model since it's dump_only in schema
            collection.update(num_records=res.total)
            db.session.commit()
        except Exception as e:
            current_app.logger.exception(str(e))
