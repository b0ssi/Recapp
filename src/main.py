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
SESSIONS.current_session.user.log_in("2", "2")
SESSIONS.current_session.backup_sources.add("user_id, source_path",
                                             ((SESSIONS.current_session.user.id,
                                               os.path.realpath("Z:/x")), ))
SESSIONS.current_session.backup_sources.remove((("user_id", "=", 2, ), ))

print(SESSIONS)