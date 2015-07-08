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
"""Setup for zojax.acknowledgement package
"""

from setuptools import setup, find_packages

version = '1.0'

long_description = (
    open('README.md').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='zojax.acknowledgement',
      version=version,
      description="The package provides a way to have users to acknowledge they have read and understood a Page, Blog Post, Document, File, etc.",
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'
      ],
      keywords='Zope Acknowledgement',
      author='Dmitry Suvorov',
      author_email='suvdim@gmail.com',
      url='https://github.com/Zojax/zojax.acknowledgement',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['zojax'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'z3c.jsonrpc',
          'zojax.skintool'
      ],
      extras_require=dict(test=[
          'zojax.autoinclude',
          'zojax.batching',
          'zojax.content.forms',
          'zojax.controlpanel',
          'zojax.layout',
          'zojax.layoutform',
          'zojax.statusmessage',
          'zojax.wizard',
          'zope.app.component',
          'zope.app.testing',
          'zope.app.zcmlfiles',
          'zope.component',
          'zope.interface',
          'zope.schema',
          'zope.testing',
          'zope.testbrowser',
          'zope.viewlet',
          'zope.proxy']),
      entry_points="""
    # -*- Entry points: -*-
    """,)
