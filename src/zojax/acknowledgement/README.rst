=============
Browser tests
=============

    >>> from zope import interface, component, event
    >>> from zope.app.component.hooks import setSite
    >>> from zope.app.intid.interfaces import IIntIds
    >>> from zope.app.security.interfaces import IAuthentication
    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> from zope.testbrowser.testing import Browser

    >>> from zojax.principal.users.interfaces import IUsersPlugin

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


Let's create two users to check banned and terminated functionality

First we register plugin with IAuthenticatorPluginFactory

    >>> admin.open("http://localhost/settings/")
    >>> admin.getLink('Authentication').click()
    >>> admin.getControl(name='factory_ids:list').value = ['principal.users']
    >>> admin.getControl(name='form.install').click()


then add new principals

    >>> admin.open("http://localhost/settings/principals/")
    >>> admin.getLink('Member').click()
    >>> admin.getControl('First Name').value = u'Test'
    >>> admin.getControl('Last Name').value = u'Banned'
    >>> admin.getControl('E-mail/Login').value = u'test-banned@zojax.com'
    >>> admin.getControl('Password').value = u'12345'
    >>> admin.getControl(name="form.buttons.add").click()

    >>> admin.open("http://localhost/settings/principals/")
    >>> admin.getLink('Member').click()
    >>> admin.getControl('First Name').value = u'Test'
    >>> admin.getControl('Last Name').value = u'Terminated'
    >>> admin.getControl('E-mail/Login').value = u'test-terminated@zojax.com'
    >>> admin.getControl('Password').value = u'12345'
    >>> admin.getControl(name="form.buttons.add").click()

    >>> usersplugin = component.getUtility(IUsersPlugin)

    >>> principal = usersplugin['01']
    >>> principal.title, principal.login, principal.id
    (u'Test Banned', u'test-banned@zojax.com', u'zojax.pf01')

    >>> principal = usersplugin['03']
    >>> principal.title, principal.login, principal.id
    (u'Test Terminated', u'test-terminated@zojax.com', u'zojax.pf03')


and login as new principals

    >>> user3 = Browser()
    >>> user3.handleErrors = False
    >>> user3.open("http://localhost/")

    >>> user3.getLink('[Login]').click()
    >>> user3.getControl('Login Name').value = u'test-banned@zojax.com'
    >>> user3.getControl('Password').value = u'12345'
    >>> user3.getControl(name="form.zojax-auth-login").click()
    >>> print user3.contents
    <!DOCTYPE html...
    ...User:...
    ...Test Ban...
    </html>

    >>> user4 = Browser()
    >>> user4.handleErrors = False
    >>> user4.open("http://localhost/")

    >>> user4.getLink('[Login]').click()
    >>> user4.getControl('Login Name').value = u'test-terminated@zojax.com'
    >>> user4.getControl('Password').value = u'12345'
    >>> user4.getControl(name="form.zojax-auth-login").click()
    >>> print user4.contents
    <!DOCTYPE html...
    ...User:...
    ...Test Terminated...
    </html>


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

    >>> oid = component.getUtility(IIntIds).getId(content1)
    >>> user.post(
    ...     jsonURL,
    ...     "{'method':'add', 'params': {'uid': 'zojax.pf01', 'oid': '"+str(oid)+"'}}",
    ...     content_type='application/json')
    >>> user.contents
    '{"jsonrpc":"2.0","result":{"date":"...July 30, 2015 01:00...","user":"User"},"id":"jsonrpc"}'

    >>> oid = component.getUtility(IIntIds).getId(content1)
    >>> user.post(
    ...     jsonURL,
    ...     "{'method':'add', 'params': {'uid': 'zojax.pf03', 'oid': '"+str(oid)+"'}}",
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
    Test Banned;Test;Banned;test-banned@zojax.com;;;2015-07-30 08:00 UTC
    Test Terminated;Test;Terminated;test-terminated@zojax.com;;;2015-07-30 08:00 UTC

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
          <td>5</td>
        </tr>
        <tr class="odd">
          <th>Acknowledged Objects</th>
          <td>2</td>
        </tr>
        <tr class="even">
          <th>Users</th>
          <td>4</td>
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



Check banned and terminated users
---------------------------------


check that users are available in the report

    >>> admin.open('http://localhost/content1/acknowledged.html')
    >>> 'Test Ban' in admin.contents
    True

    >>> 'Test Terminated' in admin.contents
    True


let's ban one user

    >>> admin.open("http://localhost/settings/principals/ban/")
    >>> admin.getControl(name="form.widgets.principals:list").value = [u'zojax.pf01']
    >>> admin.getControl('Ban').click()
    >>> 'Members has been banned' in admin.contents
    True


and check that the user is not in the report

    >>> admin.open('http://localhost/content1/acknowledged.html')
    >>> 'Test Ban' in admin.contents
    False


let's terminate the other user

    >>> admin.open("http://localhost/settings/principals/zojax.pf03/membership/roles/")
    >>> admin.getControl(name="zope.Anonymous").value = ['2']
    >>> admin.getControl(name="form.save").click()
    >>> 'Roles have been changed' in admin.contents
    True


and check that the user is not in the report

    >>> admin.open('http://localhost/content1/acknowledged.html')
    >>> 'Test Terminated' in admin.contents
    False


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
          <td>4</td>
        </tr>
        <tr class="odd">
          <th>Acknowledged Objects</th>
          <td>1</td>
        </tr>
        <tr class="even">
          <th>Users</th>
          <td>4</td>
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
          <td>3</td>
        </tr>
        <tr class="odd">
          <th>Acknowledged Objects</th>
          <td>1</td>
        </tr>
        <tr class="even">
          <th>Users</th>
          <td>3</td>
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
