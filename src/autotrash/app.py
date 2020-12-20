#!/usr/bin/env python3
#   autotrash - GNOME GVFS Trash old file auto prune
#
#   Copyright (C) 2019 A. Bram Neijt <bneijt@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
import configparser
import errno
import logging
import optparse
import os
import re
import shutil
import stat
import sys
import datetime
import subprocess
from typing import Union

import math
from autotrash import __version__
from autotrash.options import new_parser, check_options

# custom logging level between DEBUG and INFO
VERBOSE = 15


class StatsClass:
    total_size = 0
    total_files = 0
    deleted_size = 0
    deleted_files = 0
    failures = 0


def on_remove_error(function, path, excinfo):
    if excinfo[0] == errno.EPERM:
        # Permission errors, try a chmod to recover
        if function == os.remove:
            # Tried to remove a file, but failed. Try to change the write permissions of the tree to delete it
            logging.log(
                VERBOSE,
                "Failed to remove file at: %s\n\tgot exception: %s\n\tchanging permissions and trying again.",
                path,
                str(excinfo),
            )
            os.chmod(path, stat.S_IWUSR)
            os.unlink(path)
            return
        if function == os.rmdir:
            # Tried to remove a directory, but failed. Try to change the write permissions of the tree to delete it
            logging.log(
                VERBOSE,
                "Failed to remove directory at: %s\n\tgot exception: %s\n\tchanging permissions and trying again.",
                path,
                str(excinfo),
            )
            os.chmod(path, stat.S_IWUSR)
            os.unlink(path)
            return
    # Other error, what will it be?
    logging.error('Failed to remove "%s", got exception: %s', path, str(excinfo))


def real_file_name(trash_name: str) -> str:
    """Get real file name from trashinfo file name: basename without extension in ../files"""
    basename = os.path.basename(trash_name)
    trash_directory = os.path.abspath(os.path.join(os.path.dirname(trash_name), ".."))
    (file_name, trashinfo_ext) = os.path.splitext(basename)
    return os.path.join(trash_directory, "files", file_name)


def purge(trash_directory, trash_name, dryrun):
    """Purge the file behind the trash file fname"""
    assert os.path.exists(trash_name)
    target = real_file_name(trash_name)
    if dryrun:
        # Broken links will not os.path.exist
        if os.path.exists(target) or os.path.islink(target):
            logging.info("Remove %s", target)
        else:
            logging.info("Ignore %s", target)
        if os.path.exists(trash_name):
            logging.info("Remove %s", trash_name)
        else:
            logging.info("Ignore %s", trash_name)
        return False

    # The real deleting...
    if os.path.islink(target):
        logging.log(VERBOSE, "Removing link %s", target)
        os.unlink(target)
    elif os.path.isdir(target):
        logging.log(VERBOSE, "Removing directory %s", target)
        shutil.rmtree(target, False, on_remove_error)
    else:
        # Make sure we do not try to unlink a file that does not exist.
        if os.path.exists(target):
            logging.log(VERBOSE, "Removing file %s", target)
            os.unlink(target)
        else:
            logging.log(VERBOSE, "Ignore non-existing file %s", target)

    os.unlink(trash_name)
    return True


def read_datetime(value: str) -> datetime.datetime:
    for format in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"]:
        try:
            return datetime.datetime.strptime(value, format)
        except ValueError as ve:
            failure = ve
    raise failure


def get_trash_info_date(fname: str) -> Union[datetime.datetime, None]:
    try:
        parser = configparser.ConfigParser()
        read_correctly = parser.read(fname)
        section = "Trash Info"
        key = "DeletionDate"
        if read_correctly.count(fname) and parser.has_option(section, key):
            # Read the file successfully, parse the DeletionDate
            return read_datetime(parser.get(section, key))
    except Exception as e:
        # Error because exit status will be >0 because of this
        logging.error("Failed to read %s: %s", fname, e)
    return None


def get_consumed_size(path: str) -> int:
    """Get the amount of filesystem space actually consumed by a file or directory"""
    size = 0
    try:
        if os.path.islink(path):
            size = os.lstat(path).st_size
        else:
            size = os.stat(path).st_blocks * 512
            if os.path.isdir(path):
                for entry_name in os.listdir(path):
                    size += get_consumed_size(os.path.join(path, entry_name))
    except OSError:
        logging.error("Error getting size for %s", path)
    return size


def fmt_bytes(num_bytes: int, fmt: str = "%.1f") -> str:
    # If you NEED EiB, ZiB or YiB, please send me a mail I would love to hear from you!
    for size, name in (
        (1 << 50, "PiB"),
        (1 << 40, "TiB"),
        (1 << 30, "GiB"),
        (1 << 20, "MiB"),
        (1 << 10, "KiB"),
    ):
        if num_bytes >= size:
            return "%s %s" % (fmt % (float(num_bytes) / size), name)
    return "%d bytes" % num_bytes


