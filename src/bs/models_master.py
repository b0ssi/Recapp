# -*- coding: utf-8 -*-

###############################################################################
##    models_master                                                          ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Mar 16, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################

import bs.config
import bs.messages.database
import inspect
import logging
import re
import sqlite3


class BSModel(object):
    def __init__(self):
        super(BSModel, self).__init__()

    def _get_class_attributes(self):
        """
        Get public attributes of class (for API, sub-classed by objects to
        access database points)
        """
        out = []
        for attribute_name, attribute_object in inspect.getmembers(self):
            if not attribute_name[:1] == "_" and \
                isinstance(attribute_object, list):
                out.append([attribute_name, attribute_object])
        return out

    def _get_model_superclass(self):
        """
        Returns the Model superclass (meant to be directly subclassed by
        this BSModel).
        """
        self.__class__.__name__.lower()
        model_object = self.__class__
        while model_object.__bases__[0].__name__ != "BSModel" and \
            model_object.__bases__[0].__name__ != "object":
            model_object = model_object.__bases__[0]
        if model_object.__bases__[0].__name__ == "object":
            model_object = False
        return model_object

    def add(self, columns, datasets):
        # validate data
        if isinstance(columns, str) and \
            isinstance(datasets, (list, tuple, )):
            pass
        else:
            logging.critical("The method requires two attributes in the "\
                             "following format: '<string>, ...>' '[[<value>, ...], ...]'")
            raise SystemExit()
        logging.info("Saving data to database...")
        # check that
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        try:
            db_table_name = self._get_model_superclass().__name__.lower()
            conn.executemany("INSERT INTO %s (%s) VALUES (%s)" % (db_table_name, columns, str("?, " * len(datasets[0]))[:-2], ), datasets)
            logging.info("Data successfully saved to database.")
            conn.commit()
        except sqlite3.IntegrityError as e:
            logging.critical("A database integrity-error occurred, the object"\
                             " could only be partially saved: '%s'" % e)
            raise SystemExit()
        except sqlite3.OperationalError as e:
            logging.critical("A database operation-error occurred, the object"\
                             " could only be partially saved: '%s'" % e)
        except sqlite3.ProgrammingError as e:
            logging.critical("A database programming-error occurred, the "\
                             "object could only be partially saved: '%s'" % e)
        except Exception as e:
            logging.critical(messages.database.access_denied(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(messages.database.access_denied(bs.config.CONFIGDB_PATH, e)[1])
        conn.close()

    def get(self, columns, conditions=""):
        """
        Load dataset from `columns` in associated table under
        selection-conditions `conditions`, `conds_neg`.
        """
        # validate arguments
        # columns
        # allowed: a-z0-9_
        # first character only: _a-z
        # at least 4 characters
        if not re.search(bs.config.VALID_NAME_ATTRIBUTE_COLUMN_PATTERN, str(columns)) \
            and columns != "*":
            logging.critical("Argument 'columns' has invalid data. It needs "
                "to start with a Latin lowercase character (a-z), can only "\
                "contain alpha-numeric characters plus `_` and needs "\
                "to have a length between 2 and 32 characters.")
            raise SystemExit()
        # conditions
        if not re.search("(.*)", str(conditions)) \
            and conditions != "":
            logging.critical("Argument 'conditions' has invalid data. It needs "\
                             " to be a tuple of tuples that contain three values: "\
                             "<columnName><operator><value>, where <operator> E "\
                             "(!=, =, >, <).")
            raise SystemExit()

        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        try:
            logging.info("Loading data from columns '%s' with conditions "\
                         "\"%s\"..." % (columns, conditions, ))
            # build conditions
            conditions_sql = ""
            conditions_parameters = []
            if conditions != "":
                conditions_sql = " WHERE "
                for condition in conditions:
                    conditions_sql += "%s %s ? AND " % (condition[0], condition[1], )
                    conditions_parameters.append(condition[2])
                conditions_sql = conditions_sql[:-5]
            # execute SQL call
            table_name = self._get_model_superclass().__name__.lower()
            res = conn.execute("SELECT %s FROM %s%s" % (columns, table_name, conditions_sql, ), tuple(conditions_parameters)).fetchall()
            logging.info("Data from columns '%s' with conditions \"%s\" "\
                         "successfully loaded from database."
                         % (columns, conditions, ))
            return res
        except Exception as e:
            logging.critical(messages.database.access_denied(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(messages.database.access_denied(bs.config.CONFIGDB_PATH, e)[1])

        conn.commit()
        conn.close()

    def remove(self, conditions=""):
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        try:
            logging.info("Removing data with conditions \"%s\"..."
                         % (conditions, ))
            # build conditions
            conditions_sql = ""
            conditions_parameters = []
            if conditions != "":
                conditions_sql = " WHERE "
                for condition in conditions:
                    conditions_sql += "%s %s ? AND " % (condition[0], condition[1], )
                    conditions_parameters.append(condition[2])
                conditions_sql = conditions_sql[:-5]
            # execute SQL call
            table_name = self._get_model_superclass().__name__.lower()
            res = conn.execute("DELETE FROM %s%s" % (table_name, conditions_sql, ), tuple(conditions_parameters)).fetchall()
            logging.info("Data with conditions \"%s\" successfully deleted "\
                         "from database." % (conditions, ))
            conn.commit()
            return res
        except Exception as e:
            logging.critical(messages.database.access_denied(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(messages.database.access_denied(bs.config.CONFIGDB_PATH, e)[1])

        conn.commit()
        conn.close()
