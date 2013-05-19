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

""" * """

import Crypto.Cipher.AES
import Crypto.Random
import Crypto.Util.Counter
import bs.utils
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


class Backup(object):
    """ * """
    _backup_set = None
    _key_hash_32 = None
    _sources = None
    _targets = None
    _tmp_dir = None

    def __init__(self, set):
        self._backup_set = set
        self._sources = set.sources
        self._targets = set.targets
        self._tmp_dir = tempfile.TemporaryDirectory()

    def _update_db(self, conn):
        """ *
        Returns the name of the new (session-)column
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
        """ *
        Depending on what values are passed in, updates according tables in
        backup set database.
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
                # thus would never change between snapshots for a singe
                # entity_id
#                try:
#                    conn.execute("UPDATE path SET %s = ? WHERE id = ?"
#                                 % (new_column_name, ),
#                                 (file_path, entity_id, ))
#                    logging.debug("%s: path updated: %s"
#                                  % (self.__class__.__name__, entity_id, ))
#                except: pass
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

    def backup_exec(self):
        """ * """
        # check if set is encrypted and prompt for key_raw-input
        # a key_raw is set as indicated by 64-bit verification hash in db:
        if self._backup_set.key_hash_64:
            key_raw = getpass.getpass("The backup-set is encrypted. Please "\
                                      "enter the key_raw to continue:")
            key_hash_32 = hashlib.sha256(key_raw.encode()).digest()
            key_hash_64 = hashlib.sha512(key_raw.encode()).hexdigest()
            # compare hash of entered key against hash_64 in db/on set-obj
            if key_hash_64 == self._backup_set.key_hash_64:
                self._key_hash_32 = key_hash_32
            # if mismatch, prompt and exit
            else:
                logging.critical("%s: The password entered is invalid; the "\
                                 "backup-process can not continue."
                                 % (self.__class__.__name__, ))
                raise SystemExit
        # update database
        conn = sqlite3.connect(self._backup_set.set_db_path)
        new_column_name = self._update_db(conn)
        bytes_processed = [0, 0]
        files_processed = 0

        time_start = time.time()
        i = 0
        for source in self._sources:
            source_path = source.source_path
            for folder_path, folders, files in os.walk(source_path):
                for file in files:
                    # create file object
                    file_obj = BackupFile(self._backup_set,
                                          os.path.join(folder_path, file),
                                          self._targets,
                                          self._tmp_dir,
                                          key_hash_32)

                    entity_datas = conn.execute("SELECT id, path, ctime, mtime, atime, inode, size, sha512 FROM lookup WHERE path = ?",
                                                (file_obj.path, )).fetchall()
                    # new path
                    if len(entity_datas) == 0:
                        # create new entity
                        # AQUIRE NEW ID
                        entity_id = conn.execute("SELECT MAX(rowid) AS rowid FROM lookup").fetchone()[0]
                        if not entity_id:
                            entity_id = 1
                        else:
                            entity_id += 1
                        logging.info("%s: Entity %s is new: %s"
                                     % (self.__class__.__name__,
                                        entity_id, file_obj.path, ))
                        # this might still be an identic data-stream that existed
                        # under a different path/entity before, so only back-up
                        # if hash is unique
                        if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                            (file_obj.sha512, )).fetchall()) == 0:
                            # BACKUP
                            file_obj.backup()
                        # UPDATE DB
                        self._update_data_in_db(conn,
                                                new_column_name,
                                                entity_id=entity_id,
                                                file_atime=file_obj.atime,
                                                file_ctime=file_obj.ctime,
                                                file_inode=file_obj.inode,
                                                file_mtime=file_obj.mtime,
                                                file_path=file_obj.path,
                                                file_size=file_obj.size,
                                                file_sha512=file_obj.sha512,
                                                backup_archive_name=file_obj.current_backup_archive_name)
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
                            logging.info("%s: OK: %s: %s"
                                         % (self.__class__.__name__,
                                            combinations,
                                            file_obj.path, ))
                            # update DB
                            self._update_data_in_db(conn,
                                                    new_column_name,
                                                    entity_id=entity_id,
                                                    file_ctime=file_obj.ctime,
                                                    file_atime=file_obj.atime)
                        if combinations == "10110":
                            # ERROR: inode same but ctime changed
                            logging.warning("%s: Unhandled combination: %s: %s"
                                            % (self.__class__.__name__,
                                               combinations,
                                               file_obj.path, ))
                        if combinations == "10111":
                            # ERROR: inode same but ctime changed
                            logging.warning("%s: Unhandled combination: %s: %s"
                                            % (self.__class__.__name__,
                                               combinations,
                                               file_obj.path, ))
                        if combinations == "11000":
                            # OK: mtime, atime, size changed, rest same
                            logging.info("%s: OK: %s: %s"
                                         % (self.__class__.__name__,
                                            combinations,
                                            file_obj.path, ))
                            # BACKUP
                            if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                                (file_obj.sha512, )).fetchall()) == 0:
                                file_obj.backup()
                            # update DB
                            self._update_data_in_db(conn,
                                                    new_column_name,
                                                    entity_id=entity_id,
                                                    file_mtime=file_obj.mtime,
                                                    file_atime=file_obj.atime,
                                                    file_size=file_obj.size,
                                                    file_sha512=file_obj.sha512,
                                                    backup_archive_name=file_obj.current_backup_archive_name)
                        if combinations == "11001":
                            # OK: mtime and atime changed, rest same
                            logging.info("%s: OK: %s: %s"
                                         % (self.__class__.__name__,
                                            combinations,
                                            file_obj.path, ))
                            # BACKUP
                            if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                                (file_obj.sha512, )).fetchall()) == 0:
                                file_obj.backup()
                            # update DB
                            self._update_data_in_db(conn,
                                                    new_column_name,
                                                    entity_id=entity_id,
                                                    file_mtime=file_obj.mtime,
                                                    file_atime=file_obj.atime,
                                                    file_sha512=file_obj.sha512,
                                                    backup_archive_name=file_obj.current_backup_archive_name)
                        if combinations == "11010":
                            # OK: regular edit, mtime, size changed, rest same
                            logging.info("%s: OK: %s: %s"
                                         % (self.__class__.__name__,
                                            combinations,
                                            file_obj.path, ))
                            # BACKUP
                            if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                                (file_obj.sha512, )).fetchall()) == 0:
                                file_obj.backup()
                            # update DB
                            self._update_data_in_db(conn,
                                                    new_column_name,
                                                    entity_id=entity_id,
                                                    file_mtime=file_obj.mtime,
                                                    file_size=file_obj.size,
                                                    file_sha512=file_obj.sha512,
                                                    backup_archive_name=file_obj.current_backup_archive_name)
                        if combinations == "11011":
                            # OK: only mtime changed. size same
                            logging.info("%s: OK: %s: %s"
                                         % (self.__class__.__name__,
                                            combinations,
                                            file_obj.path, ))
                            # BACKUP
                            if len(conn.execute("SELECT sha512 FROM sha512_index WHERE sha512 = ?",
                                                (file_obj.sha512, )).fetchall()) == 0:
                                file_obj.backup()
                            # update DB
                            self._update_data_in_db(conn,
                                                    new_column_name,
                                                    entity_id=entity_id,
                                                    file_mtime=file_obj.mtime,
                                                    file_sha512=file_obj.sha512,
                                                    backup_archive_name=file_obj.current_backup_archive_name)
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
                            # update DB
                            self._update_data_in_db(conn,
                                                    new_column_name,
                                                    entity_id=entity_id)
                    if i % 1 == 0:
                        print("%i files/s" % (i / (time.time() - time_start - 0.001), ))
                    if i % 1000 == 0:
                        conn.commit()
                    i += 1
        conn.commit()
        conn.close()
        return True


