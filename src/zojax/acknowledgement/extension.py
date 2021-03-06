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
"""Hook that allow enable Acknowledgement functionality to documents.
"""

from rwproperty import getproperty, setproperty

from zope import interface
from zope.proxy import removeAllProxies

from interfaces import IContentAcknowledgementAware


class ContentAcknowledgementExtension(object):

    @getproperty
    def acknowledge(self):
        context = removeAllProxies(self.context)
        return IContentAcknowledgementAware.providedBy(context)

    @setproperty
    def acknowledge(self, value):
        context = removeAllProxies(self.context)

        if value is None or not value:
            if IContentAcknowledgementAware.providedBy(context):
                interface.noLongerProvides(context, IContentAcknowledgementAware)
        else:
            if not IContentAcknowledgementAware.providedBy(context):
                interface.alsoProvides(context, IContentAcknowledgementAware)
