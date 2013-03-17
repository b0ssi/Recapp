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

from utils import BSString
import _db
import config
import hashlib
import logging
import messages.database
import models
import os
import sqlite3


class UserModel(object):
    _id = None
    _username = ""
    _password = ""
    _configdb_path = config.CONFIGDB_PATH
    _parent = None

    def __init__(self, parent):
        super(UserModel, self).__init__()

        self._parent = parent

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._username

    @property
    def is_logged_in(self):
        try:
            conn = sqlite3.connect(self._configdb_path)
            res = conn.execute("SELECT `username`, `password` FROM `users` "\
                               "WHERE `username`=?", \
                               (self._username,)).fetchone()
            if res is not None:
                username = res[0]
                password = res[1]

                if self._password == password:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            logging.critical(messages.database.access_denied(self._configdb_path, e)[0])
            raise SystemExit(messages.database.access_denied(self._configdb_path, e)[1])

    def log_in(self, username, password):
        if self.is_logged_in is False:
            logging.info("Authenticating user '%s'..." % (username,))
            # Authenticate user
            password_hash = hashlib.sha512()
            password_hash.update(password.encode())
            password_hash = password_hash.hexdigest()

            conn = sqlite3.connect(self._configdb_path)
            res = conn.execute("SELECT * FROM `users` "\
                                    "WHERE `username`=? AND `password`=?", \
                                    (username, password_hash)).fetchone()
            if res is None:
                logging.error("Authentication unsuccessful. Please try again.")
                return False
            else:
                self._username = username
                self._id = res[0]
                self._password = res[2]
                logging.info("Authentication successful, user '%s' logged-in."\
                             % (username,))
                return True
        else:
            logging.info("User '%s' is already logged-in." % self._username)

    def log_out(self):
        logging.info("Attempting to log-out user '%s'." % self._username)
        if self.is_logged_in is True:
            self._password = ""
            logging.info("User '%s' successfully logged out." % self._username)
            return True
        else:
            logging.info("User '%s' was already logged-out." % self._username)
            return False

    def add(self):
        logging.info("Attempting to add user-data for user '%s' to database "\
                     "..." % self._username)
        if self.is_logged_in is True:
            try:
                conn = sqlite3.connect(self._configdb_path)
                conn.execute("UPDATE `users` SET `username`=?, `password`=? "\
                             "WHERE `username`=?",
                             (self._username, self._password, self._username)\
                             )
                conn.commit()
                conn.close()
                logging.info("User-data for user '%s' successfully saved to "\
                             "database." % self._username)
                return True
            except Exception as e:
                logging.critical(messages.database.access_denied(self._configdb_path, e)[0])
                raise SystemExit(messages.database.access_denied(self._configdb_path, e)[1])
        else:
            logging.warning("User '%s' is not logged in, aborting." \
                            % (self._username,))
            return False

    def __repr__(self):
        return(str((self._id, self._username)))


class Sources(object):
    _configdb_path = config.CONFIGDB_PATH
    _parent = None
    _backup_sources = []
    _name = BSString()

    def __init__(self, parent, name):
        super(Sources, self).__init__()

        self._parent = parent
        self._name.__unicode__ = name

    def add(self, string_to_add):
        logging.info("Adding %s '%s' for user '%s'..." \
                     % (self._name.singularize().lower(), string_to_add, self._parent.user.name))
        if self._parent.user.is_logged_in:
            # check if string_to_add already exists for user in db
            if not string_to_add in [z[2] for z in self._backup_sources]:
                self._backup_sources.append([None, self._parent.user.id, string_to_add])
                logging.info("%s '%s' for user '%s' successfully added." \
                             % (self._name.singularize().capitalize(), string_to_add, self._parent.user.name))
            else:
                logging.warning("The %s '%s' already exists for user "\
                                "'%s', aborting." \
                                % (self._name.singularize().lower(), string_to_add, self._parent.user.name))
        else:
            logging.warning("User '%s' is not logged in, aborting." \
                            % (self._parent.user.name,))
            return False

    def remove(self, string_to_add):
        logging.info("Removing %s '%s' for user '%s'..." \
                     % (self._name.singularize().lower(), string_to_add, self._parent.user.name))
        if self._parent.user.is_logged_in:
            # only removing if it actually exists in self._backup_sources
            for dataset in self._backup_sources:
                if dataset[1] == self._parent.user.id and \
                    dataset[2] == string_to_add:

                    index = self._backup_sources.index(dataset)
                    self._backup_sources.pop(index)
                    logging.info("%s '%s' for user '%s' successfully removed." \
                                 % (self._name.singularize().capitalize(), string_to_add, self._parent.user.name))
                else:
                    logging.warning("The %s '%s' does not exists for user "\
                                    "'%s', aborting." \
                                    % (self._name.singularize().lower(), string_to_add, self._parent.user.name))
        else:
            logging.warning("User '%s' is not logged in, aborting." \
                            % (self._parent.user.name,))
            return False

    def get(self):
        logging.info("Loading %s for user '%s' from database..." \
                     % (self._name.pluralize().lower(), self._parent.user.name,))
        if self._parent.user.is_logged_in:
            try:
                conn = sqlite3.connect(self._configdb_path)
                res = conn.execute("SELECT * FROM `"+self._name.pluralize().lower()+"` "\
                                       "WHERE `userId`=?", \
                                       (self._parent.user.id,)).fetchall()
                conn.close()
                if len(res) > 0:
                    self._backup_sources = res
                    logging.info("%s for user '%s' successfully loaded "\
                                 "from database." % (self._name.pluralize().capitalize(), self._parent.user.name,))
                else:
                    logging.info("No %s for user '%s' found in database."\
                                 % (self._name.pluralize(), self._parent.user.name,))
            except Exception as e:
                raise Exception(e)
