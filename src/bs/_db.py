# -*- coding: utf-8 -*-

###############################################################################
##    _db                                                                    ##
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
import bs.models
import inspect
import logging
import random
import re
import sqlite3
import time


class SyncDb(object):
    # scan models modules and extract structural
    def __init__(self):
        pass

    @property
    def schema_datas(self, models_module=bs.models):
        out = {}
        for member_name, member_object in sorted(inspect.getmembers(models_module), key=lambda x: x[0]):
            if inspect.isclass(member_object):
                class_attributes = {}
                for class_attribute_name, class_attribute_value in inspect.getmembers(member_object):
                    if re.search(bs.config.VALID_NAME_ATTRIBUTE_COLUMN_PATTERN, class_attribute_name):
                        # filter through different attribute types in model
                        # lists (regular attributes
                        if isinstance(class_attribute_value, list):
                            # change strings like "PRIMARY KEY" -> 1
                            if len(class_attribute_value) > 1:
                                if class_attribute_value[1] == "PRIMARY KEY":
                                    class_attribute_value[1] = 1
                                if class_attribute_value[1] == "UNIQUE":
                                    class_attribute_value[1] = 2
                            else:
                                class_attribute_value.append(0)
                            class_attributes[class_attribute_name.lower()] = class_attribute_value
                        # any future types...
                out[member_name.lower()] = class_attributes
        return out

    @schema_datas.setter
    def schema_datas(self):
        return False

    @property
    def db_datas(self):