class BackupFile(object):
    """ * """
    _backup_set = None
    _path = None
    _targets = None
    _target_archive_max_size = 1024 * 1024 * 12  # This is currently a soft-limit
    _sha512 = None
    _ctime = None
    _mtime = None
    _atime = None
    _inode = None
    _size = None
    _compression_level = 6
    _buffer_size = 1024 * 1024
    _key_hash_32 = None
    _tmp_dir = None
    _tmp_file_path = None
    _current_backup_archive_name = None

    def __init__(self, backup_set, file_path, targets, tmp_dir, key_hash_32):
        """ * """
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

    def __del__(self):
        """ * """
        self._remove_tmp_file()

    @property
    def path(self):
        return self._path

    @property
    def ctime(self):
        return self._ctime

    @property
    def mtime(self):
        return self._mtime

    @property
    def atime(self):
        return self._atime

    @property
    def inode(self):
        return self._inode

    @property
    def size(self):
        return self._size

    @property
    def sha512(self):
        if self._sha512:
            return self._sha512
        else:
            self._sha512 = bs.utils.HashFile(self._path).start()
            return self._sha512

    @property
    def current_backup_archive_name(self):
        """ * """
        if self._current_backup_archive_name:
            return self._current_backup_archive_name
        else:
            # ABSTRACT
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
            # if latest archive found and size below threshold, use this latest
            # archive
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
            # if no archive found at all or latest found archive exceeds size
            # threshold:
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

    def backup(self):
        """ * """
        self._compress_zlib_encrypt_aes()

    def _remove_tmp_file(self):
        """ * """
        try:
            os.unlink(self._tmp_file_path)
            return True
        except:
            return False

    def _compress_zlib_encrypt_aes(self):
        """ * """
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
        aes = Crypto.Cipher.AES.new(self._key_hash_32,
                                    Crypto.Cipher.AES.MODE_CTR, iv, counter)

        f_out.write(iv)