def find_trash_directories(override_dir=None, find_mounts=False):
    if override_dir:
        return [override_dir]

    trash_paths = []

    # Add user trash directory
    trash_path = os.path.join(
        os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "Trash"
    )
    trash_paths.append(trash_path)
    logging.log(VERBOSE, "Found trash directory: %s" % (trash_path))

    # Add trash "top directories" in all mount points (if they exist)
    if find_mounts:
        with open("/proc/mounts", "r") as mounts:
            for line in mounts.readlines():
                mount_path = line.split()[1]

                # Find a usable trash path on this device
                trash_path_options = [
                    os.path.join(mount_path, ".Trash", str(os.getuid())),
                    os.path.join(mount_path, ".Trash-%d" % (os.getuid())),
                ]
                for trash_path in trash_path_options:
                    if os.path.exists(trash_path):
                        logging.log(VERBOSE, "Found trash directory: %s" % (trash_path))
                        trash_paths.append(trash_path)
                        break

    return trash_paths


def configure_logging(options) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.addLevelName(VERBOSE, "VERBOSE")
    if options.verbose:
        logging.getLogger().setLevel(VERBOSE)
    elif options.quiet:
        logging.getLogger().setLevel(logging.WARNING)


def get_fs_stat(trash_info_path):
    return os.statvfs(trash_info_path)


def get_file_names(trash_info_path):
    return [
        os.path.join(trash_info_path, fn)
        for fn in os.listdir(trash_info_path)
        if fn.endswith(".trashinfo")
    ]


def get_cur_time():
    return datetime.datetime.now().timestamp()


class OsAccess:
    get_file_names = None
    get_cur_time = None
    get_fs_stat = None
    get_consumed_size = None
    get_trash_info_date = None
    purge = None


def process_path(trash_info_path, options, stats, os_access) -> int:
    if options.max_free or options.min_free:  # Free space calculation is needed
        fs_stat = os_access.get_fs_stat(trash_info_path)
        if fs_stat.f_bsize <= 0:
            logging.error(
                "Can not determine free space because the returned filesystem block size was %i\n"
                "The --max-free option may not be supported for this filesystem."
                % fs_stat.f_bsize
            )
            return 1
        free_megabytes = int((fs_stat.f_bavail * fs_stat.f_bsize) / (1024 * 1024))

        if options.max_free:
            # Check if there is less then max_free megabytes of free space
            # if there is not less, then do nothing and skip the glob.
            if free_megabytes > options.max_free:
                logging.log(
                    VERBOSE,
                    'I see %i MB of free space at "%s"\n'
                    "\t Which is more then --max-free, doing nothing.",
                    free_megabytes,
                    trash_info_path,
                )
                return 0
        if options.min_free and free_megabytes < options.min_free:
            options.delete = options.min_free - free_megabytes
            logging.log(
                VERBOSE,
                "Setting --delete to %i to make sure at least %i MB becomes free.\n"
                "\t Currently we have %i megabytes of free space.",
                options.delete,
                options.min_free,
                free_megabytes,
            )

    deleted_target = 0
    if options.delete:
        deleted_target = options.delete * 1024 * 1024

    trash_total_size = 0

    # Collect file info's
    files = []
    if True:  # Scope protection
        trash_info_file_names = os_access.get_file_names(trash_info_path)
        for file_name in trash_info_file_names:
            real_file = real_file_name(file_name)
            file_info = {"trash_info": file_name, "real_file": real_file}
            if options.check and not os.path.exists(real_file):
                logging.warning("%s has no real file associated with it", file_name)

            file_time = os_access.get_trash_info_date(file_name)
            if not file_time:
                # This happens when a trashinfo file is corrupted (issue #9)
                logging.warning(
                    "Failed to read trash info for real file: %s",
                    file_info["real_file"],
                )
                stats.failures += 1
                return 0
            file_info["time"] = file_time.timestamp()
            file_info["age_seconds"] = os_access.get_cur_time() - file_info["time"]
            file_info["age_days"] = int(
                math.floor(file_info["age_seconds"] / (3600.0 * 24.0))
            )

            if options.stat or options.delete or options.trash_limit:
                # calculating file size is relatively expensive; only do it if needed
                file_size = os_access.get_consumed_size(file_name)
                if os.path.exists(real_file):
                    if os.path.isdir(real_file):
                        logging.log(
                            VERBOSE,
                            "Calculating size of directory %s (may take a long time)",
                            real_file,
                        )
                    file_size += os_access.get_consumed_size(real_file)
                file_info["size"] = file_size
                trash_total_size += file_size

            logging.log(VERBOSE, "File %s", real_file)
            logging.log(
                VERBOSE,
                "    is %d days old, %d seconds, so it should %sbe removed",
                file_info["age_days"],
                file_info["age_seconds"],
                ["not ", ""][int(file_info["age_days"] > options.days)],
            )
            logging.log(VERBOSE, "    deletion date was %s", file_time.isoformat())
            if options.stat:
                logging.log(VERBOSE, "    consumes %s", fmt_bytes(file_info["size"]))

            files.append(file_info)

    if options.trash_limit:
        trash_limit_bytes = options.trash_limit * 1024 * 1024
        if deleted_target:
            logging.error("Cannot mix '--trash_limit' with '--delete'")
            return 1

        logging.log(VERBOSE, "Total trash size is %s", fmt_bytes(trash_total_size))
        logging.log(VERBOSE, "Trash size limit is %s", fmt_bytes(trash_limit_bytes))

        if trash_limit_bytes < trash_total_size:
            deleted_target = trash_total_size - trash_limit_bytes
            logging.log(VERBOSE, "Trash exceeds limit by %s", fmt_bytes(deleted_target))

    # Kill sorting: first will get purged first if --delete is enabled
    files.sort(key=lambda x: x["age_seconds"], reverse=True)

    # Push priority files (delete_first) to the top of the queue
    for pattern in reversed(options.delete_first):
        r = re.compile(pattern)
        moved_count = 0
        for i in range(len(files)):
            if r.match(os.path.basename(files[i]["real_file"])) is not None:
                file_info = files.pop(i)
                logging.log(
                    VERBOSE,
                    "Pushing %s to top of queue because it matches %s",
                    os.path.basename(file_info["real_file"]),
                    pattern,
                )
                files.insert(moved_count, file_info)
                moved_count += 1

    for file_info in files:
        if options.stat:
            stats.total_size += file_info["size"]
            stats.total_files += 1

        if (
            options.days and file_info["age_days"] > options.days
        ) or stats.deleted_size < deleted_target:
            os_access.purge(options.trash_path, file_info["trash_info"], options.dryrun)
            if deleted_target or options.stat:
                stats.deleted_size += file_info["size"]
                stats.deleted_files += 1
        elif options.verbose:
            logging.log(VERBOSE, "Keeping %s", real_file_name(file_info["trash_info"]))

    return 0


