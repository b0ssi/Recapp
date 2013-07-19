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

from PySide import QtCore, QtGui
import binascii
import bs.config
import bs.ctrl.backup
import bs.gui.window_main
import bs.messages
import bs.model.models
import Crypto.Hash.SHA256
import Crypto.Protocol.KDF
import hashlib
import json
import logging
import os
import random
import re
import sqlite3
import time
import win32file

""" * """



class SessionsCtrl(object):
    """
    Stores and manages sessions for all is_unlocked users.
    """
    _sessions = None  # holds currently is_unlocked sessions
    # gui
    _app = None
    _guis = None  # holds currently is_unlocked guis that (actively) respectively manage a session
    _gui_mode = None

    def __init__(self, gui_mode=False):
        super(SessionsCtrl, self).__init__()
        self._gui_mode = gui_mode

        self._sessions = []
        self._guis = []
        # gui stuff
        if self._gui_mode:
            self._app = bs.gui.window_main.Application("asdf")
            self._app.setWindowIcon(QtGui.QIcon("img/favicon.png"))
            self.add_session_gui(self._app)
            self._app.exec_()

    def __repr__(self):
        return str(self._sessions)

    @property
    def app(self):
        return self._app

    @property
    def guis(self):
        return self._guis

    @property
    def sessions(self):
        return self._sessions

    def add_session(self, username, password):
        """
        If attributed credentials are valid, return logged on, unlocked session
        for user.
        Returns existing session if one was previously created (used) for user.
        Fails if session for requested user is already logged in and unlocked.
        """
        logging.info("%s: Creating session for user %s..."
                     % (self.__class__.__name__,
                        username, ))
        # check if session for user already exists
        new_session = None
        for session in self._sessions:
            if session.user.username == username:
                new_session = session
                break
        # if no existing sessionf or user was found
        if not new_session:
            # create new session
            new_session = SessionCtrl()
        # verify scenarios
        if new_session.is_logged_in:
            if not new_session.is_unlocked:
                if new_session.log_in(username, password):
                    # add new_session to self._sessions
                    if new_session not in self._sessions:
                        self._sessions.append(new_session)
                    logging.info("%s: New session successfully unlocked."
                                 % (self.__class__.__name__, ))
                    return new_session
                else:
                    logging.warning("%s: No session created: Log-on failed."
                                 % (self.__class__.__name__, ))
                    return False
            else:
                logging.warning("%s: The session for this user is already active."
                             % (self.__class__.__name__, ))
                return -1
        else:
            if new_session.log_in(username, password):
                # add new_session to self._sessions
                if new_session not in self._sessions:
                    self._sessions.append(new_session)
                logging.info("%s: New session successfully logged in and unlocked."
                             % (self.__class__.__name__, ))
                return new_session
            else:
                logging.warning("%s: No session created: Log-on failed."
                             % (self.__class__.__name__, ))
                return False

    def remove_session(self, session):
        """ *
        Removes an existing session including all of its associated objects.
        """
        if session:
            self._sessions.pop(self._sessions.index(session))
            logging.info("%s: Session successfully removed: %s"
                         % (self.__class__.__name__, session, ))
        else:
            logging.warning("%s: The session does not exist: %s"
                            % (self.__class__.__name__, session, ))

    def add_session_gui(self, app):
        """ *
        Adds a new UI instance to host a separate is_unlocked session.
        """
        session_gui = SessionGuiCtrl(self, app)
        self._guis.append(session_gui)
        return session_gui

    def remove_session_gui(self, session_gui):
        """ *
        Removes the session_gui instance from this Sessions.
        """
        self._guis.pop(self._guis.index(session_gui))
        return True


class SessionGuiCtrl(object):
    """ *
    Container for a GUI session
    """
    _sessions = None
    _app = None

    _main_window = None
    _session = None

    def __init__(self, sessions, app):

        self._sessions = sessions
        self._app = app

        self._main_window = bs.gui.window_main.WindowMain(self._sessions, self, self._app)

    @property
    def main_window(self):
        return self._main_window

    @property
    def sessions(self):
        return self._sessions

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        """ * """
        if not isinstance(session, SessionCtrl) and session:
            logging.warning("%s: The first argument needs to be of type "\
                            "`SessionCtrl`."
                            % (self.__class__.__name__, ))
            return False
        self._session = session
        return session


