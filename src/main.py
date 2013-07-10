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

""" * """

import bs.ctrl._db
import bs.ctrl.backup
import bs.ctrl.session
import json
import logging
import os
import re
import sys
import time


# logging
#logger = logging.Logger('root')
logging.basicConfig(format="--------------- "\
                           "%(module)s: %(lineno)s "\
                           "(%(funcName)s)\r"\
                           "%(levelname)s      \t"\
                           "%(message)s",
                    level=logging.WARNING)


if __name__ == '__main__':
    """ * """
    # extract sys.argv
    gui_mode = False

    for arg in sys.argv:
        if re.match("^gui\=True$", arg):
            gui_mode = True
    # sync db
    sync_db = bs.ctrl._db.SyncDb("bs.model.models")
    sync_db.sync()
    # init sessions
    sessions = bs.ctrl.session.SessionsCtrl(gui_mode)


## PREP
## sync db if necessary
#sync_db = bs.ctrl._db.SyncDb("bs.model.models")
#sync_db.sync()
#
#my_sessions_1 = bs.ctrl.session.SessionsCtrl()
#my_session_1 = my_sessions_1.add_session("alpha", "1")
#
#my_session_2 = my_sessions_1.add_session("bravo", "2")


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

#my_backup = bs.ctrl.backup.Backup(
#                             my_sets_1.sets[0]
#                             )
#my_backup.backup_exec()

#my_backup_restore = bs.ctrl.backup.BackupRestore(my_sets_1.sets[0],
#                                            [10261],
#                                            "Z:\\test_restore",
#                                            1367853693)
#my_backup_restore.start()
