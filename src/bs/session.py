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

""" * """

from PySide import QtGui
import bs.config
import bs.gui.window_main
import bs.messages
import bs.models
import hashlib
import json
import logging
import os
import random
import re
import sqlite3
import time
import win32file



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
            self._app = QtGui.QApplication("asdf")
            self._app.setWindowIcon(QtGui.QIcon("img/favicon.png"))
            self.add_gui()
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
            self._current_session = self._sessions[-1]
            logging.info("%s: Session successfully removed: %s"
                         % (self.__class__.__name__, session, ))
        else:
            logging.warning("%s: The session does not exist: %s"
                            % (self.__class__.__name__, session, ))

    def add_gui(self):
        """ *
        Adds a new UI instance to host a separate is_unlocked session.
        """
        session_gui = SessionGuiCtrl(self)
        self._guis.append(session_gui)
        return session_gui


class SessionGuiCtrl(object):
    """ *
    Container for a GUI session
    """
    _main_window = None
    _sessions = None
    _session = None

    def __init__(self, sessions):
        self._sessions = sessions
        self._main_window = bs.gui.window_main.WindowMain(self._sessions, self)

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
        if not isinstance(session, SessionCtrl):
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


class UserCtrl(bs.models.Users):
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


class BackupSourceCtrl(bs.models.Sources):
    """ * """
    _session = None
    _source_id = None
    _source_name = None
    _source_path = None

    def __init__(self, session_gui, source_id, source_name, source_path):
        self._session = session_gui
        self._source_id = source_id
        self._source_name = source_name
        self._source_path = source_path
        # if source_id == None, this is a new source, add to database
        if not self._source_id:
            res = self._add("user_id, source_name, source_path",
                            (self._session.user.id,
                            self._source_name,
                            self._source_path, ))
            self._source_id = res.lastrowid

    def __repr__(self):
        return "Source #%d <%s>" % (self._source_id, self.__class__.__name__, )

    @property
    def source_id(self):
        return self._source_id

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
                     (("id", "=", self._source_id), )
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
                     (("id", "=", self._source_id), )
                     )
        self._source_path = source_path
        # out
        return True


class BackupSourcesCtrl(bs.models.Sources):
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

    def add(self, source_name, source_path):
        """ *
        Adds a new source.
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

    def remove(self, source_obj):
        """ *
        Removes an existing source.
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


class BackupTargetCtrl(bs.models.Targets):
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
        else:
            return out[0]


class BackupTargetsCtrl(bs.models.Targets):
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

    def add(self, target_name, target_path):
        """ *
        Adds a new target.
        Returns the target_device_id.
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

    def remove(self, target_obj):
        """ *
        Removes an existing target.
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


class BackupFilterCtrl(bs.models.Filters):
    """ * """
    _session = None
    _filter_id = None
    _filter_pattern = None

    def __init__(self, session_gui, filter_id, filter_pattern):
        self._session = session_gui
        self._filter_id = filter_id
        self._filter_pattern = filter_pattern
        # if flter_id == None, this is a new filter, add to database
        if not self._filter_id:
            res = self._add("user_id, filter_pattern",
                            (self._session.user.id,
                             self._filter_pattern))
            self._filter_id = res.lastrowid

    def __repr__(self):
        return "Filter #%d <%s>" % (self._filter_id, self.__class__.__name__, )

    @property
    def filter_pattern(self):
        return self._filter_pattern

    @filter_pattern.setter
    def filter_pattern(self, filter_pattern):
        """ * """
        # VALIDATE DATA
        # filter_pattern
        if not re.match("$.*^", filter_pattern):
            logging.warning("%s: The filter_pattern contains invalid "\
                            "characters. It needs to start with an "\
                            "alphabetic and contain alphanumerical "\
                            "characters plus '\_\-\#' and space."
                            % (self.__class__.__name__, ))
            return False
        # change data in db
        self._update(
                     ("filter_pattern", filter_pattern, ),
                     ("id", "=", self._filter_id, ),
                     )
        self._filter_pattern = filter_pattern
        # out
        return True

class BackupFiltersCtrl(bs.models.Filters):
    """ * """
    _session = None
    _filters = None

    def __init__(self, session_gui):
        """ * """
        super(BackupFiltersCtrl, self).__init__()
        self._session = session_gui

        self._filters = []

    def __repr__(self):
        return "Filters <%s>" % (self.__class__.__name__)

    @property
    def filters(self):
        """ *
        Returns all filter objects saved in self._filters.
        """
        # filter list is empty, load from db
        if len(self._filters) == 0:
            res = self._get("id, filter_pattern",
                            (("user_id", "=", self._session.user.id), ))
            for data_set in res:
                filter_id = data_set[0]
                filter_pattern = data_set[1]
                new_filter_obj = BackupFilterCtrl(self._session,
                                                  filter_id,
                                                  filter_pattern)
                self._filters.append(new_filter_obj)
        return self._filters

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

    def add(self, filter_pattern):
        """ *
        Adds a new filter.
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
        self._filters.append(new_filter_obj)
        # out
        return True

    def remove(self, filter_obj):
        """ *
        Removes an existing filter.
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
        self._filters.pop(self._filters.index(filter_obj))
        # out
        return True