class SessionCtrl(object):
    """
    Stores and manages contents of a single session. user, sources, targets,
    filters, sets, etc..
    """
    _user = None
    _backup_sources = None
    _backup_targets = None
    _backup_filters = None
    _backup_sets = None
    _is_unlocked = None
    _is_logged_in = None

    def __init__(self):
        super(SessionCtrl, self).__init__()

        self._user = UserCtrl(self)
        self._backup_sources = BackupSourcesCtrl(self)
        self._backup_targets = BackupTargetsCtrl(self)
        self._backup_filters = BackupFiltersCtrl(self)
        self._backup_sets = BackupSetsCtrl(self)
        self._is_unlocked = False
        self._is_logged_in = False

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

    @property
    def is_unlocked(self):
        return self._is_unlocked

    @is_unlocked.setter
    def is_unlocked(self, arg):
        if not isinstance(arg, bool):
            logging.warning("%s: The first argument needs to be of type "\
                            "boolean."
                            % (self.__class__.__name__, ))
            return False
        self._is_unlocked = arg
        return True

    @property
    def is_logged_in(self):
        return self._is_logged_in

    @is_logged_in.setter
    def is_logged_in(self, arg):
        if not isinstance(arg, bool):
            logging.warning("%s: Argument one needs to be of type boolean."
                            % (self.__class__.__name__, ))
            return False
        self._is_logged_in = arg
        return True

    def log_in(self, username, password):
        """ * """
        # VALIDATE DATA
        # username
        if not re.search(bs.config.REGEX_PATTERN_USERNAME, username):
            logging.warning("%s: The username is invalid. A valid username "\
                             "needs to start with an alphabetic, "\
                             "contain alphanumeric plus '_' "\
                             "and have a length between 4 and 32 characters."
                             % (self.__class__.__name__, ))
            return False
        # CONTEXT CHECKS & SET-UP
        if not self.is_logged_in or\
            self.is_logged_in and not self._is_unlocked:
            if self.user._validate_credentials(self, username, password):
                self.is_unlocked = True
                self.is_logged_in = True
                logging.info("%s: Session successfully logged in."
                             % (self.__class__.__name__, ))
                return True
            else:
                logging.warning("%s: Session login failed: Invalid credentials."
                                % (self.__class__.__name__, ))
                return False
        elif self.is_unlocked:
            logging.warning("%s: Session already logged in."
                            % (self.__class__.__name__, ))
            return False

    def log_out(self):
        """ * """
        if self.is_logged_in:
            self.is_unlocked = False
            self.is_logged_in = False
            logging.info("%s: Session successfully logged out."
                         % (self.__class__.__name__, ))
            return True
        else:
            logging.warning("%s: Session logout failed: Already logged out."
                            % (self.__class__.__name__, ))
            return False

    def lock(self):
        """ * """
        if self.is_logged_in:
            if self.is_unlocked:
                self.is_unlocked = False
                logging.info("%s: Session successfully locked."
                             % (self.__class__.__name__, ))
                return True
            else:
                logging.warning("%s: Session lock failed: Already locked."
                                % (self.__class__.__name__, ))
                return False
        else:
            logging.warning("%s: Session lock failed: Not logged in."
                            % (self.__class__.__name__, ))
            return False

    def unlock(self, username, password):
        """ * """
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
            if not self.is_unlocked:
                if self.user._validate_credentials(self, username, password):
                    self.is_unlocked = True
                    logging.info("%s: Session successfully unlocked."
                                 % (self.__class__.__name__, ))
                    return True
                else:
                    logging.warning("%s: Session unlock failed: Invalid "\
                                    "credentials."
                                    % (self.__class__.__name__, ))
            else:
                logging.warning("%s: Session unlock failed: Already "\
                                "unlocked."
                                % (self.__class__.__name__, ))
                return False
        else:
            logging.warning("%s: Session unlock failed: Not logged in."
                            % (self.__class__.__name__, ))
            return False


class UserCtrl(bs.model.models.Users):
    """ *
    Represents an is_unlocked user.
    """
    _id = None
    _username = None
    _session = None

    def __init__(self, session_gui):
        super(UserCtrl, self).__init__()
        self._session = session_gui

        self._id = -1
        self._username = ""
        # create default user
        if len(self._get("*", no_auth_required=True)) == 0:
            self._add("username, password",
                     [['alpha', '4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f9bd058a12a280433ed6fa46510a']],
                     no_auth_required=True)
            self._add("username, password",
                     [['bravo', '40b244112641dd78dd4f93b6c9190dd46e0099194d5a44257b7efad6ef9ff4683da1eda0244448cb343aa688f5d3efd7314dafe580ac0bcbf115aeca9e8dc114']],
                     no_auth_required=True)

    def __repr__(self):
        return "User '%s' <%s>" % (self._username, self.__class__.__name__, )

    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session.is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session.is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session.is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def _validate_credentials(self, parent, username, password):
        """ *
        Verifies `username`, `password` for correctness and returns boolean.
        This method can only be called from `parent=isinstance(SessionCtrl)`
        """
        if isinstance(parent, SessionCtrl):
            password_hash = hashlib.sha512(password.encode())
            res = self._get("id", (("username", "=", username),
                                  ("password", "=", password_hash.hexdigest(), ), ),
                           no_auth_required=True
                           )
            if len(res) == 1:
                self._id = res[0][0]
                self._username = username
                logging.debug("%s: Credentials valid for user: '%s'."
                             % (self.__class__.__name__, self._username, ))
                return True
            elif len(res) > 1:
                logging.critical("%s: More than one user exist with the same "\
                                 "username/password combination! Please "\
                                 "check the integrity of the database."
                                 % (self.__class__.__name__, ))
                raise SystemExit()
                return False
            elif len(res) < 1:
                logging.debug("%s: Credentials invalid for user: '%s'"
                                % (self.__class__.__name__, self._username, ))
                return False
        else:
            logging.warning("%s: This method can only be called from certain"\
                            "classes (SessionCtrl(, ...))"
                            % (self.__class__.__name__, ))
            return False


