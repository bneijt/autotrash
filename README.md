Autotrash is a small python script to automatically remove
(permanently delete) trashed files. It relies on the FreeDesktop.org
Trash files for it's deletion information.

It scans the `~/.local/share/Trash/info` directory and reads the `.trashinfo`
files to determine their deletion date. Files older then 30 days or files
matching a particular regular expression are then purged, including their
trash information file.

![Travis CI build status](https://api.travis-ci.org/bneijt/autotrash.svg)

Installation
============

On Fedora consider using `yum install autotrash`

[On Ubuntu](https://packages.ubuntu.com/search?suite=all&arch=any&searchon=names&keywords=autotrash) and [Debian](https://packages.debian.org/search?keywords=autotrash&searchon=names&suite=stable&section=all) try to install it using `apt-get install autotrash`.

ArchLinux has an [AUR package available](https://aur.archlinux.org/packages/autotrash/). 

Last option is to install autotrash using pip, for example, using: `pip install --user autotrash`


Configuration
=============

## Automatic Setup ##
run `autotrash --install` to create a systemd service which runs daily with the provided arguments. For example

    autotrash -d 30 --install

will run `/usr/bin/autotrash -d 30` daily.

The service can be manually started with `systemctl --user start autotrash`.
The timer can be enabled and disabled using `systemctl --user enable autotrash.timer` and
`systemctl --user disable autotrash.timer` respectively.

The service is installed to `~/.config/systemd/user` so like the cron approach, root access is not required and multiple users have their own independent services.


## Manual Cron Setup ##
To run autotrash daily using cron, add the following crontab entry:

    @daily /usr/bin/autotrash -d 30

You can also make `autotrash` process all user trash directories (not just in your home directory) by adding this crontab entry:

    @daily /usr/bin/autotrash -td 30

Or more frequently, but to keep disk IO down, only when there is less then 3GB of free space:

    @hourly /usr/bin/autotrash --max-free 3072 -d 30

To configure this, run "crontab -e" and add one of these lines in the
editor, then save and close the file.


## System Startup Setup ##
If you do not know how to work with crontab, you could add it to the startup
programs in GNOME using the menu: System -> Preferences -> Sessions

Add the program with the "+ Add" button.

This will make sure that your trash is cleaned up every time you log in.


Information
===========

Homepage: https://github.com/bneijt/autotrash

Autotrash is now in the stable repo for Fedora 20 and is going to be synced out on the mirrors also for Fedora 21.
Epel7 package is still in the testing repo but should go stable within few days.

You can install the package on Fedora right now with:

    yum install autotrash


Development
===========

The `autotrash` command is created as a script, using `poetry` you can run the current implementation using:

    poetry run autotrash

Or by using the shell:

    poetry shell
    autotrash --help

All pull requests and master builds are tested using github actions and require `black` formatting.
