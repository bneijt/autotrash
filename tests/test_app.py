import os
import tempfile
import datetime
import autotrash

class OptionsClass:
    days=0
    trash_path=None
    max_free=0
    delete=0
    min_free=0
    verbose=False
    quiet=False
    check=False
    dryrun=True
    stat=False
    delete_first=[]
    version=False

file_info_map = {}

def mock_get_file_names(trash_info_path):
    return []

def mock_get_cur_time():
    return 1000000

def mock_get_consumed_size(file_name):
    return 123

def mock_get_trash_info_date(value: str) -> datetime.datetime:
    return datetime.datetime(2000, 12, 25)

def mock_purge(trash_directory, trash_name, dryrun):
    return

class FsStat:
    f_bsize=1024
    f_bavail=100

def mock_get_fs_stat(trash_info_path):
    fs_stat = FsStat()
    return fs_stat

def add_mock_file(name, time, size):

def test_gil2():
    options = OptionsClass()
    stats = autotrash.StatsClass()
    os_access = autotrash.OsAccess()
    os_access.get_file_names = mock_get_file_names
    os_access.get_cur_time = mock_get_cur_time
    os_access.get_consumed_size = mock_get_consumed_size
    os_access.get_fs_stat = mock_get_fs_stat
    os_access.get_trash_info_date = mock_get_trash_info_date
    os_access.purge = mock_purge

    add_mock_file()

    autotrash.process_path("", options, stats, os_access)


# -------- originals ----------

def should_survive_zero_length_config():
    assert autotrash.get_trash_info_date(os.devnull) == None


def should_survive_config_with_zeros():
    (temp_handle, temp_file_path) = tempfile.mkstemp()
    os.close(temp_handle)
    with open(temp_file_path, 'wb') as tf:
        print(repr(tf))
        tf.write(b'\0x0\0x0\0x0\0x0')

    try:
        autotrash.get_trash_info_date(temp_file_path) == None
    finally:
        os.unlink(temp_file_path)


def should_read_datetime_for_all_known_formats():
    assert autotrash.read_datetime('2019-10-17T15:33:57') == datetime.datetime(2019, 10, 17, 15, 33, 57)
    assert autotrash.read_datetime('2019-10-17T15:33:57.710Z') == datetime.datetime(2019, 10, 17, 15, 33, 57, 710000)


def should_format_bytes_nicely():
    assert autotrash.fmt_bytes(10) == "10 bytes"
    assert autotrash.fmt_bytes(1024) == "1.0 KiB"
    assert autotrash.fmt_bytes(1024 * 1024) == "1.0 MiB"
    assert autotrash.fmt_bytes(1024 * 1024 + 512 * 1024) == "1.5 MiB"