class BackupSourceCtrl(bs.model.models.Sources):
    """ * """
    _session = None
    _backup_source_id = None
    _source_name = None
    _source_path = None

    _backup_source_ass = None

    def __init__(self, session_gui, backup_source_id, source_name, source_path):
        self._session = session_gui
        self._backup_source_id = backup_source_id
        self._source_name = source_name
        self._source_path = source_path
        # if backup_source_id == None, this is a new source, add to database
        if not self._backup_source_id:
            res = self._add("user_id, source_name, source_path",
                            (self._session.user.id,
                            self._source_name,
                            self._source_path, ))
            self._backup_source_id = res.lastrowid

    def __repr__(self):
        return "Source #%d <%s>" % (self._backup_source_id, self.__class__.__name__, )

    @property
    def backup_source_id(self):
        return self._backup_source_id

    @property
    def source_name(self):
        return self._source_name

    @source_name.setter
    def source_name(self, source_name):
        # VALIDATE DATA
        # source_name
        if not re.match(bs.config.REGEX_PATTERN_NAME, source_name):
            logging.warning("%s: The source_name contains invalid "\
                            "characters. It needs to start  with an "\
                            "alphabetic and contain alphanumerical "\
                            "characters plus '\_\-\#' and space."
                            % (self.__class__.__name__, ))
            return False
        # change data in db
        self._update(
                     (("source_name", source_name), ),
                     (("id", "=", self._backup_source_id), )
                     )
        self._source_name = source_name
        # out
        return True

    @property
    def source_path(self):
        return self._source_path

    @source_path.setter
    def source_path(self, source_path):
        # VALIDATE DATA
        # source_path
        if not os.path.isdir(source_path):
            logging.warning("%s: The source-path is invalid. It needs to be "\
                            "a valid directory-path on the current system."
                            % (self.__class__.__name__, ))
            return False
        # change data in db
        self._update(
                     (("source_path", source_path), ),
                     (("id", "=", self._backup_source_id), )
                     )
        self._source_path = source_path
        # out
        return True

    @property
    def backup_source_ass(self):
        """ *
        Returns an associative array (dictionary) in the following format:
        {<set>:<filter>} or
        {<set>:<target>}
        """
        if not self._backup_source_ass:
            backup_source_ass = {}
            # Follows the "dumb" model: Sets don't know the associations, have to check the sets table here to get them
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            res = conn.execute("SELECT id, source_ass FROM sets WHERE user_id = ?", (self._session.user.id, )).fetchall()
            # run through set-results
            for dataset in res:
                set_id = dataset[0]
                source_ass_dict = json.loads(dataset[1])
                # get set object
                backup_set_obj = None
                for backup_set_obj_iter in self._session.backup_sets.sets:
                    if backup_set_obj_iter.backup_set_id == set_id:
                        backup_set_obj = backup_set_obj_iter
                # run through associations in set
                for backup_source_id in source_ass_dict:
                    if self.backup_source_id == int(backup_source_id):
                        # this can be either -1 for the set's target set or a natural number as a filter id
                        ass_id = source_ass_dict[backup_source_id]
                        # target set associated
                        if ass_id == -1:
                            backup_source_ass[backup_set_obj] = backup_set_obj.backup_targets
                        # filter associated
                        else:
                            # get filter object with id that was found
                            backup_filter_obj = None
                            for backup_filter_obj_iter in self._session.backup_filters.backup_filters:
                                if backup_filter_obj_iter.backup_filter_id == ass_id:
                                    backup_filter_obj = backup_filter_obj_iter
                            backup_source_ass[backup_set_obj] = backup_filter_obj
            self._backup_source_ass = backup_source_ass
        return self._backup_source_ass


class BackupSourcesCtrl(bs.model.models.Sources):
    """ * """
    _session = None
    _sources = None

    def __init__(self, session):
        """
        *
        """
        super(BackupSourcesCtrl, self).__init__()
        self._session = session

        self._sources = []

    def __repr__(self):
        return "Sources <%s>" % (self.__class__.__name__, )

    @property
    def sources(self):
        """ *
        Returns all source objects referenced in self._sources.
        """
        # sources list is empty, load from db
        if not len(self._sources):
            res = self._get("id, source_name, source_path",
                            (("user_id", "=", self._session.user.id, ), ))
            for data_set in res:
                source_id = data_set[0]
                source_name = data_set[1]
                source_path = data_set[2]
                new_source_obj = BackupSourceCtrl(self._session,
                                                  source_id,
                                                  source_name,
                                                  source_path)
                self._sources.append(new_source_obj)
        return self._sources

    # OVERLOADS
    @property
    def _add_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    @property
    def _get_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    @property
    def _remove_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def create_backup_source(self, source_name, source_path):
        """ *
        Creates a new backup-source.
        """
        # VALIDATE DATA
        # source_name
        if not re.search(bs.config.REGEX_PATTERN_NAME, source_name):
            logging.warning("%s: The name contains invalid characters. It "\
                            "needs to start  with an alphabetic and contain "\
                            "alphanumerical characters plus '\_\-\#' and "\
                            "space." % (self.__class__.__name__, ))
            return False
        # source_path
        if not os.path.isdir(source_path):
            logging.warning("%s: The source-path is invalid. It needs to be "\
                            "a valid directory-path on the current system."
                            % (self.__class__.__name__, ))
            return False
        logging.info("%s: Adding source: '%s' (%s)"
                        % (self.__class__.__name__, source_name, source_path,))
        # check that the path does not already exist for current user.
        res = self._get("id", (("user_id", "=", self._session.user.id, ),
                               ("source_path", "=", source_path, ), ))
        if len(res) > 0:
            logging.warning("%s: This source-path is already defined: %s"
                            % (self.__class__.__name__, source_path, ))
            return False
        # add object
        source_id = None
        new_source_obj = BackupSourceCtrl(self._session,
                                          source_id,
                                          source_name,
                                          source_path)
        self._sources.append(new_source_obj)
        logging.info("%s: Source successfully added: '%s' (%s)"
                        % (self.__class__.__name__, source_name, source_path))
        # out
        return True

    def delete_backup_source(self, source_obj):
        """ *
        Deletes an existing backup-source.
        """
        # VALIDATE DATA
        # source_obj
        if not isinstance(source_obj, BackupSourceCtrl):
            logging.warning("%s: The first argument needs to be a backup "\
                            "source object."
                            % (self.__class__.__name__, ))
            return False
        # remove data from database
        self._remove((("id", "=", source_obj._source_id, ), ))
        # delete obj
        self._sources.pop(self._sources.index(source_obj))
        # out
        logging.info("%s: Source has been successfully deleted: %s"
                     % (self.__class__.__name__, source_obj, ))
        return True