class BackupSetCtrl(bs.models.Sets):
    """ * """
    _session = None
    _set_id = None
    _set_uid = None
    _set_name = None
    _key_hash_64 = None
    _set_db_path = None
    _sources = None
    _filters = None
    _targets = None

    def __init__(self, session, set_id, set_uid, set_name, key_hash_64, \
                 set_db_path, source_objs, filter_objs, target_objs):
        self._session = session
        self._set_id = set_id
        self._set_uid = set_uid
        self._set_name = set_name
        self._key_hash_64 = key_hash_64
        self._set_db_path = set_db_path
        self._sources = source_objs
        self._filters = filter_objs
        self._targets = target_objs

        # if set_id == None, this is a new set, add to database
        if not self._set_id:
            source_ids = []
            for source_obj in source_objs:
                source_ids.append(source_obj._source_id)
            source_ids_list = source_ids
            filter_ids = []
            for filter_obj in filter_objs:
                filter_ids.append(filter_obj._filter_id)
            filter_ids_list = filter_ids
            target_ids = []
            for target_obj in target_objs:
                target_ids.append(target_obj._target_id)
            target_ids_list = target_ids
            res = self._add("user_id, set_uid, set_name, key_hash_64, set_db_path, sources, filters, targets",
                      (
                       self._session.user.id,
                       set_uid,
                       set_name,
                       key_hash_64,
                       set_db_path,
                       json.dumps(source_ids_list),
                       json.dumps(filter_ids_list),
                       json.dumps(target_ids_list)
                       )
                      )
            self._set_id = res.lastrowid
            # create db file
            conn = sqlite3.connect(set_db_path)
            conn.close()

    def __repr__(self):
        return "Sets #%d id(%d) <%s>" % (self._set_id,
                                        id(self),
                                        self.__class__.__name__, )

    @property
    def set_id(self):
        return self._set_id

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
                     (("id", "=", self._set_id, ), )
                     )

    @property
    def key_hash_64(self):
        return self._key_hash_64

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
                         (("id", "=", self._set_id, ), )
                         )
        return True

    @property
    def sources(self):
        return self._sources

    @sources.setter
    def sources(self, source_objs):
        """ * """
        # VALIDATE DATA
        # set_objs
        check = False
        if not isinstance(source_objs, (list, tuple, )):
            check = True
        else:
            for source_obj in source_objs:
                if not isinstance(source_obj, BackupSourceCtrl):
                    check = True
        if check:
            logging.warning("%s: The first argument needs to be a list or "\
                            "tuple of backup source objects."
                            % (self.__class__.__name__, ))
            return False
        # set sources
        self._sources = source_objs
        # update db
        source_ids_list = [x._source_id for x in source_objs]
        self._update((("sources", json.dumps(source_ids_list)), ),
                     (("id", "=", self._set_id, ), ))

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, filter_objs):
        """ * """
        # VALIDATE DATA
        # set_objs
        check = False
        if not isinstance(filter_objs, (list, tuple, )):
            check = True
        else:
            for filter_obj in filter_objs:
                if not isinstance(filter_obj, BackupFilterCtrl):
                    check = True
        if check:
            logging.warning("%s: The first argument needs to be a list or "\
                            "tuple of backup filter objects."
                            % (self.__class__.__name__, ))
            return False
        # set filters
        self._filters = filter_objs
        # update db
        filter_ids_list = [x._filter_id for x in filter_objs]
        self._update((("filters", json.dumps(filter_ids_list)), ),
                     (("id", "=", self._set_id, ), ))

    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self, target_objs):
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
                     (("id", "=", self._set_id, ), ))


class BackupSetsCtrl(bs.models.Sets):
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
            res = self._get("id, set_uid, set_name, key_hash_64, set_db_path, sources, filters, targets",
                            (("user_id", "=", self._session.user.id, ), ))
            for data_set in res:
                set_id = data_set[0]
                set_uid = data_set[1]
                set_name = data_set[2]
                key_hash_64 = data_set[3]
                set_db_path = data_set[4]
                source_objs = []
                for source_obj in self._session.backup_sources.sources:
                    if source_obj._source_id in json.loads(data_set[5]):
                        source_objs.append(source_obj)
                filter_objs = []
                for filter_obj in self._session.backup_filters.filters:
                    if filter_obj._filter_id in json.loads(data_set[6]):
                        filter_objs.append(filter_obj)
                target_objs = []
                for target_obj in self._session.backup_targets.targets:
                    if target_obj._target_id in json.loads(data_set[7]):
                        target_objs.append(target_obj)

                new_set_obj = BackupSetCtrl(self._session,
                                            set_id,
                                            set_uid,
                                            set_name,
                                            key_hash_64,
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

    def add(self, set_name, key_raw, set_db_path, source_objs, filter_objs, target_objs):
        """ *
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
            key_hash_64 = hashlib.sha512(key_raw.encode()).hexdigest()
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
                                    key_hash_64,
                                    set_db_path,
                                    source_objs,
                                    filter_objs,
                                    target_objs)
        self._sets.append(new_set_obj)
        # out
        return True

    def remove(self, set_id):
        """ * """
        # VALIDATE DATA
        # set_id
        if not type(set_id) is int:
            logging.warning("%s: The first argument needs to be of type integer."
                            % (self.__class__.__name__, ))
            return False
        # delete from DB
        self._remove((("id", "=", set_id, ), ))
        # remove corresponding object from self._sets
        for set in self._sets:
            if set.set_id == set_id:
                self._sets.pop(self._sets.index(set))
        # out
        return True
