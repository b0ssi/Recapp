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

import bs.config
import bs.messages
import bs.models
import hashlib
import json
import logging
import os
import random
import re
import time


class SessionsModel(object):
    """
    Stores and manages sessions for all active users.
    """
    _sessions = []
    _current_session = None

    def __init__(self):
        super(SessionsModel, self).__init__()
        # _add initial session
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
                            "the 'SessionModel()' class."
                            % (self.__class__.__name__))
            return False

    def add_session(self):
        """
        Adds a new session including an empty set for the user, sources,
        targets, filters, sets, etc..
        """
        logging.info("%s: Adding session to sessions..."
                     % (self.__class__.__name__, ))
        # create new session
        new_session = SessionModel()
        # _add new session to self._sessions
        self._sessions.append(new_session)
        self.current_session = new_session
        logging.info("%s: Session successfully added."
                     % (self.__class__.__name__, ))
        return new_session

    def remove_session(self, session):
        """
        *
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

        self._user = UserModel(self)
        self._backup_sources = BackupSourcesModel(self)
        self._backup_targets = BackupTargetsModel(self)
        self._backup_filters = BackupFiltersModel(self)
        self._backup_sets = BackupSetsModel(self)

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


class UserModel(bs.models.Users):
    """
    *
    Represents an active user.
    """
    _id = -1
    _is_logged_in = False
    _username = ""
    _session = None

    def __init__(self, session):
        """
        *
        """
        super(UserModel, self).__init__()
        self._session = session
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
    def is_logged_in(self):
        return self._is_logged_in

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

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
            res = self._get("id", (("username", "=", username),
                                  ("password", "=", password_hash.hexdigest(), ), ),
                           no_auth_required=True
                           )
            if len(res) == 1:
                self._id = res[0][0]
                self._username = username
                logging.info("%s: User '%s' successfully logged in."
                             % (self.__class__.__name__, self._username, ))
                self._is_logged_in = True
                return True
            elif len(res) > 1:
                logging.critical("%s: More than one user exist with the same "\
                                 "username/password combination! Please "\
                                 "check the integrity of the database."
                                 % (self.__class__.__name__, ))
                raise SystemExit()
                return False
            elif len(res) < 1:
                logging.warning("%s: Username or password is invalid, please "\
                                "try again."
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


class BackupSourcesModel(bs.models.Sources):
    """
    *
    """
    _session = None

    def __init__(self, session):
        """
        *
        """
        super(BackupSourcesModel, self).__init__()
        self._session = session

    def __repr__(self):
        return "Sources <%s>" % (self.__class__.__name__, )

    @property
    def sources(self):
        """
        *
        Returns all saved sources for current user as a list of full dataset
        tuples straight from the database.
        """
        return self._get("*", (("user_id", "=", self._session.user.id, ), ))

    @sources.setter
    def sources(self):
        return False

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def add(self, source_name, source_path):
        """
        *
        Adds a new source.
        Returns the source_id.
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
        # add data to database
        self._add("user_id, source_name, source_path",
                  ((self._session.user.id, source_name, source_path, ), ))
        logging.info("%s: Source successfully added: '%s' (%s)"
                        % (self.__class__.__name__, source_name, source_path))
        # out
        return True

    def remove(self, table_id):
        """
        *
        Removes an existing source.
        Returns the source_id.
        """
        # VALIDATE DATA
        if not isinstance(table_id, int):
            logging.warning("%s: Argument 1 needs to be an integer."
                            % (self.__class__.__name__, ))
            return False
        # check that dataset actually exists
        res = self._get("*", (("id", "=", table_id, ), ("user_id", "=",
                                                  self._session.user.id, ), ))
        if len(res) == 0:
            logging.warning("%s: A source with this ID does not exist for "\
                            "user '%s' (id: %s)." % (self.__class__.__name__,
                                            self._session.user.name,
                                            self._session.user.id, ))
            return False
        elif len(res) > 1:
            logging.warning("%s: There is more than one dataset with ID '%s' "\
                            "and user_id '%s'. Check the database for "\
                            "integrity." % (self.__class__.__name__,
                                            self._session.user.id))
            return False
        # remove data from database
        self._remove((("id", "=", table_id, ), ("user_id", "=",
                                          self._session.user.id, ), ))
        # out
        return True