class BackupTargetCtrl(bs.model.models.Targets):
    """ * """
    _session = None
    _target_id = None
    _target_name = None
    _target_device_id = None

    def __init__(self, session_gui, target_id, target_name, target_device_id):
        self._session = session_gui
        self._target_id = target_id
        self._target_name = target_name
        self._target_device_id = target_device_id
        # if target_id == None, this is a new target, add to database
        if not self._target_id:
            res = self._add("user_id, target_name, target_device_id",
                            (self._session.user.id,
                            self._target_name,
                            self._target_device_id, ))
            self._target_id = res.lastrowid

    def __repr__(self):
        return "Target #%d <%s>" % (self._target_id, self.__class__.__name__, )

    @property
    def target_name(self):
        return self._target_name

    @target_name.setter
    def target_name(self, target_name):
        """ * """
        # VALIDATE DATA
        # target_name
        if not re.match(bs.config.REGEX_PATTERN_NAME, target_name):
            logging.warning("%s: The target_name contains invalid "\
                            "characters. It needs to start  with an "\
                            "alphabetic and contain alphanumerical "\
                            "characters plus '\_\-\#' and space."
                            % (self.__class__.__name__, ))
            return False
        # change data in db
        self._update(
                     (("target_name", target_name), ),
                     (("id", "=", self._target_id), )
                     )
        self._target_name = target_name
        # out
        return True

    @property
    def target_path(self):
        """ *
        Gets physical path that currently points to target.
        Scans all connected drives and looks for a backup folder with a
        metadata file with target's target_device_id.

        Returns physical path to target.
        """
        out = []
        for drive_root_path in bs.utils.get_drives((win32file.DRIVE_FIXED, )):
            target_config_file_path = os.path.join(drive_root_path,
                                                   bs.config.PROJECT_NAME,
                                                   "volume.json")
            if os.path.isfile(target_config_file_path):
                f = open(target_config_file_path, "r")
                data = f.read()
                target_device_id_drive = json.loads(data)[1]
                # if current target_device_id same as own device_id...
                if target_device_id_drive == self._target_device_id:
                    out.append(os.path.join(drive_root_path,
                                            bs.config.PROJECT_NAME))
                f.close()
        # out
        if len(out) > 1:
            logging.critical("%s: More than one drive carry the same ID. "\
                            "Please make sure there are no duplicates on the "\
                            "system: %s" % (self.__class__.__name__,
                                            out))
            raise SystemExit
        elif len(out) == 0:
            logging.critical("%s: The physical location of this target could "\
                             "not be found (target_device_id: %s)" % (self.__class__.__name__,
                                                                      self._target_device_id))
            raise SystemExit
        else:
            return out[0]


class BackupTargetsCtrl(bs.model.models.Targets):
    """ * """
    _session = None
    _targets = None

    def __init__(self, session_gui):
        super(BackupTargetsCtrl, self).__init__()
        self._session = session_gui

        self._targets = []

    def __repr__(self):
        return "Targets <%s>" % (self.__class__.__name__)

    @property
    def targets(self):
        """ *
        Returns all targets objects saved in self._targets.
        """
        # targets list is empty, load from db
        if len(self._targets) == 0:
            res = self._get("id, target_name, target_device_id",
                            (("user_id", "=", self._session.user.id, ), ))
            for data_set in res:
                target_id = data_set[0]
                target_name = data_set[1]
                target_device_id = data_set[2]
                new_target_obj = BackupTargetCtrl(self._session,
                                                  target_id,
                                                  target_name,
                                                  target_device_id)
                self._targets.append(new_target_obj)
        return self._targets

    # OVERLOADS
    @property
    def _add_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    @property
    def _get_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    @property
    def _remove_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def create_backup_target(self, target_name, target_path):
        """ *
        Creates a new backup-target.
        """
        # VERIFY DATA
        # target_name
        if not re.search(bs.config.REGEX_PATTERN_NAME, target_name):
            logging.warning("%s: The name contains invalid characters. It "\
                            "needs to start  with an alphabetic and contain "\
                            "alphanumerical characters plus '\_\-\#' and "\
                            "space." % (self.__class__.__name__, ))
            return False
        # target_path
        if not re.search("^[a-zA-Z]\:\\\\$", target_path):
            logging.warning("%s: This is not a valid target path. Only "\
                            "partition roots can be defined as targets."
                            % (self.__class__.__name__, ))
            return False
        # check if volume is already defined as target
        root_path = os.path.join(target_path,
                                 bs.config.PROJECT_NAME.capitalize())
        root_config_file_path = os.path.join(root_path, "volume.json")
        if not os.path.isdir(root_path) and\
            not os.path.isfile(root_config_file_path):
            # generate target_device_id
            # timestamp at high sub-second-precision as string appended by
            # random 16-bit integer as string, encoded as HEX-SHA512
            timestamp = str(int(time.time() * 1000000))
            random_num = str(random.randint(1000000000000000, 9999999999999999))
            timestamp_random_num = timestamp + random_num
            target_device_id = hashlib.sha512(timestamp_random_num.encode()).hexdigest()
            # add obj
            target_id = None
            new_target_obj = BackupTargetCtrl(self._session,
                                              target_id,
                                              target_name,
                                              target_device_id)
            self._targets.append(new_target_obj)
            # create BS root directory on volume
            try:
                # create root_folder
                os.mkdir(root_path)
                with open(root_config_file_path, "w") as f:
                    json.dump([target_name, target_device_id], f)
                logging.info("%s: Target has been successfully created: %s"
                             % (self.__class__.__name__,
                                target_path, ))
                return True
            except Exception as e:
                logging.warning(bs.messages.general.general_error(e)[0])
                return False
        else:
            logging.warning("%s: This volume is already defined as a "\
                             "target. Please try to importing it: %s"
                             % (self.__class__.__name__, target_path, ))
            return False

    def delete_backup_target(self, target_obj):
        """ *
        Deletes an existing backup-target.
        Does *not* delete any file-system data.
        """
        # VALIDATE DATA
        # target_obj
        if not isinstance(target_obj, BackupTargetCtrl):
            logging.warning("%s: The first argument needs to be a backup "\
                            "target object."
                            % (self.__class__.__name__, ))
            return False
        # delete from DB
        self._remove((("id", "=", target_obj._target_id, ), ))
        # remove obj
        self._targets.pop(self._targets.index(target_obj))
        # out
        logging.info("%s: Target has been successfully removed; file-system "\
                     "data has not been changed/removed: %s"
                     % (self.__class__.__name__,
                        target_obj, ))
        return True


