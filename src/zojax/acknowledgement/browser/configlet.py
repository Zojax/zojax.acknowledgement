##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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

from zope.component import getUtility
from zope.traversing.browser import absoluteURL

from zojax.authentication.utils import getPrincipal
from zojax.batching.batch import Batch
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.wizard import WizardStepForm

from ..interfaces import _, IAcknowledgements


class AcknowledgementsStatsView(WizardStepForm):

    name = 'stats'
    title = _(u'Statistics')
    label = _(u' ')

    def update(self):
        super(AcknowledgementsStatsView, self).update()

        configlet = getUtility(IAcknowledgements)

        self.records = len(configlet.records.items())
        self.objects = configlet.catalog[u'object'].wordCount.value
        self.users = configlet.catalog[u'principal'].wordCount.value


class AcknowledgementsCatalogView(WizardStepForm):

    name = 'catalog'
    title = _(u'Catalog')
    label = _(u' ')

    def update(self):
        super(AcknowledgementsCatalogView, self).update()

        request, context = self.request, self.context

        records = getUtility(IAcknowledgements).records.items()

        self.batch = Batch(records, size=20, context=context, request=request)

    def getUser(self, uid):
        principal = getPrincipal(uid)
        try:
            profile = IPersonalProfile(principal)
            return dict(
                title=profile.title,
                url=profile.space is not None and u'%s/' % absoluteURL(
                    profile.space, self.request))
        except TypeError:
            return dict(title='Deleted Member', url='#')
