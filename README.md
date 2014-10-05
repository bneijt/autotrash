Autotrash is a small python script to automatically remove
(permanently delete) trashed files. It relies on the FreeDesktop.org
Trash files for it's deletion information.

It scans the `~/.local/share/Trash/info` directory and reads the `.trashinfo`
files to determine their deletion date. Files older then 30 days or files
matching a particular regular expression are then purged, including their
trash information file.

Installation
------------

On Fedora consider using `yum install autotrash`

On Arch Linux use [the autotrash package in AUR](https://aur.archlinux.org/packages/autotrash/)

[On Ubuntu](http://packages.ubuntu.com/trusty/autotrash) and [Debian](https://packages.debian.org/search?keywords=autotrash&searchon=names&suite=stable&section=all) try to install it using `apt-get install autotrash`.

Last option is to copy the autotrash file from a release to any location on your PATH, for example `/usr/bin/`.


Configuration
-------------
It should be considered to be run as a crontab entry:

    @daily  /usr/bin/autotrash -d 30

Or more frequently, but to keep disk IO down, only when there is less then 3GB of free space:

    @hourly /usr/bin/autotrash --max-free 3072 -d 30

To configure this, run "crontab -e" and add one of these lines in the
editor, then save and close the file.

If you do not know how to work with crontab, you could add it to the startup
programs in GNOME using the menu: System -> Preferences -> Sessions

Add the program with the "+ Add" button.

This will make sure that your trash is cleaned up every time you log in.

Homepage: http://www.logfish.net/pr/autotrash/

Autotrash is now in the stable repo for Fedora 20 and is going to be synced out on the mirrors also for Fedora 21.
Epel7 package is still in the testing repo but should go stable within few days.

You can install the package on Fedora right now with:
yum install autotrash
