#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

"""


def general_error(e):
    """ * """
    exception_msg = "A general error occurred: %s" % (e, )
    exit_msg = "EXIT: Operation could not be successfully completed; system "\
               "needs to exit."

    out = [exception_msg, exit_msg]
    return out


def PATTERN_NAME_INVALID():
    """ * """
    msg_default = "The given name is invalid or contains illegal characters."
    msg_detailed = "A valid name needs to follow these rules:\n"
    msg_detailed += "\n"
    msg_detailed += "- begin with a lower- or upper-case Latin character\n"
    msg_detailed += "- only contain Latin characters, Arabic numbers and any of the following characters, as well as spaces: _ - #\n"
    msg_detailed += "- can not end with a space character\n"
    msg_detailed += "- have a length between 3 and 32"

    out = [msg_default, msg_detailed]
    return out
