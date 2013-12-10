# -*- coding: utf-8 -*-
###############################################################################
##    bs.ctrl.backup                                                         ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Apr 12, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################
""" ..

Hosts all backup- and restore-logics and procedures.
"""

from PySide import QtCore

import binascii
import bs.utils
import Crypto.Cipher.AES
import Crypto.Random
import Crypto.Util.Counter
import getpass
import hashlib
import logging
import os
import re
import sqlite3
import tempfile
import time
import zipfile
import zlib


class BackupUpdateEvent(object):
    """ 

    :param int byte_count_total:
    :param int byte_count_current:
    :param int byte_count_delta:
    :param int file_count_total:
    :param int file_count_current:
    :param bool file_num_increment:
    :param str file_path:
    :param bool simulate:

    This is an event object to send along :class:`~bs.ctrl.backup.BackupCtrl` \
    signals e.g.
    """
    _byte_count_total = None
    _byte_count_current = None
    _byte_count_delta = None
    _file_count_total = None
    _file_count_current = None
    _file_path = None
    _simulate = None
    _file_num_increment = None

    def __init__(self, **kwargs):
        """ ..

        """
        super(BackupUpdateEvent, self).__init__()

        self._byte_count_total = kwargs.get("byte_count_total", None)
        self._byte_count_current = kwargs.get("byte_count_current", None)
        self._byte_count_delta = kwargs.get("byte_count_delta", None)
        self._file_count_total = kwargs.get("file_count_total", None)
        self._file_count_current = kwargs.get("file_count_current", None)
        self._file_num_increment = kwargs.get("file_num_increment", None)
        self._file_path = kwargs.get("file_path", None)
        self._simulate = kwargs.get("simulate", None)

    @property
    def byte_count_current(self):
        """ ..

        :type: *int*
        """
        return self._byte_count_current

    @property
    def byte_count_delta(self):
        """ ..

        :type: *int*
        """
        return self._byte_count_delta

    @property
    def byte_count_total(self):
        """ ..

        :type: *int*
        """
        return self._byte_count_total

    @property
    def file_count_current(self):
        """ ..

        :type: *int*
        """
        return self._file_count_current

    @property
    def file_count_total(self):
        """ ..

        :type: *int*
        """
        return self._file_count_total

    @property
    def file_num_increment(self):
        """ ..

        :type: *bool*

        Whether or not this event notifies about an increment in file-count \
        (by 1).
        """
        return self._file_num_increment

    @property
    def file_path(self):
        """ ..

        :type: *str*

        If provided together with :attr:`file_num_increment`, it provides the \
        path of the last processed file this event notifies about.
        """
        return self._file_path

    @property
    def simulate(self):
        """ ..

        :type: *bool*

        Whether or not backup-ctrl is in simulation mode.
        """
        return self._simulate