class BackupFilterCtrl(bs.model.models.Filters):
    """ * """
    _session = None
    _backup_filter_id = None
    _backup_filter_pattern = None

    _backup_filter_ass = None

    def __init__(self, session_gui, backup_filter_id, backup_filter_pattern):
        self._session = session_gui
        self._backup_filter_id = backup_filter_id
        self._backup_filter_pattern = backup_filter_pattern
        # if flter_id == None, this is a new filter, add to database
        if not self._backup_filter_id:
            res = self._add("user_id, filter_pattern",
                            (self._session.user.id,
                             self._backup_filter_pattern))
            self._backup_filter_id = res.lastrowid

    def __repr__(self):
        return "Filter #%d <%s>" % (self._backup_filter_id, self.__class__.__name__, )

    @property
    def backup_filter_id(self):
        """ * """
        return self._backup_filter_id

    @property
    def backup_filter_pattern(self):
        return self._backup_filter_pattern

    @backup_filter_pattern.setter
    def backup_filter_pattern(self, backup_filter_pattern):
        """ * """
        # VALIDATE DATA
        # backup_filter_pattern
        if not re.match("$.*^", backup_filter_pattern):
            logging.warning("%s: The backup_filter_pattern contains invalid "\
                            "characters. It needs to start with an "\
                            "alphabetic and contain alphanumerical "\
                            "characters plus '\_\-\#' and space."
                            % (self.__class__.__name__, ))
            return False
        # change data in db
        self._update(
                     ("filter_pattern", backup_filter_pattern, ),
                     ("id", "=", self._backup_filter_id, ),
                     )
        self._backup_filter_pattern = backup_filter_pattern
        # out
        return True

    @property
    def backup_filter_ass(self):
        """ *
        Returns an associative array (dictionary) in the following format:
        {<set>:<filter>} or
        {<set>:<target>}
        """
        if not self._backup_filter_ass:
            backup_filter_ass = {}
            # Follows the "dumb" model: Sets don't know the associations, have to check the sets table here to get them
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            res = conn.execute("SELECT id, filter_ass FROM sets WHERE user_id = ?", (self._session.user.id, )).fetchall()
            # run through set-results
            for dataset in res:
                set_id = dataset[0]
                filter_ass_dict = json.loads(dataset[1])
                # get set object
                backup_set_obj = None
                for backup_set_obj_iter in self._session.backup_sets.sets:
                    if backup_set_obj_iter.backup_set_id == set_id:
                        backup_set_obj = backup_set_obj_iter
                # run through associations in set
                for backup_filter_id in filter_ass_dict:
                    if self.backup_filter_id == int(backup_filter_id):
                        # this can be either -1 for the set's target set or a natural number as a filter id
                        ass_id = filter_ass_dict[backup_filter_id]
                        # target set associated
                        if ass_id == -1:
                            backup_filter_ass[backup_set_obj] = backup_set_obj.backup_targets
                        # filter associated
                        else:
                            # get filter object with id that was found
                            backup_filter_obj = None
                            for backup_filter_obj_iter in self._session.backup_filters.backup_filters:
                                if backup_filter_obj_iter.backup_filter_id == ass_id:
                                    backup_filter_obj = backup_filter_obj_iter
                            backup_filter_ass[backup_set_obj] = backup_filter_obj
            self._backup_filter_ass = backup_filter_ass
        return self._backup_filter_ass


