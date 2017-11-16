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

from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from zojax.formatter.utils import getFormatter
from zojax.resourcepackage.library import includeInplaceSource

from ..interfaces import IContentAcknowledgementAware, IAcknowledgements


class AcknowledgementMessagePageElement(object):

    def update(self):

        if IContentAcknowledgementAware.providedBy(self.context):

            includeInplaceSource(
                jssource % {
                    'uid': self.request.principal.id,
                    'oid': getUtility(IIntIds).getId(self.context)
                },)

    def render(self):

        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):

            formatter = getFormatter(self.request, 'dateTime', 'medium')

            result = getUtility(IAcknowledgements).verifyRecord(
                object=self.context, uid=self.request.principal.id)

            if result:
                return msg_success % dict(
                    user=self.request.principal.title,
                    date=formatter.format(result.date))

            return msg_default

    def isAvailable(self):
        return IContentAcknowledgementAware.providedBy(self.context)


jssource = """
<script type="text/javascript">
$(document).ready(function() {
    $('#submit-acknowledge').click(function () {
        if ($(this).prev().find('input')[0].checked)
        {
            $.ajax({
                type: "POST",
                // TODO: need workaround for another hosts
                url: "http://" + location.host + "/++skin++JSONRPC.acknowledgement", // only for stage and prod
                data: "{'method':'add', 'params': {'uid':'%(uid)s','oid':'%(oid)s'}}",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(msg) {
                    // TODO: parse msg and replace #message-acknowledge text
                    if (msg.result.error)
                    {
                        $('#message-acknowledge')
                            .removeClass('statusWarningMessage yellowMessage')
                            .addClass('statusStopMessage')
                            .html(msg.result.error);
                    } else {
                        $('#message-acknowledge')
                            .removeClass('statusWarningMessage yellowMessage')
                            .addClass('statusMessage greenMessage')
                            .html(msg.result.user + ', on ' + msg.result.date + ' you acknowledged that you read and understood this document.');
                        setDatetimeFormatter($('#message-acknowledge .zojax-formatter-datetime'));
                    }
                },
                error: function (request, status, error) {
                    console.log(request.responseText);
                    alert("Something went wrong. Please reload the page and try again.");
                }
            });
        } else {
            alert('You should tick off the checkbox first.');
        }
    })
});
</script>
"""

msg_default = """
<div id="message-acknowledge" class="statusWarningMessage yellowMessage">
    <p><input type="checkbox" name="acknowledged" value="yes">
    I hereby acknowledge that I have read the document on this page and fully understand its contents. </p>
    <input id="submit-acknowledge" name="content.buttons.submit" class="z-form-button button-field" value="Submit" type="submit">
</div>
"""

msg_success = """
<div id="message-acknowledge" class="statusMessage greenMessage">
    %(user)s, on %(date)s you acknowledged that you read and understood this document.
</div>
"""
