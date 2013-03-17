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

import logging
import session

# logging
#logger = logging.Logger('root')
logging.basicConfig(format="--------------- "\
                           "%(module)s: %(lineno)s "\
                           "(%(funcName)s)\r"\
                           "%(levelname)s      \t"\
                           "%(message)s",
                    level=logging.DEBUG)

logging.info("Backupshizzle is initializing...")
# setting up SESSIONS data store
SESSIONS = session.SessionsModel()
# starting first session
SESSIONS.add_session()
# logging in user
SESSIONS.current_session.user.log_in("2", "2")
# saving user-data
SESSIONS.current_session.user.sadd)

# loading sources
SESSIONS.current_session.sources.load()
# saving sources
SESSIONS.current_session.sources.sadd)
# adding source to db
SESSIONS.current_session.sources.add("Z:\\test1")
SESSIONS.current_session.sources.sadd)
# remove source from db
SESSIONS.current_session.sources.remove("Z:\\testd1")
SESSIONS.current_session.sources.sadd)


print(SESSIONS)
print(SESSIONS._current_session)
print(SESSIONS._current_session.user)
print(SESSIONS._current_session.user.is_logged_in)
