# -*- coding: utf-8 -*-

###############################################################################
##    main                                                                   ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2012 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Mar 9, 2013                                            ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################

import bs._db
import bs.backup
import bs.session
import logging
import os
import time


# logging
#logger = logging.Logger('root')
logging.basicConfig(format="--------------- "\
                           "%(module)s: %(lineno)s "\
                           "(%(funcName)s)\r"\
                           "%(levelname)s      \t"\
                           "%(message)s",
                    level=logging.DEBUG)

# PREP
# sync db if necessary
sync_db = bs._db.SyncDb("bs.models")
sync_db.sync()


my_sessions_1 = bs.session.SessionsCtrl()
my_session_1 = my_sessions_1.current_session
my_user_1 = my_session_1.user
my_sources_1 = my_session_1.backup_sources
my_filters_1 = my_session_1.backup_filters
my_targets_1 = my_session_1.backup_targets

my_user_1.log_in("alpha", "1")

print(my_targets_1.targets)
#my_targets_1.add("FiLtErPaTtErN BaBy4", "Z:\\")
my_targets_1.remove(my_targets_1.targets[0])
print(my_targets_1.targets)

## create a sessions host
#SESSIONS = bs.session.SessionsCtrl()
## log-in
#SESSIONS.current_session.user.log_in("bravo", "2")
## SESSION 2
#session_alpha = SESSIONS.add_session()
##SESSIONS.current_session.user.log_in("alpha", "1")
#SESSIONS.current_session.backup_sources.add("MyAwesomeSource #13049", "Z:\\test2")
#SESSIONS.remove_session(SESSIONS.current_session)
## SESSION 1 AGAIN
#SESSIONS.current_session.backup_sources.add("sx2", "Y:\\_TMP\\bsTest\\sx2")
#
#SESSIONS.current_session.backup_filters.add("filter")
#
#SESSIONS.current_session.backup_targets.add("My target #1", "Z:\\")
#
#SESSIONS.current_session.backup_sets.add("My_Set", (1, ), (1, ), (1, ))
##SESSIONS.current_session.backup_sets.remove(1)
#
#time_start = time.time()
#
##my_backup = bs.backup.Backup(
##                   "backup_test",
##                   ["Y:\\_TMP\\bsTest\\sx2"],
##                   ["Y:\\_TMP\\bsTest\\t1",
##                    "Y:\\_TMP\\bsTest\\t2"
##                    ],
##                   "Z:\\test.sqlite"
##                   )
##my_backup.backup_exec()
#
#print(dir(SESSIONS.current_session.backup_sets))
#
##my_backup_restore = bs.backup.BackupRestore(
##                                            SESSIONS.current_session.,
##                                            "myPassword",
##                                            1,
##                                            "Y:\\_TMP\\bsTest\\restore"
##                                            )
##my_backup_restore = BackupRestore(r"Y:\_TMP\bsTest\t1\backup_test\1365492971.zip",
##                                  r"Y:\_TMP\bsTest\t1\backup_test")
#
#print("Time elapsed: %s" % (time.time() - time_start))
