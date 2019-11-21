import os
import tempfile

import autotrash


def should_survive_zero_length_config_test():
    assert autotrash.trash_info_date(os.devnull) == None


def should_survive_config_with_zeros_test():
    (temp_handle, temp_file_path) = tempfile.mkstemp()
    os.close(temp_handle)
    with open(temp_file_path, 'wb') as tf:
        print(repr(tf))
        tf.write(b'\0x0\0x0\0x0\0x0')

    try:
        autotrash.trash_info_date(temp_file_path) == None
    finally:
        os.unlink(temp_file_path)
