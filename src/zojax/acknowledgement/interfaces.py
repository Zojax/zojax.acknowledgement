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
""" acknowledgement interfaces

$Id$
"""

from zope import schema, interface
from zope.component.interfaces import IObjectEvent
from zojax.content.space.interfaces import IWorkspace, IWorkspaceFactory
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('zojax.acknowledgement')


class IAcknowledgement(interface.Interface):
    """ acknowledgement item """

    id = interface.Attribute('Id')
    oid = interface.Attribute('Object Id')
    date = interface.Attribute('Date')
    principal = interface.Attribute('Principal')

    # static info
    object = interface.Attribute('Content Object')


class IAcknowledgementsCatalog(interface.Interface):
    """ acknowledgements catalog """


class IAcknowledgements(interface.Interface):
    """ acknowledgements configlet """

    records = interface.Attribute('Records')
    catalog = interface.Attribute('Catalog')

    def add(object, record):
        """ add activity record """

    def remove(rid):
        """ remove activity record """

    def removeObject(object):
        """ remove records for object """

    def objectRecords(object):
        """ return object records """

    def updateObjectRecords(object):
        """ reindex records for object """

    def search(**kw):
        """ search records """

    def getObject(id):
        """ return record by id """


class IContentAcknowledgement(interface.Interface):

    acknowledge = schema.Bool(
        title=_('Enable Acknowledgement'),
        description=_(''),
        default=False,
        required=False)


class IContentWithAcknowledgement(interface.Interface):
    """ Marker interface for content with acknowledgement. """


class IContentAcknowledgementAware(interface.Interface):
    """ Content acknowledgement aware """


class IAcknowledgementActivityRecord(interface.Interface):
    """ Acknowledgement activity record """


class IAcknowledgementEvent(IObjectEvent):
    """ content acknowledgement item event """

    record = interface.Attribute('Acknowledgement item')


class IAcknowledgementAddedEvent(IAcknowledgementEvent):
    """ item added """


class IAcknowledgementRemovedEvent(IAcknowledgementEvent):
    """ item removed """


class IPersonalAcknowledgementsWorkspace(IWorkspace):
    """ acknowledgements workspace """


class IPersonalAcknowledgementsWorkspaceFactory(IWorkspaceFactory):
    """Personal acknowledgements workspace factory."""
