##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from BTrees.IFBTree import IFBTree

from zope import interface, event, component
from zope.app.catalog import catalog
from zope.app.component.hooks import getSite
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getAdapter, getAdapters
from zope.proxy import removeAllProxies
from zope.lifecycleevent import ObjectCreatedEvent
from zc.catalog.catalogindex import ValueIndex

from zojax.catalog.index import DateTimeValueIndex
from zojax.catalog.interfaces import ICatalogIndexFactory
from zojax.catalog.result import ResultSet
from zojax.catalog.utils import getAccessList

from interfaces import IAcknowledgementsCatalog, IAcknowledgements


class AcknowledgementsCatalog(catalog.Catalog):
    interface.implements(IAcknowledgementsCatalog)

    def createIndex(self, name, factory):
        index = factory()
        event.notify(ObjectCreatedEvent(index))
        self[name] = index

        return self[name]

    def getIndex(self, indexId):
        if indexId in self:
            return self[indexId]

        return self.createIndex(
            indexId, getAdapter(self, ICatalogIndexFactory, indexId))

    def getIndexes(self):
        names = []

        for index in self.values():
            names.append(removeAllProxies(index.__name__))
            yield index

        for name, indexFactory in getAdapters((self,), ICatalogIndexFactory):
            if name not in names:
                yield self.createIndex(name, indexFactory)

    def clear(self):
        for index in self.getIndexes():
            index.clear()

    def index_doc(self, docid, texts):
        for index in self.getIndexes():
            index.index_doc(docid, texts)

    def unindex_doc(self, docid):
        for index in self.getIndexes():
            index.unindex_doc(docid)

    def updateIndexes(self):
        indexes = list(self.getIndexes())

        for uid, obj in self._visitSublocations():
            for index in indexes:
                index.index_doc(uid, obj)

    def _visitSublocations(self):
        configlet = getUtility(IAcknowledgements)

        for uid, record in removeAllProxies(configlet).records.items():
            yield uid, record

    def search(self, object=None, **kw): # , contexts=()

        ids = getUtility(IIntIds)

        query = dict(kw)

        # records for object
        if object is not None:
            if type(object) is not type({}):
                oid = ids.queryId(removeAllProxies(object))
                if oid is None:
                    return ResultSet(IFBTree(), getUtility(IAcknowledgements))

                query['object'] = {'any_of': (oid,)}
            else:
                query['object'] = object

        # context
        # if not contexts:
        #     contexts = (getSite(),)

        # c = []
        # for context in contexts:
        #     id = ids.queryId(removeAllProxies(context))
        #     if id is not None:
        #         c.append(id)

        # query['contexts'] = {'any_of': c}

        return ResultSet(self.apply(query), getUtility(IAcknowledgements))


def getCatalog():
    sm = getSite().getSiteManager()

    if 'acknowledgementsCatalog' in sm:
        return sm['acknowledgementsCatalog']

    else:
        catalog = AcknowledgementsCatalog()
        event.notify(ObjectCreatedEvent(catalog))
        removeAllProxies(sm)['acknowledgementsCatalog'] = catalog
        return sm['acknowledgementsCatalog']


@component.adapter(IAcknowledgementsCatalog, IObjectAddedEvent)
def handleCatalogAdded(catalog, ev):
    catalog['principal'] = ValueIndex('principal')
    catalog['date'] = DateTimeValueIndex('date', resolution=4)
    catalog['object'] = ValueIndex('value', IndexableObject)
    # catalog['contexts'] = SetIndex('value', IndexableContexts)


class Factory(object):
    component.adapts(IAcknowledgementsCatalog)
    interface.implements(ICatalogIndexFactory)

    def __init__(self, catalog):
        self.catalog = catalog


class IndexableSecurityInformation(object):

    def __init__(self, item, default=None):
        self.value = getAccessList(removeAllProxies(item.content), 'zope.View')


# class IndexableContexts(object):

#     def __init__(self, item, default=None):
#         values = []
#         ids = getUtility(IIntIds)

#         context = removeAllProxies(item.content)
#         while context is not None:
#             values.append(ids.queryId(context))

#             context = removeAllProxies(
#                 getattr(context, '__parent__', None))

#         self.value = values


class IndexableObject(object):

    def __init__(self, item, default=None):
        try:
            self.value = getUtility(IIntIds).getId(
                removeAllProxies(item.object))
        except:
            self.value = default


class PrincipalIndex(Factory):
    def __call__(self):
        return ValueIndex('principal')


class DateIndex(Factory):
    def __call__(self):
        return DateTimeValueIndex('date', resolution=4)


class ObjectIndex(Factory):
    def __call__(self):
        return ValueIndex('value', IndexableObject)


# class ContextsIndex(Factory):
#     def __call__(self):
#         return SetIndex('value', IndexableContexts)
