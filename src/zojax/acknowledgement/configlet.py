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
import random
import BTrees

from zope import interface, event, component
from zope.app.intid.interfaces import IIntIds, IIntIdRemovedEvent
from zope.component import getUtility, getMultiAdapter, ComponentLookupError
from zope.proxy import removeAllProxies
from zope.publisher.browser import TestRequest

from zojax.authentication.interfaces import IPrincipalRemovingEvent
from zojax.catalog.utils import getRequest
from zojax.mailtemplate.interfaces import IMailTemplate

from catalog import AcknowledgementsCatalog
from interfaces import IAcknowledgements, IContentAcknowledgementAware
from interfaces import IAcknowledgementAddedEvent, IContentAcknowledgement
from interfaces import IAcknowledgementRemovedEvent


class AcknowledgementConfiglet(object):
    interface.implements(IAcknowledgements)

    family = BTrees.family32

    _v_nextid = None
    _randrange = random.randrange

    @property
    def records(self):
        data = self.data.get('records')
        if data is None:
            data = self.family.IO.BTree()
            self.data['records'] = data
        return data

    @property
    def catalog(self):
        catalog = self.data.get('catalog')
        if catalog is None:
            catalog = AcknowledgementsCatalog()
            self.data['catalog'] = catalog
        return catalog

    def _generateId(self):
        records = self.records

        while True:
            if self._v_nextid is None:
                self._v_nextid = self._randrange(0, self.family.maxint)

            id = self._v_nextid
            self._v_nextid += 1

            if id not in records:
                return id

            self._v_nextid = None

    def search(self, **kw):
        return self.catalog.search(**kw)

    def objectRecords(self, object):
        return self.catalog.search(object=object)

    def updateObjectRecords(self, object):
        catalog = self.catalog

        for record in catalog.search(object=object):
            catalog.index_doc(record.id, record)

    def getObject(self, id):
        return self.records[id]

    def add(self, record):

        if record.oid is None:
            return

        object = getUtility(IIntIds).queryObject(record.oid)

        if not IContentAcknowledgementAware.providedBy(object):
            return

        record.id = self._generateId()

        self.records[record.id] = record
        self.catalog.index_doc(record.id, record)

        event.notify(AcknowledgementAddedEvent(object, record))

    def remove(self, rid):
        records = self.records

        record = records[rid]
        event.notify(AcknowledgementRemovedEvent(record.object, record))
        self.catalog.unindex_doc(rid)
        del records[rid]

    def removeObject(self, object):
        records = self.records

        for rid in self.catalog.search(object).uids:
            event.notify(
                AcknowledgementRemovedEvent(object, records[rid]))

            self.catalog.unindex_doc(rid)
            del records[rid]

    def verifyRecord(self, uid, oid=None, object=None):

        if oid:
            object = getUtility(IIntIds).queryObject(oid)

        result = self.catalog.search(object=object,
                                     principal={'any_of': (uid,)})

        if len(result) > 0:
            return result[0]

        return False


class AcknowledgementEvent(object):

    def __init__(self, object, record):
        self.object = object
        self.record = record


class AcknowledgementAddedEvent(AcknowledgementEvent):
    interface.implements(IAcknowledgementAddedEvent)


class AcknowledgementRemovedEvent(AcknowledgementEvent):
    interface.implements(IAcknowledgementRemovedEvent)


@component.adapter(IContentAcknowledgementAware, IIntIdRemovedEvent)
def objectRemovingHandler(object, ev):
    removeAllProxies(getUtility(IAcknowledgements)).removeObject(object)


@component.adapter(IPrincipalRemovingEvent)
def principalRemovingHandler(event):
    catalog = getUtility(IAcknowledgements)
    for record in catalog.search(principal={'any_of': (event.principal.id,)}):
        catalog.remove(record.id)


@component.adapter(IContentAcknowledgementAware, IAcknowledgementAddedEvent)
def acknowledgementAddedHandler(object, ev):
    obj = IContentAcknowledgement(object)
    if not obj:
        return

    emails = obj.emails_list
    if not emails:
        return

    try:
        template = getMultiAdapter((ev.record, getRequest()),
                                   IMailTemplate,
                                   'html')
    except ComponentLookupError:
        template = getMultiAdapter((ev.record, TestRequest()),
                                   IMailTemplate,
                                   'html')
    template.send(emails)
