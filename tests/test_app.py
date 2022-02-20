import datetime
import os
import random
import tempfile
from typing import Dict

import autotrash

# ------------- mock functions & helpers --------------

mock_free_space_mb = 1000
file_info_map = {}  # type: Dict[str, dict]


class OptionsClass:
    days = 1
    trash_path = None
    max_free = 0
    delete = 0
    min_free = 0
    verbose = True
    quiet = False
    check = False
    dryrun = True
    stat = False
    delete_first = []  # type: list
    version = False
    trash_limit = 0


def mock_get_file_names(trash_info_path):
    keys = list(file_info_map.keys())
    # shuffling the list of files to make sure the order doesn't matter
    random.seed(4)
    random.shuffle(keys)
    return keys


def mock_get_cur_time():
    return datetime.datetime(2000, 12, 25).timestamp()


def mock_get_consumed_size(file_name):
    return file_info_map[file_name]["size"]


def mock_get_trash_info_date(value: str) -> datetime.datetime:
    return datetime.datetime(2000, 12, 25) - datetime.timedelta(
        days=file_info_map[value]["days_old"]
    )


def mock_purge(trash_directory, trash_name, dryrun):
    file_info_map[trash_name]["deleted"] = True
    return


class FsStat:
    f_bsize = 1024
    f_bavail = 1024 * mock_free_space_mb


def mock_get_fs_stat(trash_info_path):
    fs_stat = FsStat()
    return fs_stat


def add_mock_file(name, days_old, size_mb):
    file_info_map[name] = {
        "days_old": days_old,
        "size": size_mb * 1024 * 1024,
        "deleted": False,
    }


def run_end_to_end(options, expected_deleted):

    file_info_map.clear()

    stats = autotrash.StatsClass()
    os_access = autotrash.OsAccess()
    os_access.get_file_names = mock_get_file_names
    os_access.get_cur_time = mock_get_cur_time
    os_access.get_consumed_size = mock_get_consumed_size
    os_access.get_fs_stat = mock_get_fs_stat
    os_access.get_trash_info_date = mock_get_trash_info_date
    os_access.purge = mock_purge

    add_mock_file("a", 0, 1)
    add_mock_file("b", 1, 1)
    add_mock_file("c", 1.1, 2)
    add_mock_file("d", 2, 2)
    add_mock_file("e", 2.1, 3)
    add_mock_file("f", 3, 2)
    add_mock_file("g", 3.1, 3)

    autotrash.process_path("", options, stats, os_access)

    for f in file_info_map:
        if file_info_map[f]["deleted"] == True:
            assert f in expected_deleted
        else:
            assert f not in expected_deleted

    # just to be extra sure
    for f in expected_deleted:
        assert file_info_map[f]["deleted"] == True


# -------- "end-to-end" tests ----------

# nothing deleted
def test_nothing_deleted():
    options = OptionsClass()
    options.days = 5
    expected_deleted = []
    run_end_to_end(options, expected_deleted)


# old files deleted
def test_old_files_deleted():
    options = OptionsClass()
    options.days = 1
    expected_deleted = ["d", "e", "f", "g"]
    run_end_to_end(options, expected_deleted)


# files deleted due to --delete
def test_deleted_with_delete():
    options = OptionsClass()
    options.days = 5
    options.delete = 6
    expected_deleted = ["e", "f", "g"]
    run_end_to_end(options, expected_deleted)


# same test with --min-free
def test_deleted_with_min_free():
    options = OptionsClass()
    options.days = 5
    options.min_free = mock_free_space_mb + 6
    expected_deleted = ["e", "f", "g"]
    run_end_to_end(options, expected_deleted)


# test --min-free doesn't delete when there is enough free space
def test_nothing_deleted_with_min_free():
    options = OptionsClass()
    options.days = 5
    options.min_free = mock_free_space_mb - 1
    expected_deleted = []
    run_end_to_end(options, expected_deleted)


# test files deleted due to --trash-limit
def test_deleted_with_trash_limit():
    options = OptionsClass()
    options.days = 5
    options.trash_limit = 4
    expected_deleted = ["d", "e", "f", "g"]
    run_end_to_end(options, expected_deleted)


# test --trash-limit doesn't delete when the trash is not occupied enough
def test_nothing_deleted_with_trash_limit():
    options = OptionsClass()
    options.days = 5
    options.trash_limit = 20
    expected_deleted = []
    run_end_to_end(options, expected_deleted)


# -------- original tests ----------


def should_survive_zero_length_config():
    assert autotrash.get_trash_info_date(os.devnull) == None


def should_survive_config_with_zeros():
    (temp_handle, temp_file_path) = tempfile.mkstemp()
    os.close(temp_handle)
    with open(temp_file_path, "wb") as tf:
        print(repr(tf))
        tf.write(b"\0x0\0x0\0x0\0x0")

    try:
        autotrash.get_trash_info_date(temp_file_path) == None
    finally:
        os.unlink(temp_file_path)


def should_read_datetime_for_all_known_formats():
    assert autotrash.read_datetime("2019-10-17T15:33:57") == datetime.datetime(
        2019, 10, 17, 15, 33, 57
    )
    assert autotrash.read_datetime("2019-10-17T15:33:57.710Z") == datetime.datetime(
        2019, 10, 17, 15, 33, 57, 710000
    )


def should_format_bytes_nicely():
    assert autotrash.fmt_bytes(10) == "10 bytes"
    assert autotrash.fmt_bytes(1024) == "1.0 KiB"
    assert autotrash.fmt_bytes(1024 * 1024) == "1.0 MiB"
    assert autotrash.fmt_bytes(1024 * 1024 + 512 * 1024) == "1.5 MiB"
