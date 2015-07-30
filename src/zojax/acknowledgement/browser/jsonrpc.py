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
import logging

from datetime import datetime

from z3c.jsonrpc import publisher

from zope.component import getUtility

from zojax.formatter.utils import getFormatter

from ..acknowledgement import Acknowledgement
from ..interfaces import IAcknowledgements


logger = logging.getLogger("zojax.acknowledgement")


class AcknowledgementAPI(publisher.MethodPublisher):

    def add(self, uid=None, oid=None):

        if not uid or not oid:
            return dict(error="ERROR: user and object can not be empty")

        date = datetime.utcnow()
        formatter = getFormatter(self.request, 'fancyDatetime', 'medium')

        try:
            getUtility(IAcknowledgements).add(
                Acknowledgement(principal=uid, oid=int(oid), date=date))
        except:
            return dict(error="ERROR: couldn't add record to catalog")

        return dict(user=self.request.principal.title,
                    date=formatter.format(date))