#        data_processed = 0
        while True:
            data = f_in.read(self._buffer_size)
            if not data:
                break
            data_compressed_unencrypted = compression_obj.compress(data)
            data_compressed_unencrypted += compression_obj.flush(zlib.Z_SYNC_FLUSH)
            data_compressed_encrypted = aes.encrypt(data_compressed_unencrypted)
            f_out.write(data_compressed_encrypted)

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
                logging.debug("%s: Successfully added to target archive(s) "\
                              "(%.2fs)."
                              % (self.__class__.__name__,
                                 time_elapsed))
            else:
                logging.warning("%s: The backup file already exists in the "\
                                "current archive file: %s"
                                % (self.__class__.__name__,
                                   self.sha512))


class BackupRestore(object):
    """ * """
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
        if not self._key_hash_32:
            while not self._key_hash_32:
                key_raw = getpass.getpass("This set is encrypted; please "\
                                          "enter the corresponding password:")
                key_hash_64 = hashlib.sha512(key_raw.encode()).hexdigest()
                # verify hash_64
                if key_hash_64 == self._set_obj.key_hash_64:
                    key_hash_32 = hashlib.sha256(key_raw.encode()).digest()
                    self._key_hash_32 = key_hash_32
                    return self._key_hash_32

    def start(self):
        """ * """
        for entity_id in self._entity_ids:
            # restore-file obj, provides all necessary metadata about entity
            backup_restore_file = BackupRestoreFile(self._set_obj,
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


class BackupRestoreFile(object):
    """ * """
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
        """ *
        Returns a list of all available backup archive paths.
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
        if not self._sha512_db:
            self._sha512_db = self.get_latest_data_in_table("sha512")
        return self._sha512_db

    @property
    def backup_archive_name(self):
        """ * """
        if not self._backup_archive_name:
            conn = sqlite3.connect(self._set_obj.set_db_path)
            res = conn.execute("SELECT backup_archive_name FROM sha512_index WHERE sha512 = ?",
                               (str(self.sha512_db), )).fetchall()
            self._backup_archive_name = res[0][0]
            conn.close()
        return self._backup_archive_name

    @property
    def file_path(self):
        """ * """
        if not self._file_name:
            conn = sqlite3.connect(self._set_obj.set_db_path)
            res = conn.execute("SELECT path FROM path WHERE id = ?",
                               (self._entity_id, )).fetchall()
            self._file_name = res[0][0]
            conn.close()
        return self._file_name

    def get_latest_data_in_table(self, table_name):
        """ *
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
