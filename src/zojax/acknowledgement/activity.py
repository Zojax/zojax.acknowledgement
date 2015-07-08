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
from zope import interface
from zope.component import getUtility

from zojax.activity.interfaces import IActivity, IActivityRecordDescription
from zojax.content.activity.interfaces import IContentActivityRecord
from zojax.content.activity.record import ContentActivityRecord

from interfaces import _, IAcknowledgementActivityRecord


class AcknowledgementActivityRecord(ContentActivityRecord):
    interface.implements(IAcknowledgementActivityRecord, IContentActivityRecord)

    type = u'acknowledgement'
    verb = _('enable Acknowledgement')


class AcknowledgementActivityRecordDescription(object):
    interface.implements(IActivityRecordDescription)

    title = _(u'Acknowledgement')
    description = _(u'Acknowledgement was enabled for Content object.')


def acknowledgementAddedHandler(content):
    getUtility(IActivity).add(content, AcknowledgementActivityRecord())