class BackupCtrl(QtCore.QObject):
    """ ..

    :param bs.ctrl.session.BackupSetCtrl backup_set: The *backup-set* to \
    handle.
    :param bs.ctrl.session.BackupSourceCtrl backukp_source: The \
    *backup-source* to handle.
    :ivar enum MODE_BACKUP: Enum used to indicate that backup-controller is \
    in *backup* mode.
    :ivar enum MODE_SIMULATE: Enum used to indicate that backup-controller is \
    in *backup* mode.

    Manages and runs a backup-job.
    """
    _backup_set = None
    _backup_source = None

    _byte_count_current = None
    _byte_count_total = None
    _file_count_current = None
    _file_count_total = None
    _finished_signal = QtCore.Signal(BackupUpdateEvent)
    _mode = None
    _mutex = None
    _request_exit = None
    _targets = None
    _thread = None
    _tmp_dir = None
    _updated_signal = QtCore.Signal(BackupUpdateEvent)
    _worker = None

    MODE_BACKUP = 0
    MODE_SIMULATE = 1

    def __init__(self, backup_set, backup_source):
        super(BackupCtrl, self).__init__()

        self._backup_set = backup_set
        self._backup_source = backup_source

        self._mutex = QtCore.QMutex()
        self._targets = backup_set.backup_targets
        self._tmp_dir = tempfile.TemporaryDirectory()
        self._request_exit = False

    @property
    def byte_count_current(self):
        """ ..

        :type: *int*
        """
        return self._byte_count_current

    @property
    def byte_count_total(self):
        """ ..

        :type: *int*
        """
        return self._byte_count_total

    @property
    def file_count_current(self):
        """ ..

        :type: *int*
        """
        return self._file_count_current

    @property
    def file_count_total(self):
        """ ..

        :type: *int*
        """
        return self._file_count_total

    @property
    def finished_signal(self):
        """ ..

        :type: :class:`~bs.utils.Signal`

        This signal emits when the pre-process- or backup-execution finishes.
        """
        return self._finished_signal

    @property
    def updated_signal(self):
        """ ..

        :type: :class:`~bs.utils.Signal`

        This signal emits when the backup-process updates (this usually \
        happens for each file that is processed). It emits with \
        :class:`~bs.ctrl.backup.BackupUpdateEvent` as event-parameter.
        """
        return self._updated_signal

    def _execute(self):
        """ ..

        :rtype: *bool*

        Main backup-exec: Runs through a set of sources, applying filters,
        determining the state of an entity and backing up those that change \
        has been detected in.
        Will log error messages for entities of unknown state.
        Depending which method calls this method (:meth:`backup_exec` or \
        :meth:`pre_process_data`), this method runs in simulation mode, where \
        quantities of entities and capacity are only evaluated and, like in \
        unrestricted mode, sent out via this class's signals.
        """
        # check if set is encrypted and request authorization status if so.
        # If not authorized, abort.
        if self._backup_set.salt_dk:
            if not self._backup_set.is_authenticated:
                logging.warning("%s: The backup-set seems to be encrypted "\
                                "but has not been unlocked yet."
                                % (self.__class__.__name__, ))
                return False
        # update database
        conn = sqlite3.connect(self._backup_set.set_db_path)
        if self._mode == self.MODE_BACKUP:
            new_column_name = self._update_db(conn)
        backup_source_path = self._backup_source.source_path
        # reset counts
        self._byte_count_current = 0
        self._file_count_current = 0
        if self._mode == self.MODE_SIMULATE:
            self._byte_count_total = 0
            self._file_count_total = 0
        # iterate through file-system
        for folder_path, folders, files in os.walk(backup_source_path):
            for file in files:
                # exit thread prematurely on request
                if self._request_exit:
                    self._byte_count_current = None
                    self._byte_count_total = None
                    self._file_count_current = None
                    self._file_count_total = None
                    self._request_exit = False
                    return False
                # create file object
                file_obj = BackupFileCtrl(self,
                                          self._backup_set,
                                          os.path.join(folder_path, file),
                                          self._targets,
                                          self._tmp_dir,
                                          self._backup_set.key_hash_32,
                                          conn)
                # send update signal to push path
                self.send_signal(event_type="updated",
                                 file_path=file_obj.path)
                sql = "SELECT id, path, ctime, mtime, atime, inode, size, "\
                      "sha512 FROM lookup WHERE path = ?"
                entity_datas = conn.execute(sql,
                                            (file_obj.path, )).fetchall()
                # for simulate: trigger if backup required, take action below
                # following conditional blocks
                file_requires_backup = False
                data_to_update_in_db_kwargs = {}
                # new path
                if len(entity_datas) == 0:
                    # create new entity
                    # AQUIRE NEW ID
                    sql = "SELECT MAX(rowid) AS rowid FROM lookup"
                    entity_id = conn.execute(sql).fetchone()[0]
                    if not entity_id:
                        entity_id = 1
                    else:
                        entity_id += 1
                    logging.info("%s: Entity %s is new: %s"
                                 % (self.__class__.__name__,
                                    entity_id, file_obj.path, ))
                    sql = "SELECT sha512 FROM sha512_index WHERE sha512 = ?"
                    if len(conn.execute(sql,
                                        (file_obj.sha512, )).fetchall()) == 0:
                        file_requires_backup = True
                    if self._mode == self.MODE_BACKUP:
                        # UPDATE DB
                        data_to_update_in_db_kwargs["entity_id"] = entity_id
                        data_to_update_in_db_kwargs["file_atime"] = file_obj.atime
                        data_to_update_in_db_kwargs["file_ctime"] = file_obj.ctime
                        data_to_update_in_db_kwargs["file_inode"] = file_obj.inode
                        data_to_update_in_db_kwargs["file_mtime"] = file_obj.mtime
                        data_to_update_in_db_kwargs["file_path"] = file_obj.path
                        data_to_update_in_db_kwargs["file_size"] = file_obj.size
                        data_to_update_in_db_kwargs["file_sha512"] = file_obj.sha512
                        data_to_update_in_db_kwargs["backup_archive_name"] = file_obj.current_backup_archive_name
                # existing path
                elif len(entity_datas) == 1:
                    entity_id = entity_datas[0][0]
                    entity_path = entity_datas[0][1]
                    entity_ctime = entity_datas[0][2]
                    entity_mtime = entity_datas[0][3]
                    entity_atime = entity_datas[0][4]
                    entity_inode = entity_datas[0][5]
                    entity_size = entity_datas[0][6]
                    entity_sha512 = entity_datas[0][7]

                    if file_obj.path == entity_path: path = 1
                    else: path = 0
                    if file_obj.ctime == entity_ctime: ctime = 1
                    else: ctime = 0
                    if file_obj.mtime == entity_mtime: mtime = 1
                    else: mtime = 0
                    if file_obj.atime == entity_atime: atime = 1
                    else: atime = 0
                    if file_obj.size == entity_size: size = 1
                    else: size = 0

                    combinations = "%s%s%s%s%s" \
                                   % (path, ctime, mtime, atime, size, )

                    if combinations == "00000":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "00001":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "00010":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "00011":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "00100":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "00101":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "00110":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "00111":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "01000":
                        # OK: simple move and change in mtime, size and
                        # recent access
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "01001":
                        # OK: simple move and change in mtime, size same
                        # and recent access
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "01010":
                        # OK: simple move and change in mtime, size
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "01011":
                        # OK: simple move and change in mtime, size same
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "01100":
                        # ERROR: mtime same but size changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "01101":
                        # OK: simple move plus recent access
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "01110":
                        # ERROR: mtime same but size changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "01111":
                        # OK: simple move
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "10000":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "10001":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "10010":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "10011":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "10100":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "10101":
                        # OK: ctime, atime changed
                        # e.g. previously existing file was absent
                        # temporarily and has been moved/copied back in
                        # without change in data
                        # OR
                        # Two files, A and B, with same size have been
                        # created at same time in different locations. A has
                        # been backed-up before. Now, A has been overwritten
                        # by B. mtime and size are the same, atime might have
                        # changed, ctime certainly has and data definetaly
                        # might have as well.
                        logging.info("%s: OK: %s: %s"
                                     % (self.__class__.__name__,
                                        combinations,
                                        file_obj.path, ))
                        # BACKUP
                        sql = "SELECT sha512 FROM sha512_index WHERE sha512 = ?"
                        if len(conn.execute(sql,
                                            (file_obj.sha512, )).fetchall()
                               ) == 0:
                            file_requires_backup = True
                        # Update DB
                        if self._mode == self.MODE_BACKUP:
                            data_to_update_in_db_kwargs["entity_id"] = entity_id
                            data_to_update_in_db_kwargs["file_ctime"] = file_obj.ctime
                            data_to_update_in_db_kwargs["file_atime"] = file_obj.atime
                            if entity_sha512 != file_obj.sha512:
                                data_to_update_in_db_kwargs["file_sha512"] = file_obj.sha512
                                data_to_update_in_db_kwargs["backup_archive_name"] = file_obj.current_backup_archive_name
                    if combinations == "10110":
                        # ERROR: inode same but ctime changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "10111":
                        # OK: Same file (no change in mtime, atime, size)
                        # moved in again/overridden. Results in update of
                        # ctime only.
                        # OR
                        # Two files, A and B, with same size have been
                        # created at same time in different locations. A has
                        # been backed-up before. Now, A has been overwritten
                        # by B. mtime, atime and size are the same changed,
                        # ctime certainly has and data definetaly
                        # might have as well.
                        logging.info("%s: OK: %s: %s"
                                     % (self.__class__.__name__,
                                        combinations,
                                        file_obj.path, ))
                        # BACKUP
                        sql = "SELECT sha512 FROM sha512_index WHERE sha512 = ?"
                        if len(conn.execute(sql,
                                            (file_obj.sha512, )).fetchall()) == 0:
                            file_requires_backup = True
                        # update DB
                        if self._mode == self.MODE_BACKUP:
                            data_to_update_in_db_kwargs["entity_id"] = entity_id
                            data_to_update_in_db_kwargs["file_ctime"] = file_obj.ctime
                            if entity_sha512 != file_obj.sha512:
                                data_to_update_in_db_kwargs["file_sha512"] = file_obj.sha512
                                data_to_update_in_db_kwargs["backup_archive_name"] = file_obj.current_backup_archive_name
                    if combinations == "11000":
                        # OK: mtime, atime, size changed, rest same
                        logging.info("%s: OK: %s: %s"
                                     % (self.__class__.__name__,
                                        combinations,
                                        file_obj.path, ))
                        # BACKUP
                        sql = "SELECT sha512 FROM sha512_index WHERE sha512 = ?"
                        if len(conn.execute(sql,
                                            (file_obj.sha512, )).fetchall()) == 0:
                            file_requires_backup = True
                        # Update DB
                        if self._mode == self.MODE_BACKUP:
                            data_to_update_in_db_kwargs["entity_id"] = entity_id
                            data_to_update_in_db_kwargs["file_mtime"] = file_obj.mtime
                            data_to_update_in_db_kwargs["file_atime"] = file_obj.atime
                            data_to_update_in_db_kwargs["file_size"] = file_obj.size
                            data_to_update_in_db_kwargs["file_sha512"] = file_obj.sha512
                            data_to_update_in_db_kwargs["backup_archive_name"] = file_obj.current_backup_archive_name
                    if combinations == "11001":
                        # OK: mtime and atime changed, rest same
                        logging.info("%s: OK: %s: %s"
                                     % (self.__class__.__name__,
                                        combinations,
                                        file_obj.path, ))
                        # BACKUP
                        sql = "SELECT sha512 FROM sha512_index WHERE sha512 = ?"
                        if len(conn.execute(sql,
                                            (file_obj.sha512, )).fetchall()) == 0:
                            file_requires_backup = True
                        # Update DB
                        if self._mode == self.MODE_BACKUP:
                            data_to_update_in_db_kwargs["entity_id"] = entity_id
                            data_to_update_in_db_kwargs["file_mtime"] = file_obj.mtime
                            data_to_update_in_db_kwargs["file_atime"] = file_obj.atime
                            if entity_sha512 != file_obj.sha512:
                                data_to_update_in_db_kwargs["file_sha512"] = file_obj.sha512
                                data_to_update_in_db_kwargs["backup_archive_name"] = file_obj.current_backup_archive_name
                    if combinations == "11010":
                        # OK: regular edit, mtime, size changed, rest same
                        logging.info("%s: OK: %s: %s"
                                     % (self.__class__.__name__,
                                        combinations,
                                        file_obj.path, ))
                        # BACKUP
                        sql = "SELECT sha512 FROM sha512_index WHERE sha512 = ?"
                        if len(conn.execute(sql,
                                            (file_obj.sha512, )).fetchall()) == 0:
                            file_requires_backup = True
                        # Update DB
                        if self._mode == self.MODE_BACKUP:
                            data_to_update_in_db_kwargs["entity_id"] = entity_id
                            data_to_update_in_db_kwargs["file_mtime"] = file_obj.mtime
                            data_to_update_in_db_kwargs["file_size"] = file_obj.size
                            data_to_update_in_db_kwargs["file_sha512"] = file_obj.sha512
                            data_to_update_in_db_kwargs["backup_archive_name"] = file_obj.current_backup_archive_name
                    if combinations == "11011":
                        # OK: only mtime changed. size same
                        logging.info("%s: OK: %s: %s"
                                     % (self.__class__.__name__,
                                        combinations,
                                        file_obj.path, ))
                        # BACKUP
                        sql = "SELECT sha512 FROM sha512_index WHERE sha512 = ?"
                        if len(conn.execute(sql,
                                            (file_obj.sha512, )).fetchall()) == 0:
                            file_requires_backup = True
                        # Update DB
                        if self._mode == self.MODE_BACKUP:
                            data_to_update_in_db_kwargs["entity_id"] = entity_id
                            data_to_update_in_db_kwargs["file_mtime"] = file_obj.mtime
                            if entity_sha512 != file_obj.sha512:
                                data_to_update_in_db_kwargs["file_sha512"] = file_obj.sha512
                                data_to_update_in_db_kwargs["backup_archive_name"] = file_obj.current_backup_archive_name
                    if combinations == "11100":
                        # ERROR: size and only atime have changed
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "11101":
                        # OK: no change but has been accessed recently
                        logging.info("%s: OK: %s: %s"
                                     % (self.__class__.__name__,
                                        combinations,
                                        file_obj.path, ))
                        # Update DB
                        if self._mode == self.MODE_BACKUP:
                            data_to_update_in_db_kwargs["entity_id"] = entity_id
                            data_to_update_in_db_kwargs["file_atime"] = file_obj.atime
                    if combinations == "11110":
                        # ERROR: size has changed but rest is unchanged
                        logging.warning("%s: Unhandled combination: %s: %s"
                                        % (self.__class__.__name__,
                                           combinations,
                                           file_obj.path, ))
                    if combinations == "11111":
                        # OK: no change at all
                        logging.info("%s: OK: %s: %s"
                                     % (self.__class__.__name__,
                                        combinations,
                                        file_obj.path, ))
                # send update signal
                if file_requires_backup:
                    self.send_signal(event_type="updated",
                                     byte_num_delta=file_obj.size,
                                     file_num_increment=True)
                if self._mode == self.MODE_BACKUP:
                    if self._file_count_current % 1000 == 0:
                        conn.commit()
                    if file_requires_backup:
                        # execute backup
                        file_obj.backup()
                        # update db
                        if len(data_to_update_in_db_kwargs) > 0:
                            self._update_data_in_db(conn,
                                                    new_column_name,
                                                    **data_to_update_in_db_kwargs)
        conn.commit()
        conn.close()
        # fire processing finished signal
        self.send_signal(event_type="finished")
        return True

    def _get_worker(self):
        """ ..

        :rtype: *tuple*

        Returns a tuple with :class:`BackupThreadWorker` and QtCore.QThread.
        Returns the currently active worker/thread, creates and returns a \
        new pair otherwise.
        """
        if self._thread == None or self._thread.isFinished():

            def reset_refs():
                self._thread = None

            self._thread = QtCore.QThread()
            self._thread.finished.connect(reset_refs)
            self._worker = BackupThreadWorker(self._execute,
                                              (),
                                              self._thread)
        return self._worker, self._thread

    def _update_db(self, conn):
        """ ..

        (Re-)creates the structure of the database; adds/alters any new
        elements that might have changed (in the datas schema e.g.).
        """
        # create tables
        conn.execute("CREATE TABLE IF NOT EXISTS atime (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS ctime (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS inode (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS lookup (id INTEGER PRIMARY KEY, "\
                                                        "path TEXT UNIQUE, "\
                                                        "ctime REAL, "\
                                                        "mtime REAL, "\
                                                        "atime REAL, "\
                                                        "inode INTEGER, "\
                                                        "size INTEGER, "\
                                                        "sha512 TEXT,"\
                                                        "backup_archive_name TEXT)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS lookup_path ON lookup (path)")
        conn.execute("CREATE TABLE IF NOT EXISTS mtime (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS online (id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS path (id INTEGER PRIMARY KEY, "\
                                                      "path TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS sha512 (id INTEGER PRIMARY KEY)")
        # a hash index table with all hashes (data-streams) in backup-set.
        conn.execute("CREATE TABLE IF NOT EXISTS sha512_index (sha512 TEXT PRIMARY KEY, "\
                                                              "backup_archive_name TEXT)")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS sha512_index_sha512 ON sha512_index (sha512)")
        conn.execute("CREATE TABLE IF NOT EXISTS size (id INTEGER PRIMARY KEY)")
        # create new columns for current run
        # on fast successive attempts same name might be produced (based on
        # unix timestamp) so, cycle through and update timestamp string in name
        # until success
        new_columns_created = False
        while not new_columns_created:
            new_column_name = "snapshot_%s" % (int(time.time()), )
            try:
                conn.execute("ALTER TABLE atime ADD COLUMN %s REAL"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE ctime ADD COLUMN %s REAL"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE inode ADD COLUMN %s INTEGER"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE mtime ADD COLUMN %s REAL"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE online ADD COLUMN %s INTEGER"
                             % (new_column_name, ))
                # no need to update, path would never change between sessions
