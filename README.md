zojax.acknowledgement
=====================

The package provides a way to have users to acknowledge they have read and understood a Page, Blog Post, Document, File, etc.

add `Acknowledgements` functionality to the content type:

    <class class="zojax.contenttype.document.document.Document">
      <implements interface="zojax.acknowledgement.interfaces.IContentWithAcknowledgement" />
    </class>

add pageelement into the theme

    <tal:block tal:content="structure pageelement:content.acknowledgement" />


Build Status
------------
[![Build Status](http://jenkins.zojax.com/buildStatus/icon?job=zojax.acknowledgement)](http://jenkins.zojax.com/job/zojax.acknowledgement/)


Links
-----

- Main github project repository: https://github.com/Zojax/zojax.acknowledgement
- Issue tracker: https://github.com/Zojax/zojax.acknowledgement/issues


Contributors
------------

- Dmitry Suvorov [suvdim], Author


Copyright
---------

This package is copyright by `Zojax <http://www.zojax.com/>`.

``zojax.acknowledgement`` is licensed under GNU General Public License, version 2.