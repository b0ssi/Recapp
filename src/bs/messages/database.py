#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

"""

import bs.config


def general_error(path, e):
    """ * """
    exception_msg = "A general database-error occurred: %s. "\
                    "Database-location: %s" % (e, path, )
    exit_msg = "EXIT: Operation on the database could not be successfully "\
               "completed; system needs to exit."

    out = [exception_msg, exit_msg]
    return out


def access_denied(path, e):
    """ * """
    exception_msg = "Database file does exist at location '%s' but is either "\
                    "an invalid %s database, currently accessed "\
                    "by a different process or inaccessible (\"%s\").\r"\
                    % (path, bs.config.PROJECT_NAME, e)
    exit_msg = "EXIT: Program can not proceed without database access; "\
               "please make sure the database file at\r'%s'\ris a valid "\
               "sqlite3 database and it is not used by a different process. "\
               "Deleting the file will force-initialize %s to "\
               "create a blank database. WARNING: All data stored in the "\
               "database will be lost!" % (path, bs.config.PROJECT_NAME, )

    out = [exception_msg, exit_msg]
    return out