class BackupFiltersCtrl(bs.model.models.Filters):
    """ * """
    _session = None
    _backup_filters = None

    def __init__(self, session_gui):
        """ * """
        super(BackupFiltersCtrl, self).__init__()
        self._session = session_gui

        self._backup_filters = []

    def __repr__(self):
        return "Filters <%s>" % (self.__class__.__name__)

    @property
    def filters(self):
        """ *
        Returns all filter objects saved in self._backup_filters.
        """
        # filter list is empty, load from db
        if len(self._backup_filters) == 0:
            res = self._get("id, filter_pattern",
                            (("user_id", "=", self._session.user.id), ))
            for data_set in res:
                filter_id = data_set[0]
                filter_pattern = data_set[1]
                new_filter_obj = BackupFilterCtrl(self._session,
                                                  filter_id,
                                                  filter_pattern)
                self._backup_filters.append(new_filter_obj)
        return self._backup_filters

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    @property
    def backup_filters(self):
        """ * """
        return self._backup_filters

    def create_backup_filter(self, filter_pattern):
        """ *
        Creates a new backup-filter.
        """
        # VALIDATE DATA
        # filter
        if not re.match("$.*^", filter_pattern):
            logging.warning("%s: The filter_pattern contains invalid "\
                            "characters. It needs to start with an "\
                            "alphabetic and contain alphanumerical "\
                            "characters plus '\_\-\#' and space."
                            % (self.__class__.__name__, ))
            return False
        # validate filter data here once decided on format
        # add obj
        filter_id = None
        new_filter_obj = BackupFilterCtrl(self._session,
                                          filter_id,
                                          filter_pattern)
        self._backup_filters.append(new_filter_obj)
        # out
        return True

    def delete_backup_filter(self, filter_obj):
        """ *
        Deletes an existing backup-filter.
        """
        # VALIDATE DATA
        # filter_id
        if not isinstance(filter_obj, BackupFilterCtrl):
            logging.warning("%s: The first argument needs to be of type integer."
                            % (self.__class__.__name__, ))
            return False
        # delete from DB
        self._remove((("id", "=", filter_obj._filter_id, ), ))
        # remove obj
        self._backup_filters.pop(self._backup_filters.index(filter_obj))
        # out
        return True


