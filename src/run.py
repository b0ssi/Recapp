# -*- coding: utf-8 -*-

###############################################################################
##    run.py                                                                 ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Mar 9, 2013                                            ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################

# imports
import config
import hashlib
import logging
import models
import os
import sqlite3

# logging
#logger = logging.Logger('root')
logging.basicConfig(format="--------------- %(module)s: %(lineno)s (%(funcName)s)\r%(levelname)s      \t%(message)s", level=logging.DEBUG)

logging.info("Backupshizzle is initializing...")

## create DB
#def db_create():
#    logging.info("Checking for existing config database...")
#    # check DB for existence and integrity
#    if not os.path.exists(config.CONFIGDB_PATH) and not os.path.isfile(config.CONFIGDB_PATH):
#        try:
#            logging.info("Database does not exist; setting-up a new database...")
#            # set-up new database
#            conn = sqlite3.connect(config.CONFIGDB_PATH)
#            cursor = sqlite3.Cursor(conn)
#            cursor.execute("CREATE TABLE `users` (username TEXT, password TEXT)")
#            cursor.execute("CREATE TABLE `sources` (id TEXT, userId INTEGER, sourcePath TEXT)")
#            cursor.execute("CREATE TABLE `sets` (setId INTEGER, userId INTEGER, title TEXT, sources TEXT, filters TEXT, targets TEXT)")
#            cursor.execute("CREATE TABLE `filters` (id TEXT, userId INTEGER)")
#            cursor.execute("CREATE TABLE `targets` (userId INTEGER, targetTitle INTEGER, targetId INTEGER)")
#            cursor.execute("INSERT INTO `users` (`username`, `password`) VALUES ('1', '4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f9bd058a12a280433ed6fa46510a')")
#            cursor.execute("INSERT INTO `users` (`username`, `password`) VALUES ('2', '40b244112641dd78dd4f93b6c9190dd46e0099194d5a44257b7efad6ef9ff4683da1eda0244448cb343aa688f5d3efd7314dafe580ac0bcbf115aeca9e8dc114')")
#            conn.commit()
#            cursor.close()
#            conn.close()
#            logging.info("New database set-up successfully.")
#        except Exception as e:
#            logging.critical("Database file is unaccessible or doesn't exist and cannot be created at location %s (%s).\r" % (config.CONFIGDB_PATH, e))
#            raise
#    else:
#        try:
#            conn = sqlite3.connect(config.CONFIGDB_PATH)
#            cursor = sqlite3.Cursor(conn)
#            cursor.execute("SELECT `username`, `password` FROM `users` WHERE `rowid` = '0'")
#            cursor.execute("SELECT `id`, `userId`, `sourcePath` FROM `sources` WHERE `rowid` = '0'")
#            cursor.execute("SELECT `setId`, `userId`, `title`, `sources`, `filters`, `targets` FROM `sets` WHERE `rowid` = '0'")
#            cursor.execute("SELECT `id`, `userId` FROM `filters` WHERE `rowid` = '0'")
#            cursor.execute("SELECT `userId`, `targetTitle`, `targetId` FROM `targets` WHERE `rowid` = '0'")
#            conn.close()
#            logging.info("Valid database found.")
#        except Exception as e:
#            logging.critical("Database file does exist at location %s but is either an invalid Backupshizzle database or inaccessible (%s).\r" % (config.CONFIGDB_PATH, e))
#            raise
#
#db_create()


class SessionsModel(object):
    _sessions = []

    def __init__(self):
        super(SessionsModel, self).__init__()

    def add_session(self, session):
        logging.info("Adding a new session to runtime...")
        self._sessions.append(session)
        logging.info("New session successfully added to runtime.")

    def __repr__(self):
        return str(self._sessions)


class SessionModel(object):
    _user = None
    _sources = None
    __backup_targets= None
    __backup_filters= None
    __backup_sets= None

    def __init__(self, user):
        super(SessionModel, self).__init__()

        logging.info("Initializing session...")
        if user.is_logged_in() == True:
            self._user = user
            logging.info("Session with user '%s' successfully created." % user._username)
        else:
            logging.critical("User '%s' is not logged in. Exiting." % user._username)
            exit()

    def __repr__(self):
        return(str((self._user, self._sources, self.__backup_targets self._filters, self._sets)))


class UserModel(object):
    _username = ""
    _is_logged_in = False

    def __init__(self, username):
        super(UserModel, self).__init__()

        logging.info("Checking if user '%s' exists in db..." % username)
        self._username = username
        # check that user exists in db
        conn = sqlite3.connect(config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        res = cursor.execute("SELECT `username` FROM `users` WHERE `username`=?", (username,)).fetchone()
        conn.close()
        try:
            username_db = res[0]
            username_db == username
            logging.info("User '%s' successfully found in db." % username)
        except Exception as e:
            logging.critical("User '%s' does not exist in db (%s).\r" % (username, e))
            raise

        self._is_logged_in = False

    def log_in(self, password):
        logging.info("Authenticating user '%s'..." % (self._username,))
        # Authenticate user
        password_hash = hashlib.sha512()
        password_hash.update(password.encode())
        password_hash = password_hash.hexdigest()

        conn = sqlite3.connect(config.CONFIGDB_PATH)
        cursor = sqlite3.Cursor(conn)
        password = cursor.execute("SELECT `password` FROM `users` WHERE `username`=? AND `password`=?", (self._username, password_hash)).fetchone()
        if password == None:
            logging.error("Authentication unsuccessful. Please try again.")
            return False
        elif len(password[0]) == 128:
            self._is_logged_in = True
            logging.info("Authentication successful, user '%s' logged-in." % (self._username,))
            return True

    def log_out(self):
        self._is_logged_in = False

    def is_logged_in(self):
        return self._is_logged_in

    def __repr__(self):
        return(str(self._username))


#UI = False
## initialize sessions object
#SESSIONS = SessionsModel()
## create a new user
#new_user = UserModelNew()
#new_user.log_in("2", "2")
## create a new session
#new_session = SessionModel(new_user)
#SESSIONS.add_session(new_session)
#
#if UI == False:
#    pass
#elif UI == True:
#    pass