#                conn.execute("ALTER TABLE path ADD COLUMN %s TEXT"
#                             % (new_column_name, ))
                conn.execute("ALTER TABLE sha512 ADD COLUMN %s TEXT"
                             % (new_column_name, ))
                conn.execute("ALTER TABLE size ADD COLUMN %s INTEGER"
                             % (new_column_name, ))
                new_columns_created = True
            except:
                time.sleep(0.5)
        return new_column_name

    def _update_data_in_db(self, conn, new_column_name, **kwargs):
        """ ..

        Updates a specific entity-dataset in database during backup procedure.
        Depending on what values are passed in, updates corresponding tables in
        backup-set database.
        `entity_id` is mandatory as the lookup always needs to be updated as
        well.
        """
        columns_to_update = []
        columns_to_update_data = []
        try:
            entity_id = kwargs["entity_id"]
            columns_to_update.append("id")
            columns_to_update_data.append(entity_id)
        except: pass
        try:
            file_atime = kwargs["file_atime"]
            columns_to_update.append("atime")
            columns_to_update_data.append(file_atime)
        except: pass
        try:
            backup_archive_name = kwargs["backup_archive_name"]
            columns_to_update.append("backup_archive_name")
            columns_to_update_data.append(backup_archive_name)
        except: pass
        try:
            file_ctime = kwargs["file_ctime"]
            columns_to_update.append("ctime")
            columns_to_update_data.append(file_ctime)
        except: pass
        try:
            file_inode = kwargs["file_inode"]
            columns_to_update.append("inode")
            columns_to_update_data.append(file_inode)
        except: pass
        try:
            file_mtime = kwargs["file_mtime"]
            columns_to_update.append("mtime")
            columns_to_update_data.append(file_mtime)
        except: pass
        try:
            file_path = kwargs["file_path"]
            columns_to_update.append("path")
            columns_to_update_data.append(file_path)
        except: pass
        try:
            file_size = kwargs["file_size"]
            columns_to_update.append("size")
            columns_to_update_data.append(file_size)
        except: pass
        try:
            file_sha512 = kwargs["file_sha512"]
            columns_to_update.append("sha512")
            columns_to_update_data.append(file_sha512)
        except: pass

        try:
            # check if entity already exists
            res = conn.execute("SELECT id FROM lookup WHERE id = ?",
                               (entity_id, )).fetchall()
            # new entity
            if len(res) == 0:
                # write data to database
                conn.execute("INSERT INTO lookup (id, path, ctime, mtime, atime, inode, size, sha512, backup_archive_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (entity_id, file_path, file_ctime, file_mtime,
                              file_atime, file_inode, file_size, file_sha512,
                              backup_archive_name, ))

                conn.execute("INSERT INTO atime (id, %s) VALUES (?, ?)"
                             % (new_column_name, ), (entity_id, file_atime, ))
                conn.execute("INSERT INTO ctime (id, %s) VALUES (?, ?)"
                             % (new_column_name, ), (entity_id, file_ctime, ))
                conn.execute("INSERT INTO inode (id, %s) VALUES (?, ?)"
                             % (new_column_name, ), (entity_id, file_inode, ))
                conn.execute("INSERT INTO mtime (id, %s) VALUES (?, ?)"
                             % (new_column_name, ), (entity_id, file_mtime, ))
                conn.execute("INSERT INTO online (id, %s) VALUES (?, ?)"
                             % (new_column_name, ), (entity_id, True, ))
                conn.execute("INSERT INTO path (id, path) VALUES (?, ?)",
                             (entity_id, file_path, ))
                conn.execute("INSERT INTO size (id, %s) VALUES (?, ?)"
                             % (new_column_name, ), (entity_id, file_size, ))
                conn.execute("INSERT INTO sha512 (id, %s) VALUES (?, ?)"
                             % (new_column_name, ), (entity_id, file_sha512, ))
                logging.debug("%s: New Entity added: %s"
                              % (self.__class__.__name__, entity_id, ))
            # existing entity
            else:
                # update lookup
                if len(columns_to_update) > 0:
                    # generate SQL code
                    setters = ""
                    for column in columns_to_update:
                        setters += "%s = ?, " % (column, )
                    setters = setters[:-2] + " WHERE id = " + str(entity_id)
                    conn.execute("UPDATE lookup SET %s"
                                 % (setters, ), list(columns_to_update_data))
                    logging.debug("%s: lookup updated: %s"
                                  % (self.__class__.__name__, entity_id, ))
                # update atime
                try:
                    conn.execute("UPDATE atime SET %s = ? WHERE id = ?"
                                 % (new_column_name, ),
                                 (file_atime, entity_id, ))
                    logging.debug("%s: atime updated: %s"
                                  % (self.__class__.__name__, entity_id, ))
                except: pass
                # update ctime
                try:
                    conn.execute("UPDATE ctime SET %s = ? WHERE id = ?"
                                 % (new_column_name, ),
                                 (file_ctime, entity_id, ))
                    logging.debug("%s: ctime updated: %s"
                                  % (self.__class__.__name__, entity_id, ))
                except: pass
                # update inode
                try:
                    conn.execute("UPDATE inode SET %s = ? WHERE id = ?"
                                 % (new_column_name, ),
                                 (file_inode, entity_id, ))
                    logging.debug("%s: inode updated: %s"
                                  % (self.__class__.__name__, entity_id, ))
                except: pass
                # update mtime
                try:
                    conn.execute("UPDATE mtime SET %s = ? WHERE id = ?"
                                 % (new_column_name, ),
                                 (file_mtime, entity_id, ))
                    logging.debug("%s: mtime updated: %s"
                                  % (self.__class__.__name__, entity_id, ))
                except: pass
                # update online
                try:
                    conn.execute("UPDATE online SET %s = ? WHERE id = ?"
                                 % (new_column_name, ),
                                 (True, entity_id, ))
                    logging.debug("%s: online updated: %s"
                                  % (self.__class__.__name__, entity_id, ))
                except: pass
                # update path
                # no need to update: path is primary representation of entity,
                # thus would never change between snapshots for a single entity
                # update size
                try:
                    conn.execute("UPDATE size SET %s = ? WHERE id = ?"
                                 % (new_column_name, ),
                                 (file_size, entity_id, ))
                    logging.debug("%s: size updated: %s"
                                  % (self.__class__.__name__, entity_id, ))
                except: pass
                # update sha512
                try:
                    conn.execute("UPDATE sha512 SET %s = ? WHERE id = ?"
                                 % (new_column_name, ),
                                 (file_sha512, entity_id, ))
                    logging.debug("%s: sha512 updated: %s"
                                  % (self.__class__.__name__, entity_id, ))
                except: pass
            # update sha512_index
            # add hash to db and stream to targets
            try:
                conn.execute("INSERT INTO sha512_index (sha512, backup_archive_name) VALUES (?, ?)",
                             (file_sha512, backup_archive_name))
                logging.debug("%s: sha512_index updated: %s"
                              % (self.__class__.__name__, entity_id, ))
            # If hash already exists in index table, pass following exception
            except sqlite3.IntegrityError as e:
                pass
            # if data is not available (attributes weren't passed into method,
            # e.g. when only marking entity as online...)
            except UnboundLocalError as e:
                pass
        except:
            raise

    def backup(self):
        """ ..

        :rtype: *bool*

        Initiates the execution in backup-mode.
        """
        # set mode
        self._mode = self.MODE_BACKUP

        # reset mode
        def reset_mode():
            self._mode = None
        worker, thread = self._get_worker()
        thread.finished.connect(reset_mode)
        # return worker
        return worker, thread

    def reset(self):
        """ ..

        Resets the controller including the file- and byte-counters.
        """
        self._byte_count_current = 0
        self._byte_count_total = 0
        self._file_count_current = 0
        self._file_count_total = 0

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Requests any threads running on the object to exit and returns *True* \
        when done so.
        """
        if self._thread and\
            self._thread.isRunning():
            self._worker.request_exit()
            self._request_exit = True
            while self._thread.isRunning() or\
                self._request_exit:
                time.sleep(0.1)
        return True

    def send_signal(self, **kwargs):
        """ ..

        :param str event_type: Type of signal to send:

            - ``update`` if an update signal is to be sent
            - ``finish`` if a finish signal is to be sent

        :param int byte_count_delta: The number of processed bytes since the \
        last signal the signal is to report.
        :param bool file_num_increment: Whether or not this update is to \
        increment the current file-count or just a partial (capacity-delta) \
        update.
        :param arbitrary kwargs: The following keyword-attributes are \
        available:

            - **byte_count_delta** (*int*):
            - **event_source** (*enum*): Defines the source-process the \
            update call is coming from. Needs to be of either of the following:

                - ``hash``, if this method is called from a hashing process
                - ``backup``, if this method is called from a backup process

            - **event_type** (*str*): One of the following strings:

                - ``updated``, if an :attr:`updated_signal` is to be emitted.
                - ``finished``, if a :attr:`finished_signal` is to be emitted.

            - **file_num_increment** (*bool*):
            - **file_path** (*str*):

        :rtype: *void*

        Central event dispatch manager that acts as central \
        report-and-dispatch point for reporting objects (such as \
        BackupFileCtrl, hash-objects, etc.).
        """
        # get data from kwargs
        byte_count_delta = kwargs.get("byte_count_delta", None)
        event_source = kwargs.get("event_source", None)
        event_type = kwargs.get("event_type", None)
        file_path = kwargs.get("file_path", None)
        file_num_increment = kwargs.get("file_num_increment", False)
        # update ivars
        if event_type == "updated":
            if file_num_increment:
                if self._mode == self.MODE_SIMULATE:
                    self._file_count_total += 1
                elif self._mode == self.MODE_BACKUP:
                    self._file_count_current += 1
            elif byte_count_delta:
                if self._mode == self.MODE_SIMULATE:
                    if event_source == "hash":
                        self._byte_count_total += byte_count_delta
                elif self._mode == self.MODE_BACKUP:
                    if event_source == "backup":
                        self._byte_count_current += byte_count_delta
        if self._mode == self.MODE_BACKUP:
            simulate = False
        elif self._mode == self.MODE_SIMULATE:
            simulate = True
        # compile kwargs for event
        kwargs = {"byte_count_total": self._byte_count_total,
                  "byte_count_current": self._byte_count_current,
                  "byte_count_delta": byte_count_delta,
                  "file_count_total": self._file_count_total,
                  "file_count_current": self._file_count_current,
                  "file_num_increment": file_num_increment,
                  "file_path": file_path,
                  "simulate": simulate,
                  }
        # instantiate event
        e = BackupUpdateEvent(**kwargs)
        # send off
        if event_type == "finished":
            self.finished_signal.emit(e)
        if event_type == "updated":
            self.updated_signal.emit(e)

    def simulate(self):
        """ ..

        :param bool force_refresh: If *True*, forces a rescan of the \
        associated source. Always scans sources on its first run to aquire \
        an initial data-set.
        :rtype: *void*

        Initiates the execution in backup-mode that accumulates the total \
        capacity (in bytes) that is due for back-up.
        """
        # set mode
        self._mode = self.MODE_SIMULATE

        # reset mode
        def reset_mode():
            self._mode = None
        worker, thread = self._get_worker()
        thread.finished.connect(reset_mode)
        # return worker
        return worker, thread


class BackupFileCtrl(object):
    """ ..

    :param bs.ctrl.session.BackupCtrl backup_ctrl:
    :param bs.ctrl.session.BackupSetCtrl backup_set: The *backup-set* \
    assocaited with this backup-file instance.
    :param str file_path: This file's absolute *file-path* on the file-system.
    :param list targets: The *list* of \
    :class:`bs.ctrl.session.BackupTargetCtrl` s that are associated with this \
    *session's* :class:`bs.ctrl.session.BackupTargetsCtrl`
    :param tempfile.TemporaryDirectory tmp_dir: A temporary location on disk \
    to use as temporary storage location for compression- and encryption \
    purposes.
    :param str key_hash_32: A valid 256-bit/32byte hex-key used as encryption \
    key for the associated *backup-targets*. If an invalid key is given, \
    backup to the target(s) will fail.
    :param Sqlite3.Cursor conn: An open cursor to the database managing the \
    file-entities' states and -history.

    Representation of a backup-file during a backup-job execution.
    """
    _backup_ctrl = None
    _backup_set = None
    _path = None
    _targets = None
    # This is currently a soft-limit
    _target_archive_max_size = 1024 * 1024 * 12
    _sha512 = None
    _ctime = None
    _mtime = None
    _atime = None
    _inode = None
    _size = None
    _compression_level = 6
    _buffer_size = 1024 * 1024
    _key_hash_32 = None
    _conn = None
    _tmp_dir = None
    _tmp_file_path = None
    _current_backup_archive_name = None

    def __init__(self, backup_ctrl, backup_set, file_path, targets, tmp_dir,
                 key_hash_32, conn):
        self._backup_ctrl = backup_ctrl
        self._backup_set = backup_set
        self._path = os.path.realpath(file_path)
        self._targets = targets
        # get file stats
        stat = os.stat(self._path)
        self._ctime = stat.st_ctime
        self._mtime = stat.st_mtime
        self._atime = stat.st_atime
        self._inode = stat.st_ino
        self._size = stat.st_size
        self._tmp_dir = tmp_dir
        self._key_hash_32 = key_hash_32
        self._conn = conn

    def __del__(self):
        """ *
        Removes the associated temporary file when this object is deleted.
        """
        self._remove_tmp_file()

    @property
    def atime(self):
        """
        :type: *float*

        The file's *access time stamp*.
        """
        return self._atime

    @property
    def ctime(self):
        """
        :type: *float*

        This file's *creation time stamp*.
        """
        return self._ctime

    @property
    def current_backup_archive_name(self):
        """ ..

        :type: *str*

        The name of the latest archive-file found in the targets that will be \
        used to backup this file to. If this file (hash) already exists in \
        the set's database, the stored archive-name is returned. If a \
        soft-limit on backup-archive file-size is set, this is necessary to \
        find the last archive-file that has not yet reached its soft-limit.
        """
        if self._current_backup_archive_name:
            return self._current_backup_archive_name
        else:
            ## ABSTRACT ####################
            ################################
            # if sha_512 already in db index (already backed-up), get corresponding archive name
            # else if not backed-up yet (not in db)
                # scan all targets, select latest archive name of all of them
                # construct path for latest backup archive, if found
                # if latest archive found and size below threshold, use this latest archive
                    # on all targets:
                        # create archive on all targets/check for valid file if exists
                        # on fail: SystemExit
                # if no archive found at all or latest found archive exceeds size threshold:
                    # create new archive name
                    # for all targets
                        # create set path, archive
                        # on fail: SystemExit
                # return latest/new archive name

            # try to get archive-name from db
            sql = "SELECT backup_archive_name FROM sha512_index WHERE sha512 = ?"
            res = self._conn.execute(sql,
                               (self.sha512, )).fetchall()
            if len(res) == 1:
                return res[0][0]
            else:
                latest_archive_name = None
                # scan all targets, select latest archive name of all of them
                for target in self._targets:
                    target_path = target.target_path
                    # create set dir
                    backup_set_path = os.path.join(target_path, self._backup_set.set_uid)
                    if not os.path.isdir(backup_set_path):
                        os.makedirs(backup_set_path)
                    for folder_path, folders, files in os.walk(backup_set_path):
                        folders = []
                        for file in sorted(files, reverse=True):
                            try:
                                file_path = os.path.join(folder_path, file)
                                # if found latest archive (name) is "newer" than
                                # current latest_archive_name, replace with current
                                if not latest_archive_name or \
                                    int(os.path.splitext(file)[0]) > int(os.path.splitext(latest_archive_name)[0]):
                                    latest_archive_name = file
                                break
                            except:
                                pass
                # construct path for latest backup archive, if found
                backup_archive_path = None
                try:
                    backup_archive_path = os.path.join(backup_set_path,
                                                       latest_archive_name)
                except: pass
                # if latest archive found and size below threshold, use this
                # latest archive
                if latest_archive_name and\
                    backup_archive_path and\
                    os.path.getsize(backup_archive_path) < self._target_archive_max_size:
                    # on all targets:
                    for target in self._targets:
                        target_path = target.target_path
                        backup_set_path = os.path.join(target_path,
                                                       self._backup_set.set_uid)
                        # create archive on all targets/check for valid file if
                        # exists
                        if not os.path.isfile(backup_archive_path):
                            try:
                                f = zipfile.ZipFile(backup_archive_path, "w")
                                f.close()
                            # on fail: SystemExit
                            except Exception as e:
                                raise SystemExit(e)
                # if no archive found at all or latest found archive exceeds
                # size threshold:
                else:
                    # create new archive name
                    new_archive_name = str(int(time.time())) + ".zip"
                    # for all targets
                    for target in self._targets:
                        target_path = target.target_path
                        new_archive_path = os.path.join(target_path,
                                                        self._backup_set.set_uid,
                                                        new_archive_name)
                        # create set path, archive
                        try:
                            f = zipfile.ZipFile(new_archive_path, "w")
                            f.close()
                            latest_archive_name = new_archive_name
                        # on fail: SystemExit
                        except Exception as e:
                            raise SystemExit(e)
                self._current_backup_archive_name = latest_archive_name
                return self._current_backup_archive_name

    @property
    def inode(self):
        """
        :type: *int*

        This backup-file's *inode* value.
        """
        return self._inode

    @property
    def mtime(self):
        """
        :type: *float*

        This backup-file's *modification time*
        """
        return self._mtime

    @property
    def path(self):
        """
        :type: *str*

        This backup-file's absolute path on the file-system.
        """
        return self._path

    @property
    def sha512(self):
        """ ..

        :type: *str*

        This backup-file's *SHA512 hexadecimal hash-value*. This is a \
        lazy property.
        """
        if not self._sha512:
            self._sha512 = bs.utils.HashFile(self._path,
                                             send_signal_handler=self._backup_ctrl.send_signal
                                             ).start()
        return self._sha512

    @property
    def size(self):
        """
        :type: *int*

        This backup-file's *physical size* in bytes.
        """
        return self._size

    def _remove_tmp_file(self):
        """ * """
        try:
            os.unlink(self._tmp_file_path)
            return True
        except:
            return False

    def _compress_zlib_encrypt_aes(self):
        """ ..

        :rtype: *void*

        Encrypts and compresses the file and stores it into all targets.
        """
        time_start = time.time()
        logging.debug("%s: Compressing (zlib)/encrypting (AES) file: %s" \
                      % (self.__class__.__name__, self._path, ))

        f_in = open(self._path, "rb")
        f_out = tempfile.NamedTemporaryFile(dir=self._tmp_dir.name,
                                            mode="a+b",
                                            delete=False)

        compression_obj = zlib.compressobj(level=self._compression_level)

        iv = Crypto.Random.new().read(Crypto.Cipher.AES.block_size)
        counter = Crypto.Util.Counter.new(128)
        aes = Crypto.Cipher.AES.new(binascii.unhexlify(self._key_hash_32),
                                    Crypto.Cipher.AES.MODE_CTR,
                                    iv,
                                    counter)

        f_out.write(iv)
        while True:
            data = f_in.read(self._buffer_size)
            if not data:
                break
            data_compressed_unencrypted = compression_obj.compress(data)
            data_compressed_unencrypted += compression_obj.flush(zlib.Z_SYNC_FLUSH)
            data_compressed_encrypted = aes.encrypt(data_compressed_unencrypted)
            f_out.write(data_compressed_encrypted)
            # emit updated signal
            self._backup_ctrl.send_signal(event_type="updated",
                                          byte_count_delta=len(data),
                                          event_source="backup",
                                          file_path=self.path)

        data_compressed_unencrypted = compression_obj.flush(zlib.Z_FINISH)
        data_compressed_encrypted = aes.encrypt(data_compressed_unencrypted)
        f_out.write(data_compressed_encrypted)

        f_in.close()
        f_out.close()
        self._remove_tmp_file()
        self._tmp_file_path = f_out.name

        time_elapsed = time.time() - time_start
        logging.debug("%s: Compression/Encryption done (%.2fs)." \
                      % (self.__class__.__name__, time_elapsed))
        # add to target(s)
        self._add_to_targets()

    def _compress_bz2(self):
        """ * """
        pass

    def _compress_lzma(self):
        """ * """
        pass

    def _add_to_targets(self):
        """ * """
        backup_archive_name = self.current_backup_archive_name

        time_start = time.time()
        logging.debug("%s: Adding to target archive(s): %s"
                      % (self.__class__.__name__,
                         backup_archive_name, ))

        for target in self._targets:
            target_path = target.target_path
            backup_archive_path = os.path.join(target_path,
                                               self._backup_set.set_uid,
                                               backup_archive_name)
            f_archive = zipfile.ZipFile(backup_archive_path,
                                        "a",
                                        allowZip64=True)
            # only add if not already exist
            members = f_archive.namelist()
            if self.sha512 not in members:
                f_archive.write(self._tmp_file_path, arcname=self.sha512)
                f_archive.close()

                time_elapsed = time.time() - time_start
                logging.info("%s: Successfully added to target archive(s) "\
                              "(%.2fs)."
                              % (self.__class__.__name__,
                                 time_elapsed))
            else:
                logging.warning("%s: The backup file already exists in the "\
                                "current archive file: %s"
                                % (self.__class__.__name__,
                                   self.sha512))

    def backup(self):
        """ ..

        :rtype: *void*

        Executes the backup of this *backup-file*.
        """
        self._compress_zlib_encrypt_aes()


class BackupThreadWorker(QtCore.QObject):
    """ ..

    :param QtCore.QThread thread: The :class:`QtCore.QThread` this worker is \
    to run on.
    :param object handler: The handler to the method the worker is to execute.
    :param tuple args: A tuple of arguments to pass to the ``handler`` method.
    :ivar QtCore.Signal finished:
    :ivar QtCore.Signal started: Emits when :meth:`start` is called and the \
    thread starts evoking :meth:`process`

    This class inheriting from :class:`QtCore.QObject` is to be used to \
    execute methods from :class:`BackupCtrl` on a :class:`QtCore.QThread`.
    This enables :class:`BackupCtrl` to send signals that update objects on \
    the Qt-GUI-thread.
    """
    _args = None
    _handler = None
    _thread = None
    finished = QtCore.Signal()
    started = QtCore.Signal()

    def __init__(self, handler, args, thread):
        """ ..

        """
        super(BackupThreadWorker, self).__init__()

        self._args = args
        self._handler = handler
        self._thread = thread
        # set-up
        self.moveToThread(self._thread)
        self._thread.started.connect(self.started.emit)
        self._thread.started.connect(self._process)
        self._thread.finished.connect(self.finished.emit)
        self._thread.finished.connect(self._thread.deleteLater)

    def _process(self):
        """ ..

        :rtype: *void*

        Called by the associated thread and evokes the ``handler`` passed \
        into the constructor, together with provided ``args`` as parameters.
        This method is not to be called directly. Call :meth:`start` instead \
        to start the thread-worker.
        """
        # execute handle
        self._handler(*self._args)
        self._thread.quit()

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all \
        children.
        """
        # overwrite signals
        self.finished = QtCore.Signal()
        self.started = QtCore.Signal()
        return True

    def start(self):
        """ ..

        :rtype: *void*

        Starts the thread-worker in its own thread.
        """
        if not self._thread.isRunning():
            self._thread.start()


