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
from zope import interface
from zope.schema import TextLine

from z3c.jsonrpc.layer import IJSONRPCLayer

from zojax.content.actions.interfaces import IAction
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.skintool.interfaces import INoSkinSwitching

from ..interfaces import _


class IAcknowledgementMessage(interface.Interface):
    """ acknowledgement message """


class IJSONRPCLayer(IJSONRPCLayer, INoSkinSwitching):
    """ jsonrpc layer """


class IContentAcknowledgementsCategory(interface.Interface):
    """ acknowledgements actions category """


class IAcknowledgementsAction(IAction, IContentAcknowledgementsCategory):
    """ acknowledgements action """


class INoAcknowledgementsAction(IAction, IContentAcknowledgementsCategory):
    """ no acknowledgements action """


class IPrincipalExported(IPersonalProfile):
    """ member exported """

    title = TextLine(title=_(u'Principal full name'))
    firstname = TextLine(title=_(u'Principal first name'))
    lastname = TextLine(title=_(u'Principal last name'))
    email = TextLine(title=_(u'Principal email'))
    location = TextLine(title=_(u'Location'))
