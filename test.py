#!/usr/bin/python
import tempfile
import os

#Dynamically load autotrash because it has no .py extension
import imp
autotrash = imp.load_source('autotrash', './autotrash')


def should_survive_zero_length_config_test():
    assert autotrash.trash_info_date(os.devnull) == None


# def should_survive_config_with_zeros_test():
#     (tempHandle, tempFilePath) = tempfile.mkstemp()
#     os.close(tempHandle)
#     with open(tempFilePath, 'wb') as tf:
#         print(repr(tf))
#         tf.write(b'\0x0\0x0\0x0\0x0')
#     try:
#         autotrash.trash_info_date(tempFilePath) == None
#     finally:
#         os.unlink(tempFilePath)
#     pass