=============
Browser tests
=============

    >>> from zope import interface, component, event
    >>> from zope.app.component.hooks import setSite
    >>> from zope.app.intid.interfaces import IIntIds
    >>> from zope.app.security.interfaces import IAuthentication
    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> from zope.testbrowser.testing import Browser

    >>> from zojax.authentication.interfaces import IAuthenticationConfiglet, \
    ...     PrincipalRemovingEvent

    >>> from zojax.acknowledgement.interfaces import IAcknowledgements, \
    ...     IContentAcknowledgement, IContentWithAcknowledgement


Declare default variables
-------------------------

    >>> root = getRootFolder()
    >>> setSite(root)
    >>> sm = root.getSiteManager()

    >>> auth_configlet = component.getUtility(IAuthenticationConfiglet)
    >>> auth_configlet.installUtility()
    >>> auth_configlet.installPrincipalRegistry()
    >>> auth = sm.getUtility(IAuthentication)
    >>> auth.authenticatorPlugins = auth.authenticatorPlugins + ('authplugin',)

    >>> content1 = root['content1']
    >>> content2 = root['content2']

    >>> admin = Browser()
    >>> admin.addHeader("Authorization", "Basic mgr:mgrpw")
    >>> admin.handleErrors = False

    >>> user = Browser()
    >>> user.addHeader("Authorization", "Basic user:userpw")
    >>> user.handleErrors = False


Add `Acknowledgements` functionality
------------------------------------


Let's mark content as content with Acknowledgements

    >>> interface.alsoProvides(content1, IContentWithAcknowledgement)
    >>> interface.alsoProvides(content2, IContentWithAcknowledgement)
    >>> event.notify(ObjectModifiedEvent(root['content1']))
    >>> event.notify(ObjectModifiedEvent(root['content2']))

    >>> admin.open('http://localhost/content1/context.html')
    >>> 'Acknowledgement' in admin.contents
    True


Enable Acknowledgements for content1 and content2

    >>> IContentAcknowledgement(content1).acknowledge
    False

    >>> admin.getControl(name='form.widgets.acknowledge:list').value = ['true']
    >>> admin.getControl(name="content.edit.buttons.save").click()

    >>> IContentAcknowledgement(content1).acknowledge
    True

    >>> admin.open('http://localhost/content2/context.html')
    >>> admin.getControl(name='form.widgets.acknowledge:list').value = ['true']
    >>> admin.getControl(name="content.edit.buttons.save").click()

    >>> IContentAcknowledgement(content2).acknowledge
    True


Add a few Acknowledgements

    >>> jsonURL = 'http://localhost/++skin++JSONRPC.acknowledgement'

    >>> oid = component.getUtility(IIntIds).getId(content1)
    >>> admin.post(
    ...     jsonURL,
    ...     "{'method':'add', 'params': {'uid': 'zope.mgr', 'oid': '"+str(oid)+"'}}",
    ...     content_type='application/json')
    >>> admin.contents
    '{"jsonrpc":"2.0","result":{"date":"...July 30, 2015 01:00...","user":"Manager"},"id":"jsonrpc"}'

    >>> oid = component.getUtility(IIntIds).getId(content1)
    >>> user.post(
    ...     jsonURL,
    ...     "{'method':'add', 'params': {'uid': 'zope.user', 'oid': '"+str(oid)+"'}}",
    ...     content_type='application/json')
    >>> user.contents
    '{"jsonrpc":"2.0","result":{"date":"...July 30, 2015 01:00...","user":"User"},"id":"jsonrpc"}'

    >>> oid = component.getUtility(IIntIds).getId(content2)
    >>> admin.post(
    ...     jsonURL,
    ...     "{'method':'add', 'params': {'uid': 'zope.mgr', 'oid': '"+str(oid)+"'}}",
    ...     content_type='application/json')
    >>> admin.contents
    '{"jsonrpc":"2.0","result":{"date":"...July 30, 2015 01:00...","user":"Manager"},"id":"jsonrpc"}'


Check acknowledged reports

    >>> admin.open('http://localhost/content1/acknowledged.html')
    >>> print admin.contents
    Principal full name;Principal first name;Principal last name;Principal email;Location;Department;Date
    Manager;Manager;;;;;2015-07-30 08:00 UTC
    User;User;;;;;2015-07-30 08:00 UTC

    >>> admin.open('http://localhost/content1/not-acknowledged.html')
    >>> print admin.contents
    Principal full name;Principal first name;Principal last name;Principal email;Location;Department
    <BLANKLINE>


Check Acknowledgements tab in User's profile

    >>> admin.open('http://localhost/people/manager/personal-acknowledgements/')
    >>> print admin.contents
    <html>
    ...
      <h2>Your Acknowledged Items</h2>
      <div class="z-page-description">Below is a list of your acknowledged items.</div>
    ...
        <tr>
          <th>Type</th>
          <th>Title</th>
          <th>Date</th>
        </tr>
    ...
        <tr class="odd">
          <td><img src="http://localhost/@@/zojax-content-type-interfaces-IContent-zmi_icon.png" alt="Content" width="16" height="16" border="0" /></td>
          <td>
              <a href="http://localhost/content1/">Content1</a>
          </td>
          <td><span class="zojax-formatter-fancydatetime" ... format="medium">July 30, 2015 01:00:00 -0700</span></td>
        </tr> <tr class="even">
          <td><img src="http://localhost/@@/zojax-content-type-interfaces-IContent-zmi_icon.png" alt="Content" width="16" height="16" border="0" /></td>
          <td>
              <a href="http://localhost/content2/">Content2</a>
          </td>
          <td><span class="zojax-formatter-fancydatetime" ... format="medium">July 30, 2015 01:00:00 -0700</span></td>
        </tr>
    ...
    </html>


