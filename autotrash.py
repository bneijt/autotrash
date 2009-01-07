#!/usr/bin/env python
#    autotrash.py - GNOME GVFS Trash old file auto prune
#    
#    Copyright (C) 2008 A. Bram Neijt <bneijt@gmail.com>
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import optparse
import ConfigParser
import shutil
import glob
import os.path
import time
import math

def purge(trash_name, dryrun):
  '''Purge the file behind the trash file fname'''
  file_name = os.path.basename(trash_name)[:-10]
  target = os.path.expanduser('~/.local/share/Trash/files/')+file_name
  if dryrun:
    print 'Remove',target
    print 'Remove',trash_name
    return False
  if os.path.exists(target):
    if os.path.isdir(target):
        shutil.rmtree(target)
    else:
      os.unlink(target)
  os.unlink(trash_name)
  return True

def trash_info_date(fname):
  parser = ConfigParser.SafeConfigParser()
  readCorrectly = parser.read(fname)
  section = 'Trash Info'
  key = 'DeletionDate'
  if readCorrectly.count(fname) and parser.has_option(section, key):
    #Read the file succesfully
    return time.strptime(parser.get(section, key), '%Y-%m-%dT%H:%M:%S')
  return None

def main(args):
  #Load and set configuration options
  parser = optparse.OptionParser()
  parser.set_defaults(days=30, dryrun=False, verbose=False)
  parser.add_option("-d", "--days", dest='days', help='Delete files older then this DAYS number of days', metavar="DAYS")
  parser.add_option("--verbose", action='store_true', dest='verbose', help='Verbose')
  parser.add_option("--dry-run", action='store_true', dest='dryrun', help='Just list what would have been done')
  parser.add_option("--version", action='store_true', dest='version', help='Show version and exit')
  (options, args) = parser.parse_args()
  
  if options.version:
    print '''Version 0.0.1 \nCopyright (C) 2008 A. Bram Neijt <bneijt@gmail.com>\n License GPLv3+'''
  
  options.days = int(options.days)
  if options.days <= 0:
    print 'Can not work with negative or zero days'
    return 0
  
  for file_name in glob.iglob(os.path.expanduser('~/.local/share/Trash/info/*.trashinfo')):
    #print 'Loading file',file_name
    file_time = trash_info_date(file_name)
    if file_time == None:
      continue
    #Calculate seconds from now
    seconds_old = time.time() - time.mktime(file_time)
    days_old = int(math.floor(seconds_old/(3600.0*24.0)))
    if options.verbose:
      print 'File',file_name
      print '  is',days_old,'days old (',seconds_old,' seconds)'
      print '  deletion date was', time.strftime('%c', file_time)
    if days_old > options.days:
      purge(file_name, options.dryrun)
      if options.dryrun:
        print '  because it describes a',days_old,'days old file'
  return 0

if __name__ == '__main__':
  sys.exit(main(sys.argv))
