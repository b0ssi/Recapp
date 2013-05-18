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

""" * """

import bs.config
import bs.messages.database
import importlib
import inspect
import logging
import random
import re
import sqlite3
import time


class SyncDb(object):
    _models_module = None

    """
    Synchronizes schema-structure with db-structure.
    `schema_module_path` is the module-path to the module to use relative to
    the `PYTHONPATH`
    """
    # scan models modules and extract structural
    def __init__(self, schema_module_path):
        try:
            self._models_module = importlib.import_module(str(schema_module_path))
        except SyntaxError as e:
            logging.critical("The models schema contains errors, %s needs to "\
                             "quit: %s" % (bs.config.PROJECT_NAME, e))
            raise SystemExit()

    @property
    def _schema_datas(self):
        """
        Scans all classes in the passed models_module and returns data in the
        following format:
        ["<classname>": ["<attributename>": [<attributevalues>], ...], ...],
        where <attributename> would be only a custom attribute (none of the
        built-in and/or inherited attributes such as "__doc__")
        and <attributevalues> would always have to be a (2)-list.
        """
        out = {}
        for member_name, member_object in sorted(inspect.getmembers(self._models_module),
                                                                    key=lambda x: x[0]):
            if inspect.isclass(member_object):
                class_attributes = {}
                for class_attribute_name, class_attribute_value in inspect.getmembers(member_object):
                    if re.search(bs.config.REGEX_PATTERN_COLUMN, class_attribute_name):
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

    @property
    def _db_datas(self):
        """
        Calls db metadata and returns it in a multi-dimensional dictionary:
        {table: {column: datatype, column: datatype}, ... }
        """
        try:
            out = {}
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            sql_call = "SELECT `name` FROM `sqlite_master` WHERE type='table'"
            db_table_names = [x[0] for x in conn.execute(sql_call).fetchall()]
            for db_table_name in db_table_names:
                db_table_datas_raw = conn.execute("PRAGMA table_info (%s)"
                                                  % (db_table_name,)).fetchall()
                db_table_data_formatted = {}
                for db_table_data_raw in db_table_datas_raw:
                    db_column_name = db_table_data_raw[1]
                    db_data_type = db_table_data_raw[2]
                    # check for PRIMARY KEY
                    db_constraint = db_table_data_raw[5]
                    # check for UNIQUE
                    if db_constraint == 0:
                        db_unique_index_names = [x[1] for x in conn.execute("PRAGMA index_list ('%s')"
                                                                            % (db_table_name, )
                                                                            ).fetchall()]
                        db_unique_index_columns = []
                        for db_unique_index_name in db_unique_index_names:
                            db_unique_index_columns.append(conn.execute("PRAGMA index_info (%s)"
                                                                        % (db_unique_index_name, )
                                                                        ).fetchall()[0][2])
                        if db_column_name in db_unique_index_columns:
                            db_constraint = 2
                    db_table_data_formatted[db_column_name] = [db_data_type,
                                                               db_constraint]
                out[db_table_name] = db_table_data_formatted
            conn.close()
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])
        return out

    def sync(self, execute=True):
        """ Just add description """
        logging.info("## Synchronizing database-structure with Schema... #############")
        compact_db = False
        # verifying that schema-data is true...
        if self._verify_schema():

            if self._create_missing_tables(execute):
                compact_db = True
            if self._delete_foster_tables(execute):
                compact_db = True
            if self._detect_inconsistency(execute):
                compact_db = True

            # compact db if necessary
            if compact_db:
                logging.info("Compacting database...")
                timer_start = time.clock()
                conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                conn.execute("VACUUM")
                conn.commit()
                conn.close
                logging.info("Compacting successful (%.2f sec)."
                             % (time.clock() - timer_start, ))
        logging.info("## Synchronization successfully completed. #####################")

    def _verify_schema(self):
        """
        Checks schema-data for its validity. Raises exception if any issues
        exist, True if verification passess the test.
        """
        logging.info("Validating schema...")
        # warning trigger if no class has been found in module
        out_no_class_found = True
        # run through *all* members in module
        members = sorted(inspect.getmembers(self._models_module),
                         key=lambda x: x[0])
        for member_name, member_object in members:
            # filter members down to classes
            if inspect.isclass(member_object):
                out_no_class_found = False
                # validate class name
                # allowed: a-zA-Z0-9_
                # first character only: _a-zA-Z
                # 4-32 characters
                if not re.search(bs.config.REGEX_PATTERN_TABLE,
                                 member_name):
                    logging.critical("The model '%s' has an invalid name. It "\
                                     "needs to start with a Latin lower-case "\
                                     "character (a-z, A-Z), can only contain "\
                                     "alpha-numeric characters plus `_` and "\
                                     "needs to have a length between 2 and "\
                                     "32 characters." % (member_name, ))
                    raise SystemExit()
                # create list of valid attributes
                # checks validity of attribute value (list with 2 <= n <= 4 attr)
                # checks validity of attribute name
                class_attributes = [[x[0], x[1]] for x in inspect.getmembers(member_object) \
                                    if re.search(bs.config.REGEX_PATTERN_COLUMN, x[0]) and \
                                    isinstance(x[1], list) and \
                                    1 <= len(x[1]) <= 2]
                # if no valid attributes were found
                if len(class_attributes) == 0:
                    logging.critical("The model '%s' needs to have at least "\
                                     "one attribute with valid name and value."
                                     % (member_name, ))
                    raise SystemExit()
                # run through valid attributes
                for class_attribute_name, class_attribute_value in class_attributes:
                    # validate attribute value
                    allowed_values_types = ("NULL",
                                            "INTEGER",
                                            "REAL",
                                            "TEXT",
                                            "BLOB",
                                            )
                    if class_attribute_value[0] not in allowed_values_types:
                        logging.critical("The attribute '%s' on model '%s' "\
                                         "has an invalid defined data-type, "\
                                         "aborting: '%s'"
                                         % (class_attribute_name,
                                            member_name,
                                            class_attribute_value[0],
                                            )
                                         )
                        raise SystemExit()
                    # column-constraint
                    #
                    # this basically checks, that, if constraint is in
                    # any of the 2-typles in allowed_values_constraints
                    # on pos 2, its type is in the corresponding tuple
                    # on position 1.
                    # (((<tupleOfAllowedTypesForConstraint>), <constraintL, ), ...)
                    allowed_values_constraints = ((("NULL", "INTEGER", "REAL", "TEXT", "BLOB", ), "UNIQUE", ),
                                                  (("INTEGER", ), "PRIMARY KEY", ),
                                                  )
                    if len(class_attribute_value) > 1:
                        if class_attribute_value[1] not in [x[1] for x in allowed_values_constraints] or \
                            class_attribute_value[0] not in [x[0] for x in allowed_values_constraints if x[1] == class_attribute_value[1]][0]:
                            logging.critical("The attribute '%s' on model "\
                                             "'%s' has an invalid constraint "\
                                             "defined (for data-type '%s'), "\
                                             "aborting: '%s'"
                                             % (class_attribute_name,
                                                member_name,
                                                class_attribute_value[0],
                                                class_attribute_value[1],
                                                )
                                             )
                            raise SystemExit()
                    # all good, proceed
        # if no valid class has been found, output warning
        if out_no_class_found:
            logging.warning("No class has been found in the schema; database "\
                            "will be rendered empty.")
        logging.info("Schema successfully validated.")
        return True

    def _create_missing_tables(self, execute):
        """
        Creates all tables that exist in the schema but not in the database.
        """
        # ABSTRACT #####################
        ################################
        # if schema_table not in db_tables
        #    create if exists
        # else
        #    continue

        # activity trigger
        activity_trigger = False
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        schema_table_names = sorted(self._schema_datas.keys(),
                                    key=lambda x: x[0])
        db_table_names = sorted(self._db_datas.keys(), key=lambda x: x[0])
        # run through schema and compare with db status quo
        for schema_table_name in schema_table_names:
            # if inconsistency detected... 
            if schema_table_name not in db_table_names:
                # ...compile SQL instructions
                out = "CREATE TABLE IF NOT EXISTS %s\n\t(\n" % (schema_table_name,)
                schema_column_names = sorted(self._schema_datas[schema_table_name].keys(),
                                             key=lambda x: x[0])
                for schema_column_name in schema_column_names:
                    schema_data_type = self._schema_datas[schema_table_name][schema_column_name][0]
                    schema_constraint = self._schema_datas[schema_table_name][schema_column_name][1]
                    if schema_constraint == 1:
                        schema_constraint = " PRIMARY KEY"
                    elif schema_constraint == 2:
                        schema_constraint = " UNIQUE"
                    else:
                        schema_constraint = ""
                    out += "\t%s %s%s" % (schema_column_name, schema_data_type,
                                          schema_constraint)
                    if schema_column_name == schema_column_names[-1]:
                        out += "\n"
                    else:
                        out += ",\n"
                out += "\t)\n\n"
                # commit
                try:
                    logging.info("Adding table '%s' to database..."
                                 % (schema_table_name, ))
                    conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                    conn.execute(out)
                    conn.commit()
                    conn.close()
                    action_taken = True
                    logging.info("Table '%s' successfully added to database."
                                 % (schema_table_name, ))
                    activity_trigger = True
                except Exception as e:
                    logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
                    raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])
        if activity_trigger:
            return True
        else:
            return False

    def _delete_foster_tables(self, execute):
        """
        Delete tables that exist in the database but not in the schema.
        """
        activity_trigger = False
        db_table_names = sorted(self._db_datas.keys(), key=lambda x: x[0])
        schema_table_names = sorted(self._schema_datas.keys(),
                                    key=lambda x: x[0])
        for db_table_name in db_table_names:
            if db_table_name not in schema_table_names:
                out = "DROP TABLE IF EXISTS `%s`" % db_table_name
                # commit
                try:
                    logging.info("Removing table '%s' from database..."
                                 % (db_table_name, ))
                    conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
                    conn.execute(out)
                    conn.commit()
                    conn.close()
                    logging.info("Table '%s' successfully removed from database."
                                 % (db_table_name, ))
                    activity_trigger = True
                except Exception as e:
                    logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
                    raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])
        if activity_trigger:
            return True
        else:
            return False

    def _detect_inconsistency(self, execute):
        """
        Checks db for
        - any inconsistency in existing columns between db <-> schema
        - any inconsistency in column specifications and data types between
          db <-> schema
        and call self.rebuild_table to rebuild the whole table incl. data as
        SQLite does not support changing these attributes subsequently.
        """
        activity_trigger = False
        # look for foster columns and inconsistent column specifications
        db_table_names = sorted(self._db_datas.keys(), key=lambda x: x[0])
        for db_table_name in db_table_names:
            db_column_names = sorted(self._db_datas[db_table_name].keys(),
                                     key=lambda x: x[0])
            schema_column_names = sorted(self._schema_datas[db_table_name].keys(),
                                         key=lambda x: x[0])
            # if inconsistency detected between column- and db-structure...
            if len(schema_column_names) != len([x for x in db_column_names if x in schema_column_names]) or \
                len(schema_column_names) != len(db_column_names):

                logging.debug("Columns have changed:\n"\
                              "\t\tdb_column_names:\t%s\n"\
                              "\t\tschema_column_names:\t%s"
                              % (db_column_names, schema_column_names, ))
                logging.info("Structural inconsistency in table '%s' detected, rewriting..."
                             % (db_table_name, ))
                self._rebuild_table(execute, db_table_name)
                activity_trigger = True
            # if no inconsistency detected, look deeper: type/definitions
            else:
                for db_column_name in db_column_names:
                    # check if it exists in schema
                    if db_column_name in schema_column_names:
                        db_column_data_type = self._db_datas[db_table_name][db_column_name][0]
                        db_column_primary_key = self._db_datas[db_table_name][db_column_name][1]
                        schema_column_data_type = self._schema_datas[db_table_name][db_column_name][0]
                        schema_column_primary_key = self._schema_datas[db_table_name][db_column_name][1]
                        # if specifications are inconsistent between schame/db
                        if db_column_data_type != schema_column_data_type or \
                            db_column_primary_key != schema_column_primary_key:
                            # rebuild table
                            logging.debug("Inconsistency in column '%s', "\
                                          "table '%s' (and possibly other "\
                                          "columns) detected: Data-type "\
                                          "and/or specifications have changed."
                                          % (db_column_name, db_table_name, ))
                            logging.info("Structural inconsistency in table "\
                                         "'%s' detected, rewriting..."
                                         % (db_table_name, ))
                            self._rebuild_table(execute, db_table_name)
                            activity_trigger = True
                            break
                        # if specifications are consistent
                        else:
                            # all good.
                            pass
        if activity_trigger:
            return True
        else:
            return False

    def _rebuild_table(self, execute, db_table_name_to_rebuild):
        """
        Rebuilds the specified table including all of its data. Adds any
        columns that have changed and updates data-types/
        specifications if they have changed in the schema.
        """
        # A) create temporary db from (changed) schema
        db_table_names = sorted(self._db_datas.keys(), key=lambda x: x[0])
        db_table_name_temp = ""
        while db_table_name_temp in db_table_names or db_table_name_temp == "":
            db_table_name_temp = "_%s" % str(random.randint(1000000000000,
                                                            9999999999999))
        # get column+definitions string for CREATE TABLE...
        db_columns_to_creat_sql = ""
        schema_column_names = sorted(self._schema_datas[db_table_name_to_rebuild].keys(),
                                     key=lambda x: x[0])
        for schema_column_name in schema_column_names:
            schema_column_data = self._schema_datas[db_table_name_to_rebuild][schema_column_name]
            if schema_column_data[1] == 1:
                schema_column_data[1] = " PRIMARY KEY"
            elif schema_column_data[1] == 2:
                schema_column_data[1] = " UNIQUE"
            else:
                schema_column_data[1] = ""
            db_columns_to_creat_sql += "%s %s%s, " % (schema_column_name,
                                                      schema_column_data[0],
                                                      schema_column_data[1])
        db_columns_to_creat_sql = "(%s)" % (db_columns_to_creat_sql[:-2],)
        try:
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            conn.execute("CREATE TABLE IF NOT EXISTS '%s' %s"
                         % (db_table_name_temp, db_columns_to_creat_sql))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])
        # B) run through old table and copy data from columns still in schema/
        # new db over
        db_column_names = sorted(self._db_datas[db_table_name_to_rebuild].keys(),
                                 key=lambda x: x[0])
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
        db_columns_to_transfer_formatted = (str("%s, " * len(db_columns_to_transfer))
                                            % tuple(db_columns_to_transfer))[:-2]
        logging.info("Rewriting table '%s'..." % (db_table_name_to_rebuild))
        timer_start = time.clock()
        # only transfer data IF there actually is a column to transfer...
        try:
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            if len(db_columns_to_transfer) > 0:
                res = conn.execute("SELECT %s FROM %s"
                                   % (db_columns_to_transfer_formatted,
                                      db_table_name_to_rebuild)).fetchall()
                conn.executemany("INSERT INTO %s (%s) VALUES (%s)"
                                 % (db_table_name_temp,
                                    db_columns_to_transfer_formatted,
                                    str("?, " * len(db_columns_to_transfer))[:-2], ),
                                 res)
                conn.commit()
            # D) drop old table & rename new table to orig name
            conn.execute("DROP TABLE %s" % (db_table_name_to_rebuild, ))
            conn.commit()
            conn.execute("ALTER TABLE %s RENAME TO %s"
                         % (db_table_name_temp, db_table_name_to_rebuild, ))
            conn.commit()
            conn.close()
            logging.info("Table '%s' has been successfully rewritten "\
                         "(%.2f sec)."
                         % (db_table_name_to_rebuild,
                            time.clock() - timer_start,))
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])
        return True