class BackupTargetsModel(bs.models.Targets):
    """
    *
    """
    _session = None

    def __init__(self, session):
        """
        *
        """
        super(BackupTargetsModel, self).__init__()
        self._session = session

    def __repr__(self):
        return "Targets <%s>" % (self.__class__.__name__)

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def add(self, target_name, target_path):
        """
        *
        Adds a target to the list of targets.
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
        if not os.path.isdir(root_path):
            # generate target_id
            # timestamp at high sub-second-precision as string appended by random
            # 16-bit integer as string, encoded as HEX-SHA512
            timestamp = str(int(time.time() * 1000000))
            random_num = str(random.randint(1000000000000000, 9999999999999999))
            timestamp_random_num = timestamp + random_num
            target_id = hashlib.sha512(timestamp_random_num.encode()).hexdigest()
            # add to database
            self._add("user_id, target_name, target_id",
                      ((self._session.user.id, target_name, target_id,),))
            # create BS root directory on volume
            try:
                # create root_folder
                os.mkdir(root_path)
                with open(root_config_file_path, "w") as f:
                    json.dump([target_name, target_id], f)
                return True
            except Exception as e:
                logging.warning(bs.messages.general.general_error(e)[0])
                return False
        else:
            logging.warning("%s: This volume is already defined as a "\
                             "target: %s"
                             % (self.__class__.__name__, target_path, ))
            return False


class BackupFiltersModel(bs.models.Filters):
    """
    *
    """
    _session = None

    def __init__(self, session):
        """
        *
        """
        super(BackupFiltersModel, self).__init__()
        self._session = session

    def __repr__(self):
        return "Filters <%s>" % (self.__class__.__name__)

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS


class BackupSetsModel(bs.models.Sets):
    """
    *
    """
    _session = None

    def __init__(self, session):
        """
        *
        """
        super(BackupSetsModel, self).__init__()
        self._session = session

    def __repr__(self):
        return "Sets <%s>" % (self.__class__.__name__)

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session.user._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def add(self, set_name, sources, filters, targets):
        """
        *
        """
        # VALIDATE DATA
        # set_name
        if not re.search(bs.config.REGEX_PATTERN_NAME, set_name):
            logging.warning("%s: The name contains invalid characters. It "\
                            "needs to start  with an alphabetic and contain "\
                            "alphanumerical characters plus '\_\-\#' and "\
                            "space." % (self.__class__.__name__, ))
            return False
        # sources, filters, targets
        for candidate in (sources, filters, targets):
            check = True
            if not type(candidate) in (list, tuple, ):
                check = False
            for item in candidate:
                if not type(item) is int:
                    check = False
            if not check:
                logging.warning("%s: The second, third and fourth argument must "\
                                "be a list or tuple of item-ids (integers)."
                                % (self.__class__.__name__, ))
                return False
        # Check that the set with set_name doesn't already exist for current user.
        res = self._get("id", (("set_name", "=", set_name, ), ("user_id", "=", self._session.user.id, ), ))

        if len(res) > 0:
            logging.warning("%s: A set with this name already exists for this user: '%s'"
                            % (self.__class__.__name__,
                               set_name, ))
            return False
        # add set to database
        self._add("user_id, set_name, sources, filters, targets", ((self._session.user.id,
                                                                    set_name,
                                                                    json.dumps(sources),
                                                                    json.dumps(filters),
                                                                    json.dumps(targets), ),
                                                                   ))
        # out
        return True

    def remove(self, set_id):
        """
        *
        """
        # VALIDATE DATA
        # set_id
        if not type(set_id) is int:
            logging.warning("%s: The first argument needs to be of type integer."
                            % (self.__class__.__name__, ))
            return False
        # delete from DB
        self._remove((("id", "=", set_id, ), ))
        # out
        return True
