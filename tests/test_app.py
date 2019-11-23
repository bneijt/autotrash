import os
import tempfile
import datetime
import autotrash


def should_survive_zero_length_config():
    assert autotrash.trash_info_date(os.devnull) == None


def should_survive_config_with_zeros():
    (temp_handle, temp_file_path) = tempfile.mkstemp()
    os.close(temp_handle)
    with open(temp_file_path, 'wb') as tf:
        print(repr(tf))
        tf.write(b'\0x0\0x0\0x0\0x0')

    try:
        autotrash.trash_info_date(temp_file_path) == None
    finally:
        os.unlink(temp_file_path)


def should_read_datetime_for_all_known_formats():
    assert autotrash.read_datetime('2019-10-17T15:33:57') == datetime.datetime(2019, 10, 17, 15, 33, 57)
    assert autotrash.read_datetime('2019-10-17T15:33:57.710Z') == datetime.datetime(2019, 10, 17, 15, 33, 57, 710000)
