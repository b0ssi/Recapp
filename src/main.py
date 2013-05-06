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
my_sets_1 = my_session_1.backup_sets

my_user_1.log_in("alpha", "1")

#print(my_sets_1.sets[0].targets)
#my_sets_1.sets[0].sources = [
#                             my_sources_1.sources[0],
#                             my_sources_1.sources[1]
#                            ]
#my_sets_1.sets[0].filters = [
#                             my_filters_1.filters[0],
#                             my_filters_1.filters[1],
#                             my_filters_1.filters[2]
#                            ]
#my_sets_1.sets[0].targets = [
#                             my_targets_1.targets[0]
#                            ]
#my_sets_1.add("My awesommmmme set2",
#              "12345678",
#              "Z:\\test.sqlite",
#              (my_sources_1.sources[0], my_sources_1.sources[1], ),
#              (my_filters_1.filters[0], my_filters_1.filters[1], my_filters_1.filters[2], ),
#              (my_targets_1.targets[0], )
#              )
#my_targets_1.remove(my_targets_1.targets[0])
#print(my_sets_1.sets[0].targets)

time_start = time.time()

#my_backup = bs.backup.Backup(
#                             my_sets_1.sets[0]
#                             )
#my_backup.backup_exec()

#my_backup_restore = bs.backup.BackupRestore(my_sets_1.sets[0],
#                                            [10261],
#                                            "Z:\\test_restore",
#                                            1367853693)
#my_backup_restore.start()

print("Time elapsed: %s" % (time.time() - time_start))
