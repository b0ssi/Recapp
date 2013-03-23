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
import bs.messages.database
import bs.models
import hashlib
import logging
import os
import re
import sqlite3


class SessionsModel(object):
    """
    Stores and manages sessions for all active users.
    """
    _sessions = []
    _current_session = None

    def __init__(self):
        super(SessionsModel, self).__init__()
        # add initial session
        self.add_session()

    def __repr__(self):
        return str(self._sessions)

    @property
    def current_session(self):
        """
        Returns the currently active session.
        """
        return self._current_session

    @current_session.setter
    def current_session(self, arg):
        """
        Sets a session as the currently active session.
        """
        if isinstance(arg, SessionModel):
            self._current_session = arg
            logging.info("%s: Session '%s' successfully set as active session."
                         % (self.__class__.__name__, arg, ))
            return True
        else:
            logging.warning("%s: Argument 1 needs to be an instance of "\
                            "the 'SessionModel()' class." % (self.__class__.__name__))
            return False

    def add_session(self):
        """
        Adds a new session including an empty set for the user, sources,
        targets, filters, sets, etc..
        """
        logging.info("%s: Adding session to sessions..." % (self.__class__.__name__, ))
        # create new session
        new_session = SessionModel()
        # add new session to self._sessions
        self._sessions.append(new_session)
        self.current_session = new_session
        logging.info("%s: Session successfully added." % (self.__class__.__name__, ))
        return True


class SessionModel(object):
    """
    Stores and manages contents of a single session. user, sources, targets,
    filters, sets, etc..
    """
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
    """
    Represents an active user.
    """
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
        """
        Loggs the user in.
        """
        # VALIDATE DATA
        # username
        if not re.search(bs.config.REGEX_PATTERN_USERNAME, username):
            logging.warning("%s: The username is invalid. A valid username "\
                             "needs to start with an alphabetic, "\
                             "contain alphanumeric plus '_' "\
                             "and have a length between 4 and 32 characters."
                             % (self.__class__.__name__, ))
            return False

        if self.is_logged_in:
            logging.info("%s: User '%s' is already logged in."
                         % (self.__class__.__name__, self._username, ))
            return True
        else:
            password_hash = hashlib.sha512(password.encode())
            res = self.get("id", (("username", "=", username),
                             ("password", "=", password_hash.hexdigest(), ), ))
            if len(res) == 1:
                self._id = res[0][0]
                self._username = username
                logging.info("%s: User '%s' successfully logged in."
                             % (self.__class__.__name__, self._username, ))
                self._is_logged_in = True
                return True
            elif len(res) > 1:
                logging.critical("%s: More than one user exist with the same "\
                                 "username/password combination! Please check "\
                                 "the integrity of the database."
                                 % (self.__class__.__name__, ))
                raise SystemExit()
                return False
            elif len(res) < 1:
                logging.warning("%s: Username or password is invalid, please try "\
                                "again."
                                % (self.__class__.__name__, ))
                return False

    def log_out(self):
        """
        Loggs the user out.
        """
        # if already logged out
        if not self._is_logged_in:
            logging.warning("%s: User '%s' is already logged out."
                         % (self.__class__.__name__, self._username, ))
            return False
        # else, log-out
        else:
            self._is_logged_in = False
            logging.info("%s: User '%s' successfully logged out."
                         % (self.__class__.__name__, self._username, ))
            return True


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
