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
from datetime import datetime
from persistent import Persistent

from zope import interface
from zope.component import getUtility
from zope.security.management import queryInteraction
from zope.app.intid.interfaces import IIntIds

from interfaces import IAcknowledgement


class Acknowledgement(Persistent):
    interface.implements(IAcknowledgement)

    id = None
    oid = 0
    date = None
    principal = u''

    def __init__(self, date=None, principal=None, **kw):
        if date is None:
            date = datetime.utcnow()

        self.date = date

        if principal is None:
            interaction = queryInteraction()

            if interaction is not None:
                for participation in interaction.participations:
                    principal = participation.principal.id

        self.principal = principal

        for attr, value in kw.items():
            setattr(self, attr, value)

    @property
    def object(self):
        return getUtility(IIntIds).queryObject(self.oid)
