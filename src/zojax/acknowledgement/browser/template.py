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

from zope.app.security.interfaces import PrincipalLookupError
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser import absoluteURL

from zojax.mailtemplate.base import MailTemplateBase
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.security.utils import getPrincipal

from ..interfaces import _


class AcknowledgementAddedNotification(MailTemplateBase):

    contentType = u'text/html'
    info = dict()

    def update(self):
        super(AcknowledgementAddedNotification, self).update()

        context = self.context
        object = removeSecurityProxy(context.object)

        try:
            principal = getPrincipal(context.principal)
        except PrincipalLookupError:
            principal = ''

        profile = IPersonalProfile(principal, None)

        datetime = ''
        if context.date:
            datetime = context.date.strftime('%Y-%m-%d %H:%M UTC')

        self.info = {
            'title': object.title,
            'user': getattr(profile, 'title', 'NO NAME'),
            'datetime': datetime,
            'url': '%s/' % absoluteURL(
                object,
                self.request).replace('/++skin++JSONRPC.acknowledgement', '')
        }

    @property
    def subject(self):
        return _(u'New Acknowledgement for %s' % (self.context.object.title))
