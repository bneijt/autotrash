#!/usr/bin/python
from distutils.core import setup

setup(
  name=         'autotrash',
  version=      '0.0.6',
  author=       'A. Bram Neijt',
  author_email= 'bram@neijt.nl',
  url=          'http://logfish.net/pr/autotrash/',
  description=  'Automatic GNOME Trash purging',
  license=      'GNU GPL v3',
  download_url= 'http://logfish.net/pr/autotrash/downloads/',
  long_description= 'AutoTrash is a simple Python script which will remove files which you deleted more then 30 days ago (or any other number of days you would like). It uses the FreeDesktop.org Trash Info files included in the new GNOME system to find the correct files and the dates they where deleted. ',
  scripts= ['autotrash'],
  )