#                logging.critical(messages.database.access_denied(self._configdb_path, e)[0])
#                raise SystemExit(messages.database.access_denied(self._configdb_path, e)[1])
        else:
            logging.warning("User '%s' is not logged in, aborting." \
                            % (self._parent.user.name,))
            return False

    def add(self):
        logging.info("Saving %s for user '%s' to database..." \
                     % (self._name.pluralize(), self._parent.user.name,))
        if self._parent.user.is_logged_in:
            try:
                conn = sqlite3.connect(self._configdb_path)
                # add/update current datasets in object
                for dataset in self._backup_sources:
                    table_id = dataset[0]
                    user_id = dataset[1]
                    string_0 = dataset[2]
                    conn.execute("INSERT OR REPLACE INTO `"+self._name.pluralize().lower()+"` "\
                                 "(`id`, `userId`, `sourcePath`) " \
                                 "VALUES ("\
                                    "(select id from "+self._name.pluralize().lower()+" where userId = ? and sourcePath = ?), "\
                                    "?, "\
                                    "?)",
                                 (
                                  user_id,
                                  string_0,
                                  user_id,
                                  string_0
                                  )
                                 )
                # remove those datasets from db that don't exist on obj anymore
                for dataset in conn.execute("SELECT * FROM `"+self._name.pluralize().lower()+"` "\
                                            "WHERE `userId` = ?",
                                            (self._parent.user.id,)).fetchall():
                    if not (dataset[1], dataset[2]) in [(x[1], x[2]) for x in self._backup_sources]:
                        table_id = dataset[0]
                        conn.execute("DELETE FROM `"+self._name.pluralize().lower()+"` "\
                                     "WHERE `id` = ?", (table_id,))
                # update newly added datasets from db (to obtain id)
                for dataset in self._backup_sources:
                    if dataset[0] == None:
                        user_id = dataset[1]
                        string_0 = dataset[2]
                        res = conn.execute("SELECT `id` FROM `"+self._name.pluralize().lower()+"` "\
                                           "WHERE `userId` = ? AND `sourcePath` = ?",
                                           (user_id, string_0)).fetchall()
                        # remove old dataset with id=None
                        self._backup_sources.pop(self._backup_sources.index(dataset))
                        # add new dataset with id just aquired from db
                        self._backup_sources.append((res[0], user_id, string_0))
                conn.commit()
                conn.close()
                logging.info("%s for user '%s' successfully saved "\
                                 "to database." % (self._name.pluralize().capitalize(), self._parent.user.name,))
            except Exception as e:
                logging.critical(messages.database.access_denied(self._configdb_path, e)[0])
                raise SystemExit(messages.database.access_denied(self._configdb_path, e)[1])
        else:
            logging.warning("User '%s' is not logged in, aborting." \
                            % (self._parent.user.name,))
            return False


## NEW DESIGN 2013-03-17 ######################################################


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

    def __repr__(self):
        return(str((self._user,
                    self._backup_sources,
                    self._backup_targets,
                    self._backup_filters,
                    self._backup_sets))
               )


class UserModelNew(models.Users):
    _id = -1
    _is_logged_in = False
    _username = ""

    def __init__(self):
        super(UserModelNew, self).__init__()
        # create default user
        if len(self.get("*")) == 0:
            self.add("username, password",
                      [['1', '4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851"\
                      "f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f"\
                      "9bd058a12a280433ed6fa46510a']])
            self.add("username, password",
                      [['2', '40b244112641dd78dd4f93b6c9190dd46e0099194d5a442"\
                      "57b7efad6ef9ff4683da1eda0244448cb343aa688f5d3efd7314da"\
                      "fe580ac0bcbf115aeca9e8dc114']])

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
                logging.critical("More than one user exists with the same "\
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


class BackupSourcesModelNew(models.Sources):
    def __init__(self):
        super(BackupSourcesModelNew, self).__init__()


class BackupTargetsModelNew(models.Targets):
    def __init__(self):
        super(BackupTargetsModelNew, self).__init__()


class BackupFiltersModelNew(models.Filters):
    def __init__(self):
        super(BackupFiltersModelNew, self).__init__()


class BackupSetsModelNew(models.Sources):
    def __init__(self):
        super(BackupSetsModelNew, self).__init__()


# PREP
# sync db if necessary
sync_db = _db.SyncDb()
sync_db.sync()

# create a sessions host
SESSIONS = SessionsModel()
# log-in
SESSIONS.current_session.user.log_in("2", "2")
SESSIONS.current_session.backup_sources.add("user_id, source_path",
                                             ((SESSIONS.current_session.user.id,
                                               os.path.realpath("Z:/x")), ))
SESSIONS.current_session.backup_sources.remove((("user_id", "=", 2, ), ))