class BackupRestoreCtrl(object):
    """ ..

    :param bs.ctrl.session.BackupSetCtrl set_obj: The *backup-set* to restore \
    from.

    :param list entity_ids: The *list of entity-IDs* of the files to restore.

    :param str restore_location: The absolute path to the location on the \
    file-system to restore to.

    :param int snapshot_to_restore_tstamp: The *snapshot-ID* to restore from.

    Restores a set of files, given by their *file-IDs* from a given
    *snapshot-ID* and their associated *backup-set* to a given
    *backup-location* on the computer's file-system.
    """
    _set_obj = None
    _entity_ids = None
    _restore_location = None
    _snapshot_to_restore_tstamp = None
    _key_hash_32 = None
    _buffer_size = 1024 * 1024

    def __init__(self, set_obj, entity_ids, restore_location,
                 snapshot_to_restore_tstamp):
        """ * """
        self._set_obj = set_obj
        self._entity_ids = entity_ids
        self._restore_location = restore_location
        self._snapshot_to_restore_tstamp = snapshot_to_restore_tstamp
        self._tmp_dir = tempfile.TemporaryDirectory()

    @property
    def key_hashed_32(self):
        """ ..

        :type: *str*

        The valid 256-bit/32byte hex-key the backup-target(s) is/are \
        encrypted with. If an invalid key is given, the extraction from the \
        backup-target will fail.
        """
        if not self._key_hash_32:
            while not self._key_hash_32:
                key_raw = getpass.getpass("This set is encrypted; please "\
                                          "enter the corresponding password:")
                salt_dk = hashlib.sha512(key_raw.encode()).hexdigest()
                # verify hash_64
                if salt_dk == self._set_obj.salt_dk:
                    key_hash_32 = hashlib.sha256(key_raw.encode()).digest()
                    self._key_hash_32 = key_hash_32
                    return self._key_hash_32

    def start(self):
        """ ..

        :rtype: *void*

        Initiates the restore-process.
        """
        for entity_id in self._entity_ids:
            # restore-file obj, provides all necessary metadata about entity
            backup_restore_file = BackupRestoreFileCtrl(self._set_obj,
                                                    entity_id,
                                                    self._snapshot_to_restore_tstamp)
            self._unzip_file(backup_restore_file)
            self._decrypt_aes_decompress_zlib(backup_restore_file)

    def _remove_tmp_file(self):
        """ * """
        try:
            os.unlink(self._tmp_file_path)
            return True
        except:
            return False

    def _unzip_file(self, backup_restore_file):
        """ * """
        time_start = time.time()
        logging.debug("%s: Unzipping file: %s"
                      % (self.__class__.__name__,
                         backup_restore_file.file_path, ))

        f_zip = zipfile.ZipFile(backup_restore_file.backup_archive_path,
                                mode="r")

        self._tmp_file_path = f_zip.extract(backup_restore_file.sha512_db,
                                            path=self._tmp_dir.name)

        time_elapsed = time.time() - time_start
        logging.debug("%s: File successfully unzipped (%.2fs)."
                      % (self.__class__.__name__,
                         time_elapsed))

    def _decrypt_aes_decompress_zlib(self, backup_restore_file):
        """ * """
        time_start = time.time()
        logging.debug("%s: Decrypting (AES) file..."
                      % (self.__class__.__name__, ))

        f_in = open(self._tmp_file_path, "rb")
        # create full restore file-path (restore location + orig. file path)
        f_out_path = self._restore_location
        if re.match("^[a-zA-Z]:\\\\.*$", backup_restore_file.file_path):
            f_out_path = os.path.join(self._restore_location,
                                      backup_restore_file.file_path[:1],
                                      backup_restore_file.file_path[3:])
        else:
            logging.critical("%s: This ouput path format still needs to be "\
                             "configured to be appended to the "\
                             "restore_location: %s"
                             % (self.__class__.__name__,
                                backup_restore_file.file_path, ))
            raise SystemExit
        os.makedirs(os.path.dirname(f_out_path))
        f_out = open(f_out_path, "a+b")

        decompression_obj = zlib.decompressobj()

        iv = f_in.read(Crypto.Cipher.AES.block_size)
        counter = Crypto.Util.Counter.new(128)
        aes = Crypto.Cipher.AES.new(self.key_hashed_32,
                                    Crypto.Cipher.AES.MODE_CTR, iv, counter)

        while True:
            data = f_in.read(self._buffer_size)
            if not data:
                break
            data_compressed_decrypted = aes.decrypt(data)
            data_decompressed_decrypted = decompression_obj.decompress(data_compressed_decrypted)
            data_decompressed_decrypted += decompression_obj.flush(zlib.Z_SYNC_FLUSH)
            f_out.write(data_decompressed_decrypted)
        f_in.close()
        f_out.close()

        self._remove_tmp_file()

        time_elapsed = time.time() - time_start
        logging.debug("%s: File successfully decrypted (%.2fs)."
                      % (self.__class__.__name__,
                         time_elapsed))