class BackupSetCtrl(bs.model.models.Sets):
    """ * """
    _session = None
    _backup_set_id = None
    _set_uid = None
    _set_name = None
    _salt_dk = None
    _set_db_path = None
    _backup_sources = None
    _backup_filters = None
    _backup_targets = None
    _gui_data = None

    _backup_ctrls = None
    _is_authenticated = None
    _key_hash_32 = None

    def __init__(self, session, set_id, set_uid, set_name, salt_dk, \
                 set_db_path, source_objs, filter_objs, target_objs):
        self._session = session
        self._backup_set_id = set_id
        self._set_uid = set_uid
        self._set_name = set_name
        self._salt_dk = salt_dk
        self._set_db_path = set_db_path
        self._backup_sources = source_objs
        self._backup_filters = filter_objs
        self._backup_targets = target_objs

        # build backup_ctrls
        self._backup_ctrls = {}
        for backup_source in self._backup_sources:
            self._backup_ctrls[backup_source] = bs.ctrl.backup.BackupCtrl(self,
                                                                          backup_source)
        # if set_id == None, this is a new set, add to database
        if not self._backup_set_id:
            target_ids = []
            for target_obj in target_objs:
                target_ids.append(target_obj._target_id)
            target_ids_list = target_ids
            res = self._add("user_id, set_uid, set_name, salt_dk, set_db_path, sources, filters, targets",
                      (
                       self._session.user.id,
                       set_uid,
                       set_name,
                       salt_dk,
                       set_db_path,
                       json.dumps(target_ids_list)
                       )
                      )
            self._backup_set_id = res.lastrowid
            # create db file
            conn = sqlite3.connect(set_db_path)
            conn.close()

    def __repr__(self):
        return "Sets #%d id(%d) <%s>" % (self._backup_set_id,
                                        id(self),
                                        self.__class__.__name__, )

    @property
    def backup_set_id(self):
        return self._backup_set_id

    @property
    def set_uid(self):
        return self._set_uid

    @property
    def set_name(self):
        return self._set_name

    @set_name.setter
    def set_name(self, set_name):
        """ * """
        # VERIFY DATA
        # set name
        if not re.match(bs.config.REGEX_PATTERN_NAME, set_name):
            logging.warning("%s: The name contains invalid characters. It "\
                            "needs to start  with an alphabetic and contain "\
                            "alphanumerical characters plus '\_\-\#' and "\
                            "space." % (self.__class__.__name__, ))
            return False
        # set new name
        self._set_name = set_name
        # update db
        self._update(
                     (("set_name", set_name, ), ),
                     (("id", "=", self._backup_set_id, ), )
                     )

    @property
    def salt_dk(self):
        return self._salt_dk

    @property
    def set_db_path(self):
        if not os.path.isfile(self._set_db_path):
            self.set_db_path = self._set_db_path
        return self._set_db_path

    @set_db_path.setter
    def set_db_path(self, set_db_path):
        # validate existence of path
        if not os.path.isfile(self._set_db_path):
            set_db_path_new = ""
            while not os.path.isfile(set_db_path_new):
                set_db_path_new = input("The last used path ('%s') is "\
                                        "invalid; please enter the current "\
                                        "path of this set's database:"
                                        % (self._set_db_path, ))
            self._set_db_path = set_db_path_new
            # update db
            self._update(
                         (("set_db_path", set_db_path_new, ), ),
                         (("id", "=", self._backup_set_id, ), )
                         )
        return True

    @property
    def backup_sources(self):
        """ * """
        return self._backup_sources

    @property
    def backup_filters(self):
        """ * """
        return self._backup_filters

    @property
    def backup_targets(self):
        """ * """
        return self._backup_targets

    @backup_targets.setter
    def backup_targets(self, target_objs):
        """ * """
        # VALIDATE DATA
        # set_objs
        check = False
        if not isinstance(target_objs, (list, tuple, )):
            check = True
        else:
            for target_obj in target_objs:
                if not isinstance(target_obj, BackupTargetCtrl):
                    check = True
        if check:
            logging.warning("%s: The first argument needs to be a list or "\
                            "tuple of backup target objects."
                            % (self.__class__.__name__, ))
            return False
        # set targets
        self._targets = target_objs
        # update db
        target_ids_list = [x._target_id for x in target_objs]
        self._update((("targets", json.dumps(target_ids_list)), ),
                     (("id", "=", self._backup_set_id, ), ))

    @property
    def gui_data(self):
        """ *
        This associative array holds arbitrary gui-specific data such as
        node-coordinates and anything that might be added in the future.
        """
        if not self._gui_data:
            # get data from db
            res = self._get("gui_data",
                            (("id", "=", self.backup_set_id, ), ))
            gui_data = json.loads(res[0][0])
            self._gui_data = gui_data
        return self._gui_data

    @property
    def backup_ctrls(self):
        return self._backup_ctrls

    @property
    def is_authenticated(self):
        if self._is_authenticated:
            return True
        else:
            return False

    @property
    def key_hash_32(self):
        return self._key_hash_32

    def add_backup_source(self, backup_source):
        """ *
        Adds a backup-source to this backup-set.
        """
        # add backup_source as member to this set
        if backup_source not in self.backup_sources:
            self.backup_sources.append(backup_source)
        # add set association to backup_source
        if not self in backup_source.backup_source_ass.keys():
            backup_source.backup_source_ass[self] = None
        # add backup_ctrl for new source
        if backup_source not in self._backup_ctrls.keys():
            self._backup_ctrls[backup_source] = bs.ctrl.backup.BackupCtrl(self,
                                                                          backup_source)

    def add_backup_filter(self, backup_filter):
        """ *
        Adds a backup-filter to this backup-set.
        """
        # add backup_filter as member to this set
        if backup_filter not in self.backup_filters:
            self.backup_filters.append(backup_filter)
        # add set association to backup_filter
        if not self in backup_filter.backup_filter_ass.keys():
            backup_filter.backup_filter_ass[self] = None

    def remove_backup_source(self, backup_source):
        """ *
        Removes a backup-source from this backup-set.
        """
        backup_source_id = backup_source.source_id
        backup_sources_list_new = []
        # remove object from self.sources
        self._backup_sources.pop(self._backup_sources.index(backup_source))
        # compile new list for db
        for backup_source_in_current_set in [x.backup_source_id for x in self._backup_sources]:
            if not backup_source_in_current_set == backup_source_id:
                backup_sources_list_new.append(backup_source_in_current_set)
        # update db
        self._update((("sources", json.dumps(backup_sources_list_new), ), ), (("id", "=", self.backup_set_id, ), ))

    def save_to_db(self):
        """ *
        Explicitly saves specified fields to db that are only intermittendly
        modified in memory during runtime.
        """
        logging.debug("%s: Saving gui_data to db..." % (self.__class__.__name__, ))
        # gui_data
        self._update((("gui_data", json.dumps(self.gui_data)), ), (("id", "=", self.backup_set_id, ), ))
        # source_ass
        source_ass = {}
        for backup_source in self.backup_sources:
            associated_obj = backup_source.backup_source_ass[self]
            # if ass: filter
            if isinstance(associated_obj, BackupFilterCtrl):
                associated_obj_id = associated_obj.backup_filter_id
            # if ass: targets
            elif isinstance(associated_obj, list) and\
                isinstance(associated_obj[0], BackupTargetCtrl):
                associated_obj_id = -1
            # if ass: None
            elif not associated_obj:
                associated_obj_id = None
            source_ass[str(backup_source.backup_source_id)] = associated_obj_id
        self._update((("source_ass", json.dumps(source_ass)), ), (("id", "=", self.backup_set_id, ), ))
        # filter_ass
        filter_ass = {}
        for backup_filter in self.backup_filters:
            associated_obj = backup_filter.backup_filter_ass[self]
            # if ass: filter
            if isinstance(associated_obj, BackupFilterCtrl):
                associated_obj_id = associated_obj.backup_filter_id
            # if ass: targets
            elif isinstance(associated_obj, list) and\
                isinstance(associated_obj[0], BackupTargetCtrl):
                associated_obj_id = -1
            # if ass: None
            elif not associated_obj:
                associated_obj_id = None
            filter_ass[str(backup_filter.backup_filter_id)] = associated_obj_id
        self._update((("filter_ass", json.dumps(filter_ass)), ), (("id", "=", self.backup_set_id, ), ))
        logging.debug("%s: gui_data successfully saved to db." % (self.__class__.__name__, ))
        return True

    def authenticate(self, key_raw):
        """ *
        Authenticates user with backup_set.
        """
        # Calculate PBKDF2 ciphers
        key_hash_32 = Crypto.Protocol.KDF.PBKDF2(key_raw,
                                                 binascii.unhexlify(self.salt_dk[:128]),
                                                 dkLen=32,
                                                 count=64000)
        # compare hash of entered key against hash_64 in db/on set-obj
        dk_hex = binascii.hexlify(key_hash_32).decode("utf-8")
        if dk_hex == self.salt_dk[128:]:
            self._is_authenticated = True
            self._key_hash_32 = hashlib.sha512(key_raw.encode()).hexdigest()
        else:
            logging.warning("%s: The password is invalid." % (self.__class__.__name__, ))


