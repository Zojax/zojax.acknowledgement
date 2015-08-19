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
from zope import interface, component
from zope.security import checkPermission
from zope.traversing.browser import absoluteURL

from zojax.content.actions.contentactions import ContentAction
from zojax.content.actions.categories import ActionCategory

from ..interfaces import _, IContentWithAcknowledgement
from ..interfaces import IContentAcknowledgementAware

from interfaces import IAcknowledgementsAction, INoAcknowledgementsAction
from interfaces import IContentAcknowledgementsCategory


ContentAcknowledgements = ActionCategory(
    _(u'Acknowledgements'), 25, IContentAcknowledgementsCategory)


class AcknowledgementsAction(ContentAction):
    interface.implements(IAcknowledgementsAction)
    component.adapts(IContentWithAcknowledgement, interface.Interface)

    title = _('Acknowledged users')
    permission = 'zojax.ModifyContent'
    weight = 900

    @property
    def url(self):
        return u'%s/acknowledged.html' % absoluteURL(
            self.context, self.request)

    def isAvailable(self):
        if IContentAcknowledgementAware.providedBy(self.context) and \
                checkPermission('zojax.ModifyContent', self.context):
            return True

        return False


class NoAcknowledgementsAction(ContentAction):
    interface.implements(INoAcknowledgementsAction)
    component.adapts(IContentWithAcknowledgement, interface.Interface)

    title = _('Not acknowledged users')
    permission = 'zojax.ModifyContent'
    weight = 900

    @property
    def url(self):
        return u'%s/not-acknowledged.html' % absoluteURL(
            self.context, self.request)

    def isAvailable(self):
        if IContentAcknowledgementAware.providedBy(self.context) and \
                checkPermission('zojax.ModifyContent', self.context):
            return True

        return False