#        {table: {column: datatype, column: datatype}, ... }
        out = {}
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        db_table_names = [x[0] for x in conn.execute("SELECT `name` FROM `sqlite_master` WHERE type='table'").fetchall()]
        for db_table_name in db_table_names:
            db_table_datas_raw = conn.execute("PRAGMA table_info (%s)" % (db_table_name,)).fetchall()
            db_table_data_formatted = {}
            for db_table_data_raw in db_table_datas_raw:
                db_column_name = db_table_data_raw[1]
                db_data_type = db_table_data_raw[2]
                # check for PRIMARY KEY
                db_constraint = db_table_data_raw[5]
                # check for UNIQUE
                if db_constraint == 0:
                    db_unique_index_names = [x[1] for x in conn.execute("PRAGMA index_list ('%s')" % (db_table_name, )).fetchall()]
                    db_unique_index_columns = []
                    for db_unique_index_name in db_unique_index_names:
                        db_unique_index_columns.append(conn.execute("PRAGMA index_info (%s)" % (db_unique_index_name, )).fetchall()[0][2])
                    if db_column_name in db_unique_index_columns:
                        db_constraint = 2

                db_table_data_formatted[db_column_name] = [db_data_type, db_constraint]
            out[db_table_name] = db_table_data_formatted
        conn.close()
        return out

    @db_datas.setter
    def db_datas(self):
        return False

    def sync(self, execute=True):
        compact_db = False
        # verifying that schema-data is true...
        if self._verify_schema():

            if self._create_missing_tables(execute): compact_db = True
            if self._delete_foster_tables(execute): compact_db = True
            if self._detect_inconsistency(execute): compact_db = True

            # compact db if necessary
            if compact_db:
                logging.info("Compacting database...")
                timer_start = time.clock()
                conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                conn.execute("VACUUM")
                conn.commit()
                conn.close
                logging.info("Compacting successful (%.2f sec)." % (time.clock() - timer_start, ))

    def _verify_schema(self, models_module=bs.models):
        """
        Checks schema-data for its validity
        """
        for member_name, member_object in sorted(inspect.getmembers(models_module), key=lambda x: x[0]):
            if inspect.isclass(member_object):
                # validate class name
                # allowed: a-z0-9_
                # first character only: _a-z
                # 4-32 characters
                if not re.search(bs.config.VALID_NAME_MODEL_TABLE_PATTERN, member_name):
                    logging.critical("Model '%s' has an invalid name. It needs "
                "to start with a Latin lowercase character (a-z), can only "\
                "contain alpha-numeric characters plus `_` and needs "\
                "to have a length between 2 and 32 characters." % (member_name, ))
                    raise SystemExit()
                class_attributes = [[x[0], x[1]] for x in inspect.getmembers(member_object) \
                                    if isinstance(x[1], list) and \
                                    re.search(bs.config.VALID_NAME_ATTRIBUTE_COLUMN_PATTERN, x[0])]
                if len(class_attributes) == 0:
                    logging.critical("The model '%s' needs to have at least "\
                                     "one attribute with a valid name." % (member_name, ))
                    raise SystemExit()
                for class_attribute_name, class_attribute_value in class_attributes:
                    # iterate over all class-attributes here
                    if isinstance(class_attribute_value, list):
                        # data type
                        allowed_values_types = ("NULL", "INTEGER", "REAL", "TEXT", "BLOB")
                        if class_attribute_value[0] not in allowed_values_types:
                            logging.critical("The attribute '%s' in model '%s' has an invalid defined data-type, aborting: '%s'" % (class_attribute_name, member_name, class_attribute_value[0]))
                            return False
                        allowed_values_constraints = ((("NULL", "INTEGER", "REAL", "TEXT", "BLOB", ), "UNIQUE", ), (("INTEGER", ), "PRIMARY KEY", ), )
                        # column-constraint
                        #
                        # this basically checks, that, if constraint is in
                        # any of the 2-typles in allowed_values_constraints
                        # on pos 2, its type is in the corresponding tuple
                        # on position 1.
                        # (((<tupleOfAllowedTypesForConstraint>), <constraintL, ), ...)
                        if len(class_attribute_value) > 1:
                            if class_attribute_value[1] not in [x[1] for x in allowed_values_constraints] or \
                                class_attribute_value[0] not in [x[0] for x in allowed_values_constraints if x[1] == class_attribute_value[1]][0]:
                                logging.critical("The attribute '%s' in model '%s' has an invalid constraint defined (for data-type '%s'), aborting: '%s'" % (class_attribute_name, member_name, class_attribute_value[0], class_attribute_value[1]))
                                return False
                        # all good, proceed
        return True

    def _create_missing_tables(self, execute):
        """
        Create tables that exist in the schema but not in the database.
        """
        action_taken = False
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        schema_table_names = sorted(self.schema_datas.keys(), key=lambda x: x[0])
        db_table_names = sorted(self.db_datas.keys(), key=lambda x: x[0])
        out = ""
        for schema_table_name in schema_table_names:
            if schema_table_name not in db_table_names:
                out += "CREATE TABLE IF NOT EXISTS %s\n\t(\n" % (schema_table_name,)
                schema_column_names = sorted(self.schema_datas[schema_table_name].keys(), key=lambda x: x[0])
                i = 0
                for schema_column_name in schema_column_names:
                    schema_data_type = self.schema_datas[schema_table_name][schema_column_name][0]
                    schema_constraint = self.schema_datas[schema_table_name][schema_column_name][1]
                    if schema_constraint == 1:
                        schema_constraint = " PRIMARY KEY"
                    elif schema_constraint == 2:
                        schema_constraint = " UNIQUE"
                    else:
                        schema_constraint = ""
                    out += "\t%s %s%s" % (schema_column_name, schema_data_type, schema_constraint)
                    if i == len(schema_column_names) - 1:
                        out += "\n"
                    else:
                        out += ",\n"
                    i += 1
                out += "\t)\n\n"
                # commit
                conn.execute(out)
                conn.commit()
                logging.info("Created missing table: '%s'." % (schema_table_name, ))
                out = ""
                action_taken = True
        conn.close()
        # return
        if action_taken: return True
        else: return False

    def _delete_foster_tables(self, execute):
        """
        Delete tables that (still) exist in the database but not in the schema.
        """
        action_taken = False
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        out = ""
        db_table_names = sorted(self.db_datas.keys(), key=lambda x: x[0])
        schema_table_names = sorted(self.schema_datas.keys(), key=lambda x: x[0])
        for db_table_name in db_table_names:
            if db_table_name not in schema_table_names:
                out += "DROP TABLE IF EXISTS `%s`" % db_table_name
                # commit
                conn.execute(out)
                conn.commit()
                logging.info("Deleted foster-table from database: '%s'." % (db_table_name, ))
                out = ""
                action_taken = True
        conn.close()
        # return
        if action_taken: return True
        else: return False

    def _detect_inconsistency(self, execute):
        """
        Checks db for
        - any difference in column names or -counts between db <-> schema
        - column specifications and data types that have changed
        and rebuild whole table incl. data as SQLite does not support changing
        these attributes subsequently.
        """
        action_taken = False
        # look for foster columns and inconsistent column specifications
        db_table_names = sorted(self.db_datas.keys(), key=lambda x: x[0])
        for db_table_name in db_table_names:
            db_column_names = sorted(self.db_datas[db_table_name].keys(), key=lambda x: x[0])
            schema_column_names = sorted(self.schema_datas[db_table_name].keys(), key=lambda x: x[0])
            # if column-structure between db, schema is inconsistent
            if len(schema_column_names) != len([x for x in db_column_names if x in schema_column_names]) or len(schema_column_names) != len(db_column_names):
                logging.debug("Columns have changed:\n\t\tdb_column_names:\t%s\n\t\tschema_column_names:\t%s" % (db_column_names, schema_column_names, ))
                logging.info("Inconsistency in table structure found, rewriting the table...")
                self._rebuild_table(execute, db_table_name)
                action_taken = True
            # if column-structure is consistent, look deeper: type/definitions
            else:
                for db_column_name in db_column_names:
                    # check if it exists in schema
                    if db_column_name in schema_column_names:
                    # if exists in schema
                        db_column_data_type = self.db_datas[db_table_name][db_column_name][0]
                        db_column_primary_key = self.db_datas[db_table_name][db_column_name][1]
                        schema_column_data_type = self.schema_datas[db_table_name][db_column_name][0]
                        schema_column_primary_key = self.schema_datas[db_table_name][db_column_name][1]
                        # check if specifications are consistent with schema
                        # if specifications are inconsistent
                        if db_column_data_type != schema_column_data_type or \
                            db_column_primary_key != schema_column_primary_key:
                            # rebuild table
                            logging.debug("Column '%s' (and possibly others) has a changed data-type and/or specification." % (db_column_name, ))
                            logging.info("Inconsistency in table structure found, rewriting the table...")
                            action_taken = True
                            self._rebuild_table(execute, db_table_name)
                            break
                        # if specifications are consistent
                        else:
                            # all good.
                            pass
        # return
        if action_taken: return True
        else: return False

    def _rebuild_table(self, execute, db_table_name_to_rebuild):
        """
        Rebuilds the specified table.
        """
        # A) create new db from new schema
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        db_table_names = sorted(self.db_datas.keys(), key=lambda x: x[0])
        db_table_name_temp = ""
        while db_table_name_temp in db_table_names or db_table_name_temp == "":
            db_table_name_temp = "_%s" % str(random.randint(1000000000000, 9999999999999))
        # get column+definitions string for CREATE TABLE...
        db_columns_to_creat_sql = ""
        schema_column_names = sorted(self.schema_datas[db_table_name_to_rebuild].keys(), key=lambda x: x[0])
        for schema_column_name in schema_column_names:
            schema_column_data = self.schema_datas[db_table_name_to_rebuild][schema_column_name]
            if schema_column_data[1] == 1:
                schema_column_data[1] = " PRIMARY KEY"
            elif schema_column_data[1] == 2:
                schema_column_data[1] = " UNIQUE"
            else:
                schema_column_data[1] = ""
            db_columns_to_creat_sql += "%s %s%s, " % (schema_column_name, schema_column_data[0], schema_column_data[1])
        db_columns_to_creat_sql = "(%s)" % (db_columns_to_creat_sql[:-2],)
        conn.execute("CREATE TABLE IF NOT EXISTS '%s' %s" % (db_table_name_temp, db_columns_to_creat_sql))
        conn.commit()
        conn.close()
        # B) run through old table and copying data for all columns that are
        # still present in new db over
        db_column_names = sorted(self.db_datas[db_table_name_to_rebuild].keys(), key=lambda x: x[0])
        # for all columns in old db table that still exist in new table/schema
        db_columns_to_transfer = []
        for db_column_name in db_column_names:
            if db_column_name in schema_column_names:
                db_columns_to_transfer.append(db_column_name)
            # for all columns that are *not* brought over into new table/schema
            else:
                logging.info("Column '%s' has been removed from database "\
                                "alongside all of its associated data."
                                % (db_column_name,))
        # prints something like "str1, str2, str3" (minus quot. marks)
        db_columns_to_transfer_formatted = (str("%s, " * len(db_columns_to_transfer)) % tuple(db_columns_to_transfer))[:-2]
        logging.info("Rewriting table '%s'..." % (db_table_name_to_rebuild))
        timer_start = time.clock()
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        # only transfer data IF there actually is a column to transfer...
        if len(db_columns_to_transfer) > 0:
            res = conn.execute("SELECT %s FROM %s" % (db_columns_to_transfer_formatted, db_table_name_to_rebuild)).fetchall()
            conn.executemany("INSERT INTO %s (%s) VALUES (%s)" % (db_table_name_temp, db_columns_to_transfer_formatted, str("?, " * len(db_columns_to_transfer))[:-2], ), res)
            conn.commit()
        logging.info("Table '%s' has been successfully rewritten (%.2f sec)." % (db_table_name_to_rebuild, time.clock() - timer_start,))
        # D) drop old table & rename new table to orig name
        conn.execute("DROP TABLE %s" % (db_table_name_to_rebuild, ))
        conn.commit()
        conn.execute("ALTER TABLE %s RENAME TO %s" % (db_table_name_temp, db_table_name_to_rebuild, ))
        conn.commit()
        conn.close()
        return True
