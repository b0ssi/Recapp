# -*- coding: utf-8 -*-

###############################################################################
##    strings                                                                ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Mar 11, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################


def general_error(path, e):
    exception_msg = "A general database-error occurred: %s. "\
                    "Database-location: %s" % (e, path, )
    exit_msg = "EXIT: Operation on the database could not be successfully "\
               "completed; system needs to exit."

    out = [exception_msg, exit_msg]
    return out


def access_denied(path, e):
    exception_msg = "Database file does exist at location '%s' but is either an invalid Backupshizzle database, currently accessed by a different process or inaccessible (\"%s\").\r" % (path, e)
    exit_msg = "EXIT: Program can not proceed without database access; please make sure the database file at\r'%s'\ris a valid sqlite3 database and it is not used by a different process. Deleting the file will force-initialize Backupshizzle to create a blank database. WARNING: All data stored in the database will be lost!" % path

    out = [exception_msg, exit_msg]
    return out