class BackupSetsCtrl(bs.model.models.Sets):
    """ * """
    _session = None
    _sets = None

    def __init__(self, session):
        super(BackupSetsCtrl, self).__init__()
        self._session = session

        self._sets = []

    def __repr__(self):
        return "Sets <%s>" % (self.__class__.__name__)

    @property
    def sets(self):
        """ * """
        # sets list is empty, load from db
        if len(self._sets) == 0:
            res = self._get("id, set_uid, set_name, salt_dk, set_db_path, source_ass, filter_ass, targets",
                            (("user_id", "=", self._session.user.id, ), ))
            for data_set in res:
                set_id = data_set[0]
                set_uid = data_set[1]
                set_name = data_set[2]
                salt_dk = data_set[3]
                set_db_path = data_set[4]
                source_objs = []
                for source_id in json.loads(data_set[5]):
                    source_id = int(source_id)
                    for source_obj in self._session.backup_sources.sources:
                        if source_obj.backup_source_id == source_id:
                            source_objs.append(source_obj)
                filter_objs = []
                for filter_id in json.loads(data_set[6]):
                    filter_id = int(filter_id)
                    for filter_obj in self._session.backup_filters.filters:
                        if filter_obj.backup_filter_id == filter_id:
                            filter_objs.append(filter_obj)
                target_objs = []
                for target_obj in self._session.backup_targets.targets:
                    if target_obj._target_id in json.loads(data_set[7]):
                        target_objs.append(target_obj)

                new_set_obj = BackupSetCtrl(self._session,
                                            set_id,
                                            set_uid,
                                            set_name,
                                            salt_dk,
                                            set_db_path,
                                            source_objs,
                                            filter_objs,
                                            target_objs)
                self._sets.append(new_set_obj)
        return self._sets

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def create_backup_set(self, set_name, key_raw, set_db_path, source_objs, filter_objs, target_objs):
        """ *
        Creates a new (empty) backup-set.
        """
        # VALIDATE DATA
        # set_name
        if not re.match(bs.config.REGEX_PATTERN_NAME, set_name):
            logging.warning("%s: The name contains invalid characters. It "\
                            "needs to start  with an alphabetic and contain "\
                            "alphanumerical characters plus '\_\-\#' and "\
                            "space." % (self.__class__.__name__, ))
            return False
        check = False
        # key_raw
        if not re.match(bs.config.REGEX_PATTERN_KEY, key_raw):
            logging.warning("%s: The password contains invalid characters "\
                            "and/or is of invalid length."
                            % (self.__class__.__name__, ))
            return False
        else:
            salt_dk = hashlib.sha512(key_raw.encode()).hexdigest()
        # set_db_path
        check = False
        if not isinstance(set_db_path, str):
            check = True
        elif not os.path.isdir(os.path.dirname(set_db_path)):
            check = True
        elif not re.match(".*\.sqlite$", set_db_path):
            check = True
        if check:
            logging.warning("%s: The given path does not point to an existing"\
                            "location on this system or the filename is in "\
                            "an invalid format (extension <.sqlite> "\
                            "expected)."
                            % (self.__class__.__name__, ))
            return False
        # source_objs
        if not isinstance(source_objs, (list, tuple)):
            check = True
        else:
            for source_obj in source_objs:
                if not isinstance(source_obj, BackupSourceCtrl):
                    check = True
        # filter_objs
        if not isinstance(filter_objs, (list, tuple)):
            check = True
        else:
            for filter_obj in filter_objs:
                if not isinstance(filter_obj, BackupFilterCtrl):
                    check = True
        # target_objs
        if not isinstance(target_objs, (list, tuple)):
            check = True
        else:
            for target_obj in target_objs:
                if not isinstance(target_obj, BackupTargetCtrl):
                    check = True

        if check:
            logging.warning("%s: The second, thrid and fourth arguments need "\
                            "to be a list or tuple of backup "\
                            "source/filter/target object respectively."
                            % (self.__class__.__name__, ))
            return False
        # ADD OBJ
        set_id = None
        # set_uid
        set_uid = None
        check = False
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        while not check:
            # generate (new) set_uid
            timestamp = str(int(time.time() * 1000000))
            random_num = str(random.randint(1000000000000000, 9999999999999999))
            timestamp_random_num = timestamp + random_num
            set_uid = hashlib.md5(timestamp_random_num.encode()).hexdigest()
            # check if unique in db
            res = conn.execute("SELECT id FROM sets WHERE set_uid = ?",
                               (set_uid, )).fetchall()
            if len(res) == 0:
                check = True
                break
            time.sleep(0.005)
        conn.close()
        new_set_obj = BackupSetCtrl(self._session,
                                    set_id,
                                    set_uid,
                                    set_name,
                                    salt_dk,
                                    set_db_path,
                                    source_objs,
                                    filter_objs,
                                    target_objs)
        self._sets.append(new_set_obj)
        # out
        return True

    def delete_backup_set(self, backup_set):
        """ *
        Deletes an existing backup-set.
        """
        # VALIDATE DATA
        # backup_set
        if not isinstance(backup_set, BackupSetCtrl):
            logging.warning("%s: The first argument needs to be of "\
                            "type BackupSetCtrl."
                            % (self.__class__.__name__, ))
            return False
        backup_set_id = backup_set.backup_set_id
        # delete from DB
        self._remove((("id", "=", backup_set_id, ), ))
        # remove corresponding object from self._sets
        for set in self._sets:
            if set == backup_set:
                self._sets.pop(self._sets.index(set))
        # out
        return True