class BackupRestoreFileCtrl(object):
    """ ..

    :param bs.ctrl.session.BackupSetCtrl set_obj: The *backup-set* to restore \
    from.

    :param int entity_id: The *entity-ID* of the file to restore.

    :param int snapshot_to_restore_tstamp: The *snapshot-ID* to restore from.

    A single *restore-file instance* representing a backed-up file at its \
    distinct stage in the *backup-target*.

    This class is usually instantiated by :class:`BackupRestoreCtrl` and \
    should not be accessed manually.
    """
    _set_obj = None
    _entity_id = None
    _snapshot_to_restore_tstamp = None
    _backup_archive_paths = []  # list of all available backup archive paths
    _sha512_db = None
    _backup_archive_name = None
    _file_name = None

    def __init__(self, set_obj, entity_id, snapshot_to_restore_tstamp):
        """ * """
        self._set_obj = set_obj
        self._entity_id = entity_id
        self._snapshot_to_restore_tstamp = snapshot_to_restore_tstamp

    @property
    def backup_archive_path(self):
        """ ..

        :type: *list*

        A list of all available backup archive paths that are currently \
        online on the system.
        """
        if not self._backup_archive_paths:
            for target in self._set_obj.targets:
                target_path = target.target_path
                backup_archive_path = os.path.join(target_path,
                                                   self._set_obj.set_uid,
                                                   self.backup_archive_name)
                self._backup_archive_paths.append(backup_archive_path)
        return self._backup_archive_paths[0]

    @property
    def sha512_db(self):
        """ ..

        :type: *str*

        This *backup-file*'s *SHA512 hexadecimal hash* as stored in the \
        database.
        """
        if not self._sha512_db:
            self._sha512_db = self._get_latest_data_in_table("sha512")
        return self._sha512_db

    @property
    def backup_archive_name(self):
        """ ..

        :type: *str*

        The *backup-archive*'s filename the associated file is stored in.
        """
        if not self._backup_archive_name:
            conn = sqlite3.connect(self._set_obj.set_db_path)
            res = conn.execute("SELECT backup_archive_name FROM sha512_index WHERE sha512 = ?",
                               (str(self.sha512_db), )).fetchall()
            self._backup_archive_name = res[0][0]
            conn.close()
        return self._backup_archive_name

    @property
    def file_path(self):
        """ ..

        :type: *str*

        The *backup-file*'s absolute original *file-path* it was backuped from.
        """
        if not self._file_name:
            conn = sqlite3.connect(self._set_obj.set_db_path)
            res = conn.execute("SELECT path FROM path WHERE id = ?",
                               (self._entity_id, )).fetchall()
            self._file_name = res[0][0]
            conn.close()
        return self._file_name

    def _get_latest_data_in_table(self, table_name):
        """ ..

        Gets the file_id's data in db for the latest snapshot-column that has
        data on it.
        """
        conn = sqlite3.connect(self._set_obj.set_db_path)
        # sorted list of of all snapshot_timestamps (snapshot column-names) in
        # table_name, latest first, descending
        res = conn.execute("PRAGMA table_info(%s)"
                                      % (table_name, )).fetchall()
        column_names = sorted([x[1] for x in res], reverse=True)
        column_names.pop(len(column_names)-1)
        # extract timestamps from snapshot-column-names and cast into int
        snapshot_timestamps = []
        for column_name in column_names:
            snapshot_timestamps.append(int(column_name[9:]))
        snapshot_data = None
        for snapshot_timestamp in snapshot_timestamps:
            # ignore snapshots that are younger than targeted timestamp
            if snapshot_timestamp <= self._snapshot_to_restore_tstamp:
                while not snapshot_data:
                    snapshot_name = "snapshot_" + str(snapshot_timestamp)
                    res = conn.execute("SELECT %s FROM %s WHERE id = ?"
                                       % (snapshot_name, table_name, ),
                                       (self._entity_id, )).fetchall()
                    if len(res[0]) > 0:
                        snapshot_data = res[0][0]
                        break
        conn.close()
        return snapshot_data
