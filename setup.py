#!/usr/bin/python
from distutils.core import setup

setup(
  name=         'autotrash',
  version=      '0.1.5',
  author=       'A. Bram Neijt',
  author_email= 'bram@neijt.nl',
  url=          'http://logfish.net/pr/autotrash/',
  description=  'Automatic GNOME Trash purging',
  license=      'GNU GPL v3',
  download_url= 'http://logfish.net/pr/autotrash/downloads/',
  long_description= 'AutoTrash is a simple Python script which will remove files which you deleted more then X days ago. It uses the FreeDesktop.org Trash Info files to find the correct files and when they where trashed.',
  scripts= ['autotrash'],
  )

