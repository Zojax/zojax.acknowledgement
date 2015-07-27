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
"""
from zope import interface, component
from zope.location import Location

from zojax.personal.space.interfaces import IPersonalSpace

from interfaces import _, IPersonalAcknowledgementsWorkspace, \
    IPersonalAcknowledgementsWorkspaceFactory


class PersonalAcknowledgementsWorkspace(Location):
    interface.implements(IPersonalAcknowledgementsWorkspace)

    title = _('Acknowledgements')
    __name__ = u'personal-acknowledgements'


class PersonalAcknowledgementsWorkspaceFactory(object):
    component.adapts(IPersonalSpace)
    interface.implements(IPersonalAcknowledgementsWorkspaceFactory)

    name = u'Acknowledgements'
    title = _('Acknowledgements')
    description = _("Personal acknowledgements")
    weight = 9

    def __init__(self, space):
        self.space = space

    def get(self):
        view = PersonalAcknowledgementsWorkspace()
        view.__parent__ = self.space
        return view

    install = get

    def uninstall(self):
        pass

    def isInstalled(self):
        return False

    def isAvailable(self):
        return True
