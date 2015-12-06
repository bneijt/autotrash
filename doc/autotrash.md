% AUTOTRASH(1)
% A. Bram Neijt <bneijt@gmail.com>

# NAME

autotrash — program to automatically purge old files from the FreeDesktop.org trash

# SYNOPSIS

**autotrash** [**-d** purge_n_days_old]

**autotrash** [**--delete** number_of_megabytes_to_purge]

**autotrash** [**--keep-free** number_of_megabytes_to_free]

# DESCRIPTION

**autotrash** is  a program that looks in a FreeDesktop.org Trash folder for information on it's contents
and then purges a part of the trash depending on the options.

The most common option is **-d**, which will purge files that have been in the trash for more then a given
number of days.

The  option **--delete** will remove at least the given number of megabytes from the trash, removing the
oldest trash first.

Using **--keep-free** will make sure at least the given number of megabytes of free space is available, by
automatically setting **--delete** to the right value. For example, to keep at least a 1GB of free space,
removing files from the trash if needed, use **autotrash --keep-free 1024** .

# OPTIONS

This program follows the usual GNU command line syntax, with long options  starting  with  two  dashes
(`-').

-h --help
:   Show a summary of options.

-d _DAYS_ --days _DAYS_
:   Purge files older than DAYS number of days.

-T _PATH_ --trash-path _PATH_
:   Use  the  given  path  as  the  location  of  the  Trash  directory, instead of the default:
    ~/.local/share/Trash .

--max-free _M_
:   Only purge files if there is less than _M_ megabytes of free space left at the trash location.
    As  an  example, if you set this to 1024, then autotrash will only start to work if there is
    less than 1GB of free space in the trash. Till that time, autotrash will just exit  normally
    without  scanning  the  Trash directory. If unsure, try running autotrash with **--dry-run** and
    **--verbose** to see the effect.

--delete _M_
:   Purge at least _M_ megabytes, deleting oldest trash addition first. It uses trash entries, NOT
    individual  files.  This  means that if your oldest trashed item is a 1GB directory, and you
    request at least 10MB to be removed (_M_=10), autotrash will remove 1GB. If unsure,  try  run‐
    ning autotrash with both **--dry-run** and **--stat** to see the effect.

--min-free _M_ --keep-free _M_
:   Make  sure there is a minimum of _M_ megabytes of free space. If there is less free space, set
    --delete to the difference between _M_ and the amount of free space. If  unsure,  try  running
    autotrash with --dry-run and --verbose to see the effect.

-D _REGEX_ --delete-first _REGEX_
:   Purge  any  file  which  matches _REGEX_ first, regardless of it's time-stamp. REGEX must be a
    valid regular expression. If this option is used multiple  times,  the  files  matching  the
    first  regular  expression are deleted first, then the second etc.

    Example: delete any .avi files first, then by age: **--delete-first '.\*\\\.avi'**

-v --verbose
:   Output information on what is happening and why.

-q --quiet
:   Only output warnings.

--check
:   Report .trashinfo files that point to a non-existing file. This will only happen with a bro‐
    ken  Trashcan.  It  is  left  up to the user to actually do something with this information.
    These files will be removed as soon as the mentioned file would be removed by autotrash.

--dry-run
:   Only list what would be done, but actually do nothing.

--stat
:   Show the number, and total size of files involved.

-V --version
:   Show the version of program.

# EXAMPLES

Examples of program use.

autotrash -d 30
:   Purge any file that has been in the trash for more then 30 days.

autotrash --max-free 1024 -d 30
:   Only purge files from the trash if there is less  than  1GB  of  space  left  on  the  trash
    filesystem. If so, only trash files that are older than 30 days.

autotrash --min-free 2048
:   Purge  files  from  trash,  oldest  first,  till there is at least 2GB of space on the trash
    filesystem. There is no restriction on how old trashed files are.

autotrash --min-free 2048 -D '.\*\\\\.bak' -D '.\*\\\\.avi'
:   Purge files from trash till there is at least 2GB of space on the trash  filesystem.  If  we
    need  to remove files, make sure we remove *.bak files first, then all *.avi files and after
    that the oldest to the newest. There is no restriction on how old  trashed  files  can  get.
    Please  note  that  '.\*\\.bak'  and  '.\*\\.avi' are regular expressions and not glob patterns.
    Given that they are regular expressions, using -D '.\*\\.(png|gif|jpg|jpeg)' will match images
    with any of the given extensions.

autotrash --max-free 4000 --min-free 2048 -d 30
:   Start  reading  the  trash if there is less than 4000MB of free space, then start keeping an
    eye on it. At that point, remove files older than 30 days and if there is less than 2GB of free
    space after that remove even newer files.

@hourly /usr/bin/autotrash --max-free 4000 --min-free 2048 -d 30
:   Experienced  users should consider adding autotrash as a crontab entry, using **crontab -e** and
    adding the line above.

# COPYING

Copyright © 2015 Bram Neijt <bneijt@gmail.com>

This manual page was written for the **Debian** system (and may be used  by
others).  Permission is granted to copy, distribute and/or modify this document under the terms of the
GNU General Public License, Version 3 or any later version published by the Free Software Foundation.

On Debian systems, the complete text of the GNU General Public License can be found in
/usr/share/common-licenses/GPL.
