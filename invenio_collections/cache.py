# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2012, 2014, 2015 CERN.
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

"""Implementation of collections caching."""

import warnings

from sqlalchemy import event
from werkzeug.utils import cached_property

from invenio_base.globals import cfg
from invenio_ext.cache import cache

from invenio_access.control import acc_get_action_id
from invenio_access.engine import acc_authorize_action
from invenio_access.models import AccAuthorization, AccARGUMENT

from .models import Collection, Collectionname


def get_collection_allchildren(coll, recreate_cache_if_needed=True):
    """Return the list of all children of a collection."""
    warnings.warn('get_collection_allchildren has been deprecated.',
                  DeprecationWarning)
    return []


def get_collection_nbrecs(coll):
    """Return number of records in collection."""
    warnings.warn('get_collection_nbrecs has been deprecated.',
                  DeprecationWarning)
    return 0


@cache.memoize()
def get_restricted_collections():
    from invenio_access.local_config import VIEWRESTRCOLL
    VIEWRESTRCOLL_ID = acc_get_action_id(VIEWRESTRCOLL)

    return [auth[0] for auth in AccAuthorization.query.join(
        AccAuthorization.argument
    ).filter(
        AccARGUMENT.keyword == 'collection',
        AccAuthorization.id_accACTION == VIEWRESTRCOLL_ID
    ).values(AccARGUMENT.value)]


class RestrictedCollections(object):

    @property
    def cache(self):
        warnings.warn('restricted_collection_cache has been deprecated.',
                      DeprecationWarning)
        return get_restricted_collections()

    def recreate_cache_if_needed(self):
        warnings.warn('restricted_collection_cache has been deprecated.',
                      DeprecationWarning)

restricted_collection_cache = RestrictedCollections()


def get_permitted_restricted_collections(user_info):
    """Return a list of restricted collection with user is authorization."""
    from invenio_access.local_config import VIEWRESTRCOLL
    restricted_collections = get_restricted_collections()

    ret = []

    auths = acc_authorize_action(
        user_info,
        VIEWRESTRCOLL,
        batch_args=True,
        collection=restricted_collections
    )

    for collection, auth in zip(restricted_collections, auths):
        if auth[0] == 0:
            ret.append(collection)
    return ret


@event.listens_for(AccARGUMENT, 'after_insert')
@event.listens_for(AccARGUMENT, 'after_update')
@event.listens_for(AccARGUMENT, 'after_delete')
@event.listens_for(AccAuthorization, 'after_insert')
@event.listens_for(AccAuthorization, 'after_update')
@event.listens_for(AccAuthorization, 'after_delete')
def clear_restricted_collections_cache(mapper, connection, target):
    """Clear cache after modification of access rights."""
    cache.delete_memoized(get_restricted_collections)


def collection_restricted_p(collection, **kwargs):
    return collection in get_restricted_collections()


@cache.memoize()
def get_i18n_collection_names():
    """Return I18N collection names.

    This function is not to be used directly; use function
    get_coll_i18nname() instead.
    """
    # TODO Consider storing cache per collection to avaid large data transfers
    # between Redis and web node.
    res = Collection.query.join(
        Collection.collection_names
    ).filter(Collectionname.type == 'ln').values(
        Collection.name, 'ln', 'value'
    )
    ret = {}
    for c, ln, i18nname in res:
        if i18nname:
            if c not in ret:
                ret[c] = {}
            ret[c][ln] = i18nname
    return ret


@event.listens_for(Collectionname, 'after_insert')
@event.listens_for(Collectionname, 'after_update')
@event.listens_for(Collectionname, 'after_delete')
def clear_collection_names_cache(mapper, connection, target):
    """Clear caches connected to Collectionname table."""
    cache.delete_memoized(get_i18n_collection_names)


def get_coll_i18nname(c, ln=None):
    """Return nicely formatted collection name for given language.

    This function uses collection_i18nname_cache, but it verifies
    whether the cache is up-to-date first by default.  This
    verification step is performed by checking the DB table update
    time.  So, if you call this function 1000 times, it can get very
    slow because it will do 1000 table update time verifications, even
    though collection names change not that often.

    Hence the parameter VERIFY_CACHE_TIMESTAMP which, when set to
    False, will assume the cache is already up-to-date.  This is
    useful namely in the generation of collection lists for the search
    results page.
    """
    ln = ln or cfg['CFG_SITE_LANG']
    return get_i18n_collection_names().get(c, {}).get(ln, c)
