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
""" zojax.acknowledgement tests

$Id$
"""
import datetime
import os
import unittest
import doctest

from forbiddenfruit import curse

from zope import interface, event
from zope.app.testing import functional
from zope.app.component.hooks import setSite
from zope.app.rotterdam import Rotterdam
from zope.app.security.interfaces import IAuthentication
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectCreatedEvent
from zope.security.management import newInteraction, endInteraction

from zojax.authentication.authentication import PluggableAuthentication
from zojax.authentication.credentials import factory as defaultCreds
from zojax.catalog.catalog import Catalog, ICatalog
from zojax.content.type.interfaces import IItem
from zojax.content.type.item import PersistentItem
from zojax.layoutform.interfaces import ILayoutFormLayer
from zojax.ownership.interfaces import IOwnership
from zojax.personal.space.manager import PersonalSpaceManager, IPersonalSpaceManager


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


AcknowledgementLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'AcknowledgementLayer', allow_teardown=True)


class IContent(IItem):
    """ content """


class Content(PersistentItem):
    interface.implements(IContent)


def FunctionalDocFileSuite(*paths, **kw):
    layer = AcknowledgementLayer

    globs = kw.setdefault('globs', {})
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')

    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        newInteraction()

        def fake_utcnow(self):
            return datetime.datetime(2015, 7, 30, 8, 0, 0)
        curse(datetime.datetime, 'utcnow', classmethod(fake_utcnow))

        root = functional.getRootFolder()
        setSite(root)
        sm = root.getSiteManager()

        # IIntIds
        root['intids'] = IntIds()
        sm.registerUtility(root['intids'], IIntIds)
        root['intids'].register(root)

        # catalog
        root['catalog'] = Catalog()
        sm.registerUtility(root['catalog'], ICatalog)

        # PluggableAuthentication
        pau = PluggableAuthentication(u'')
        event.notify(ObjectCreatedEvent(pau))
        sm[u'auth'] = pau
        sm.registerUtility(pau, IAuthentication)

        # Credentials Plugin
        defaultCreds.install()
        defaultCreds.activate()

        # people
        people = PersonalSpaceManager(title=u'People')
        event.notify(ObjectCreatedEvent(people))
        root['people'] = people
        sm.registerUtility(root['people'], IPersonalSpaceManager)

        user = sm.getUtility(IAuthentication).getPrincipal('zope.mgr')
        people.assignPersonalSpace(user)

        user = sm.getUtility(IAuthentication).getPrincipal('zope.user')
        people.assignPersonalSpace(user)

        # default content
        content = Content(u'Content1', u'Some Content1')
        event.notify(ObjectCreatedEvent(content))
        IOwnership(content).ownerId = 'zope.user'
        root['content1'] = content

        content = Content(u'Content2', u'Some Content2')
        event.notify(ObjectCreatedEvent(content))
        IOwnership(content).ownerId = 'zope.user'
        root['content2'] = content

        endInteraction()

    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')

    def tearDown(test):
        setSite(None)
        functional.FunctionalTestSetup().tearDown()
        # datetime_patcher.stop()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old|doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


def test_suite():
    return unittest.TestSuite((FunctionalDocFileSuite("../README.rst"),))
