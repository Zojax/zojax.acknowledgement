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
import csv
import StringIO

from zope.app.security.interfaces import PrincipalLookupError
from zope.component import getUtility
from zope.traversing.browser import absoluteURL

from zojax.authentication.utils import getPrincipal
from zojax.batching.batch import Batch
from zojax.principal.ban.interfaces import IBanPrincipalConfiglet
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.statusmessage.interfaces import IStatusMessage
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
    result = None

    def update(self):
        super(AcknowledgementsCatalogView, self).update()

        request, context = self.request, self.context

        records = getUtility(IAcknowledgements).records.items()

        if 'form.button.export_csv' in request:
            banned = getUtility(IBanPrincipalConfiglet).banned
            try:
                self.result = self.generate_report(banned, records)
                IStatusMessage(request).add(
                    _(u'The report was successfully generated.'))
            except:
                IStatusMessage(request).add(
                    _(u'The report was not generated.'), 'error')

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

    def generate_report(self, bannedusers, records):
        principals = {}
        res = StringIO.StringIO()
        writer = csv.writer(res, delimiter=';')
        writer.writerow([u'User', u'Acknowledgement Title', u'Date'])

        for uid, record in records:
            if record.principal in bannedusers:
                continue
            if not hasattr(record.object, 'title'):
                continue

            if record.principal in principals:
                principal = principals[record.principal]
            else:
                try:
                    principal = getPrincipal(record.principal)
                    principals[record.principal] = principal
                except PrincipalLookupError:
                    continue

            if hasattr(principal, 'title'):
                writer.writerow([
                    unicode(principal.title),
                    unicode(record.object.title),
                    record.date.strftime('%Y-%m-%d %H:%M UTC')])

        res.seek(0)
        return res.read()

    def __call__(self):
        if self.result:
            self.request.response.setHeader('Content-Type', 'text/csv')
            self.request.response.setHeader(
                'Content-Disposition',
                'attachment; filename=all-acknowledgements.csv')
            return self.result

        return super(AcknowledgementsCatalogView, self).__call__()
