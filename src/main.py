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
import bs.session
import logging
import os


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

# create a sessions host
SESSIONS = bs.session.SessionsModel()
# log-in
SESSIONS.current_session.user.log_in("bravo", "2")
# SESSION 2
session_alpha = SESSIONS.add_session()
#SESSIONS.current_session.user.log_in("alpha", "1")
SESSIONS.current_session.backup_sources.add("MyAwesomeSource #13049", "Z:\\test2")
SESSIONS.remove_session(SESSIONS.current_session)
# SESSION 1 AGAIN
SESSIONS.current_session.backup_sources.add("MySource", "Z:\\test")
SESSIONS.current_session.backup_sources.add("MySource #2", "Z:\\test2")

SESSIONS.current_session.backup_targets.add("My target #1", "Z:\\")

SESSIONS.current_session.backup_sets.add("My_Set", (2, 3, ), (4, 67, ), (4, 6, 1, 31, ))
SESSIONS.current_session.backup_sets.remove(1)
