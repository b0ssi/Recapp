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
""" ..

"""

from PySide import QtGui

import bs.ctrl._db
import bs.ctrl.session
import logging
import os
import re
import sqlite3
import sys
import time


# extract sys.argv
gui_mode = True
dev_mode = False

for arg in sys.argv:
    if re.match("^\-gui$", arg):
        gui_mode = True
    if re.match("^\-dev$", arg):
        dev_mode = True


# logging
logging_level = logging.DEBUG
logging_filename = bs.config.LOGFILE_PATH
if dev_mode:
    logging_level = logging.WARNING
    logging_filename = False
#logger = logging.Logger('root')
logging.basicConfig(format="%(asctime)s %(levelname)s: \t%(message)s [Module: %(module)s, Line: %(lineno)s, Method: %(funcName)s]",
                    level=logging_level,
                    filename=logging_filename,
                    datefmt="%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    """ * """
    ## INITIAL CHECKS ##
    if gui_mode:
        # check DB existence/validity
        errors_acc = []
        if os.path.isfile(bs.config.CONFIGDB_PATH):
            f = open(bs.config.CONFIGDB_PATH, 'rb')
            if os.path.getsize(bs.config.CONFIGDB_PATH) < 100 or\
                f.read(16) != b"SQLite format 3\x00":
                error_msg = "The file is not a valid SQLite3 database: "\
                            "%s" % (bs.config.CONFIGDB_PATH, )
                errors_acc.append(error_msg)
                logging.critical("%s" % (error_msg, ))
        else:
            error_msg = "No application-database was found at %s." \
                        % (bs.config.CONFIGDB_PATH, )
            errors_acc.append(error_msg)
            logging.critical("%s" % (error_msg, ))
        if len(errors_acc) > 0:
            app = QtGui.QApplication("preliminary_check")
            out = "Error(s) were detected when initializing %s:\n\n" \
                  % (bs.config.PROJECT_NAME, )
            for i in range(len(errors_acc)):
                out += "> " + errors_acc[i] + "\n"
            msg_window = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error",
                                           out)
            app.setWindowIcon(QtGui.QIcon("img\\recapp_emblem_noname.png"))
            msg_window.exec_()
            app.exec_()
            sys.exit()
    if dev_mode:
        # sync db
        sync_db = bs.ctrl._db.SyncDb("bs.model.models")
        sync_db.sync()
    # init sessions
    sessions = bs.ctrl.session.SessionsCtrl(gui_mode)

# # PREP
# # sync db if necessary
# sync_db = bs.ctrl._db.SyncDb("bs.model.models")
# sync_db.sync()
#
# my_sessions_1 = bs.ctrl.session.SessionsCtrl()
# my_session_1 = my_sessions_1.add_session("alpha", "1")
#
# print(my_session_1.backup_sets.sets[0].backup_sources)
# print(my_session_1.backup_sets.sets[0].backup_filters)
# print(my_session_1.backup_sets.sets[0].backup_targets)
# print(my_session_1.backup_sets.sets[0].backup_sources[0].source_path)
# print(my_session_1.backup_sets.sets[0].backup_targets[0]._target_device_id)
#
# my_backup = bs.ctrl.backup.Backup(my_session_1.backup_sets.sets[0])
# print(my_backup.bytes_total)
# print(my_backup.files_num_total)


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

# my_backup = bs.ctrl.backup.Backup(
#                                   my_sets_1.sets[0]
#                                   )
# my_backup.backup_exec()

#my_backup_restore = bs.ctrl.backup.BackupRestore(my_sets_1.sets[0],
#                                            [10261],
#                                            "Z:\\test_restore",
#                                            1367853693)
#my_backup_restore.start()
