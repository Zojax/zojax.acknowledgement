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
import csv
import StringIO

from zope.app.security.interfaces import PrincipalLookupError
from zope.component import getUtility

from zojax.layoutform import Fields
from zojax.principal.field.utils import searchPrincipals
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.security.utils import getPrincipal
from zojax.statusmessage.interfaces import IStatusMessage
from zope.traversing.browser import absoluteURL

from ..interfaces import _, IAcknowledgements
from interfaces import IPrincipalExported


class BaseAcknowledged(object):

    result = None
    exportFields = Fields(IPrincipalExported).select(
        'title', 'firstname', 'lastname', 'email')
    filename = 'Acknowledged.csv'

    def __call__(self):
        request = self.request
        excel = self.prepare()

        if excel:
            request.response.setHeader('Content-Type', 'text/csv')
            request.response.setHeader(
                'Content-Disposition',
                'attachment; filename=%s' % self.filename)
            return excel

        IStatusMessage(request).add(_("No results"))
        request.response.redirect(absoluteURL(self.context, request))
        return

    def export(self, data):
        res = StringIO.StringIO()
        fields = self.exportFields.items()
        names = [value.field.title for key, value in fields] + [u'Location']
        writer = csv.writer(res, delimiter=';')
        writer.writerow(names)
        for value in data:
            location = value.getProfileData().get('location')
            writer.writerow(
                [unicode(getattr(value, fname, '') or '') for fname,
                    field in fields] + [location])

        res.seek(0)
        return res.read()


class Acknowledged(BaseAcknowledged):

    def prepare(self):
        results = getUtility(IAcknowledgements).search(object=self.context)

        if len(results) > 0:
            members = []
            for pid in [i.principal for i in results]:
                try:
                    principal = getPrincipal(pid)
                except PrincipalLookupError:
                    continue

                profile = IPersonalProfile(principal, None)
                if profile is None:
                    continue

                members.append(profile)

            return self.export(members)


class NotAcknowledged(BaseAcknowledged):

    filename = 'Not-Acknowledged.csv'

    def prepare(self):
        results = getUtility(IAcknowledgements).search(object=self.context)

        acknowledged = [i.principal for i in results]
        allusers = searchPrincipals(
            type=('user',),
            principalSubscribed = {'any_of': (True,)})

        members = []
        for pid in [i.id for i in allusers if i.id not in acknowledged]:
            try:
                principal = getPrincipal(pid)
            except PrincipalLookupError:
                continue

            profile = IPersonalProfile(principal, None)
            if profile is None:
                continue

            members.append(profile)

        return self.export(members)