def install_service(options, args):
    if shutil.which("systemctl") is None:
        logging.error("system must support systemd to use --install")
        return

    if options.dryrun:
        logging.error("cannot install with --dry-run enabled")
        return

    executable_path = shutil.which("autotrash")
    if executable_path is None:
        logging.error("autotrash not found in the path")

    args = subprocess.list2cmdline([arg for arg in sys.argv[1:] if arg != "--install"])

    timer_file = """\
[Unit]
Description=Empty trash

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
"""

    service_file = """\
[Unit]
Description=Empty trash

[Service]
Type=oneshot
ExecStart="{}" {}
""".format(
        executable_path, args
    )

    systemd_dir = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(systemd_dir, exist_ok=True)

    with open(os.path.join(systemd_dir, "autotrash.timer"), "w") as f:
        f.write(timer_file)

    with open(os.path.join(systemd_dir, "autotrash.service"), "w") as f:
        f.write(service_file)

    logging.info('service installed to "{}"'.format(systemd_dir))
    subprocess.check_output(["systemctl", "--user", "enable", "autotrash.timer"])
    logging.info("checking that the service is working...")
    subprocess.check_output(["systemctl", "--user", "start", "autotrash"])
    logging.info("service is working")


def cli():
    # Load and set configuration options
    parser = new_parser()
    (options, args) = parser.parse_args()

    configure_logging(options)

    if options.version:
        logging.info(
            "Version %s\n"
            "Copyright (C) 2019 Bram Neijt <bram@neijt.nl>\n"
            "License GPLv3+",
            __version__,
        )
        return 1

    check_options(parser, options)

    if options.install:
        install_service(options, args)
        return 1

    # Compile list of possible trash directories
    trash_paths = find_trash_directories(options.trash_path, options.trash_mounts)

    # Set variables for stats collecting
    stats = StatsClass()

    os_access = OsAccess()
    os_access.get_file_names = get_file_names
    os_access.get_cur_time = get_cur_time
    os_access.get_fs_stat = get_fs_stat
    os_access.get_consumed_size = get_consumed_size
    os_access.get_trash_info_date = get_trash_info_date
    os_access.purge = purge

    for trash_path in trash_paths:
        trash_info_path = os.path.expanduser(os.path.join(trash_path, "info"))
        if not os.path.exists(trash_info_path):
            logging.error(
                "Can not find trash information directory: %s", trash_info_path
            )
            return 1

        if process_path(trash_info_path, options, stats, os_access):
            return 1

    if options.stat:
        logging.info("Trash statistics:")
        logging.info(
            "  %6d entries at start (%s)",
            stats.total_files,
            fmt_bytes(stats.total_size),
        )
        logging.info(
            " -%6d deleted (%s)", stats.deleted_files, fmt_bytes(stats.deleted_size)
        )
        logging.info(
            " =%6d remaining (%s)",
            (stats.total_files - stats.deleted_files),
            fmt_bytes(stats.total_size - stats.deleted_size),
        )
    return 0 if stats.failures == 0 else 1


def main():
    sys.exit(cli())


if __name__ == "__main__":
    main()