Configlet
---------

Statistic tab

    >>> admin.open("http://localhost/settings/")
    >>> admin.getLink('Acknowledgements').click()

    >>> print admin.contents
    <html>
    ...
      <h1 class="z-content-title">Acknowledgements</h1>
      <div class="z-content-description">Portal acknowledgements.</div>
    ...
        <tr class="even">
          <th>Total Acknowledgements</th>
          <td>3</td>
        </tr>
        <tr class="odd">
          <th>Acknowledged Objects</th>
          <td>2</td>
        </tr>
        <tr class="even">
          <th>Users</th>
          <td>2</td>
        </tr>
    ...
    </html>


Catalog tab

    >>> admin.open('http://localhost/settings/system/acknowledgement/index.html/catalog/')
    >>> print admin.contents
    <html>
    ...
      <h1 class="z-content-title">Acknowledgements</h1>
      <div class="z-content-description">Portal acknowledgements.</div>
    ...
            <thead>
              <th>Type</th>
              <th>Object</th>
              <th>User</th>
              <th>Data</th>
            </thead>
    ...
              <tr class="odd">
                <td><img src="http://localhost/@@/zojax-content-type-interfaces-IContent-zmi_icon.png" alt="Content" width="16" height="16" border="0" /></td>
                  <td>
                    <a href="http://localhost/content1/">Content1</a>
                  </td>
                  <td>
                    <a>Manager</a>
                  </td>
                  <td><span class="zojax-formatter-fancydatetime" date="..." format="medium">July 30, 2015 01:00:00 -0700</span></td>
              </tr> <tr class="even">
                <td><img src="http://localhost/@@/zojax-content-type-interfaces-IContent-zmi_icon.png" alt="Content" width="16" height="16" border="0" /></td>
                  <td>
                    <a href="http://localhost/content1/">Content1</a>
                  </td>
                  <td>
                    <a>User</a>
                  </td>
                  <td><span class="zojax-formatter-fancydatetime" date="..." format="medium">July 30, 2015 01:00:00 -0700</span></td>
              </tr> <tr class="odd">
                <td><img src="http://localhost/@@/zojax-content-type-interfaces-IContent-zmi_icon.png" alt="Content" width="16" height="16" border="0" /></td>
                  <td>
                    <a href="http://localhost/content2/">Content2</a>
                  </td>
                  <td>
                    <a>Manager</a>
                  </td>
                  <td><span class="zojax-formatter-fancydatetime" date="..." format="medium">July 30, 2015 01:00:00 -0700</span></td>
              </tr>
    ...
    </html>


Check object deletion
---------------------


Acknowledgements for the deleted object should also be deleted

    >>> admin.open('http://localhost/content2/delete.html')
    >>> 'Are you sure you want remove this content item?' in admin.contents
    True

    >>> admin.getControl('Delete').click()
    >>> 'Content2' in admin.contents
    False

    >>> admin.open('http://localhost/settings/system/acknowledgement/')
    >>> print admin.contents
    <html>
    ...
        <tr class="even">
          <th>Total Acknowledgements</th>
          <td>2</td>
        </tr>
        <tr class="odd">
          <th>Acknowledged Objects</th>
          <td>1</td>
        </tr>
        <tr class="even">
          <th>Users</th>
          <td>2</td>
        </tr>
    ...
    </html>

    >>> admin.open('http://localhost/settings/system/acknowledgement/index.html/catalog/')
    >>> 'Content2' in admin.contents
    False


Acknowledgements for the deleted user should also be deleted

    >>> event.notify(PrincipalRemovingEvent(auth.getPrincipal('zope.user')))
    >>> admin.open('http://localhost/settings/system/acknowledgement/')
    >>> print admin.contents
    <html>
    ...
        <tr class="even">
          <th>Total Acknowledgements</th>
          <td>1</td>
        </tr>
        <tr class="odd">
          <th>Acknowledged Objects</th>
          <td>1</td>
        </tr>
        <tr class="even">
          <th>Users</th>
          <td>1</td>
        </tr>
    ...
    </html>

    >>> admin.open('http://localhost/settings/system/acknowledgement/index.html/catalog/')
    >>> print admin.contents
    <html>
    ...
          <table class="z-table">
            <thead>
              <th>Type</th>
              <th>Object</th>
              <th>User</th>
              <th>Data</th>
            </thead>
            <tbody>
              <tr class="odd">
                <td><img src="http://localhost/@@/zojax-content-type-interfaces-IContent-zmi_icon.png" alt="Content" width="16" height="16" border="0" /></td>
                  <td>
                    <a href="http://localhost/content1/">Content1</a>
                  </td>
                  <td>
                    <a>Manager</a>
                  </td>
                  <td><span class="zojax-formatter-fancydatetime" date="..." format="medium">July 30, 2015 01:00:00 -0700</span></td>
              </tr>
            </tbody>
          </table>
    ...
    </html>


Cleanup
-------

    >>> setSite(None)
