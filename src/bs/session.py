# -*- coding: utf-8 -*-

###############################################################################
##    session                                                                ##
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

from bs.utils import BSString
import bs._db
import bs.config
import hashlib
import logging
import bs.messages.database
import bs.models
import os
import sqlite3


class SessionsModel(object):
    _sessions = []
    _current_session = None

    def __init__(self):
        super(SessionsModel, self).__init__()
        # add initial session
        self.add_session()

    def add_session(self):
        logging.info("Adding session to sessions...")
        # create new session
        new_session = SessionModel()
        # add new session to self._sessions
        self._sessions.append(new_session)
        self._current_session = new_session
        return True

    @property
    def current_session(self):
        return self._current_session

    @current_session.setter
    def current_session(self, arg):
        self._current_session = arg

    def __repr__(self):
        return str(self._sessions)


class SessionModel(object):
    _user = None
    _backup_sources = None
    _backup_targets = None
    _backup_filters = None
    _backup_sets = None

    def __init__(self):
        super(SessionModel, self).__init__()

        self._user = UserModelNew()
        self._backup_sources = BackupSourcesModelNew()
        self._backup_targets = BackupTargetsModelNew()
        self._backup_filters = BackupFiltersModelNew()
        self._backup_sets = BackupSetsModelNew()

    def __repr__(self):
        return(str((self._user,
                    self._backup_sources,
                    self._backup_targets,
                    self._backup_filters,
                    self._backup_sets))
               )

    @property
    def user(self):
        return self._user

    @property
    def backup_sources(self):
        return self._backup_sources

    @property
    def backup_targets(self):
        return self._backup_targets

    @property
    def backup_filters(self):
        return self._backup_filters

    @property
    def backup_sets(self):
        return self._backup_sets


class UserModelNew(bs.models.Users):
    _id = -1
    _is_logged_in = False
    _username = ""

    def __init__(self):
        super(UserModelNew, self).__init__()
        # create default user
        if len(self.get("*")) == 0:
            self.add("username, password",
                      [['1', '4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f9bd058a12a280433ed6fa46510a']])
            self.add("username, password",
                      [['2', '40b244112641dd78dd4f93b6c9190dd46e0099194d5a44257b7efad6ef9ff4683da1eda0244448cb343aa688f5d3efd7314dafe580ac0bcbf115aeca9e8dc114']])

    def __repr__(self):
        return "User '%s' <%s>" % (self._username, self.__class__.__name__, )

    @property
    def id(self):
        return self._id

    @property
    def is_logged_in(self):
        return self._is_logged_in

    def log_in(self, username, password):
        if not self.is_logged_in:
            password_hash = hashlib.sha512(password.encode())
            res = (self.get("id", (("username", "=", username),
                             ("password", "=", password_hash.hexdigest(), ), )))
            if len(res) == 1:
                self._id = res[0][0]
                self._username = username
                logging.info("User '%s' successfully logged in." % (self._username, ))
                self._is_logged_in = True
                return True
            elif len(res) > 1:
                logging.critical("More than one user exist with the same "\
                                 "username/password combination! Please check "\
                                 "consistency of the database.")
                raise SystemExit()
                return False
            elif len(res) < 1:
                logging.warning("Username or password is invalid, please try "\
                                "again.")
                return False

    def log_out(self):
        self._is_logged_in = False
        logging.info("User '%s' successfully logged out." % (self._username))


class BackupSourcesModelNew(bs.models.Sources):
    def __init__(self):
        super(BackupSourcesModelNew, self).__init__()

    def __repr__(self):
        return "Sources <%s>" % (self.__class__.__name__, )


class BackupTargetsModelNew(bs.models.Targets):
    def __init__(self):
        super(BackupTargetsModelNew, self).__init__()

    def __repr__(self):
        return "Targets <%s>" % (self.__class__.__name__)


class BackupFiltersModelNew(bs.models.Filters):
    def __init__(self):
        super(BackupFiltersModelNew, self).__init__()

    def __repr__(self):
        return "Filters <%s>" % (self.__class__.__name__)


class BackupSetsModelNew(bs.models.Sets):
    def __init__(self):
        super(BackupSetsModelNew, self).__init__()

    def __repr__(self):
        return "Sets <%s>" % (self.__class__.__name__)
