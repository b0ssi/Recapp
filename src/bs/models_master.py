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
        Gets public attributes of class (for API, sub-classed by objects to
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
        model_object = self.__class__
        while model_object.__bases__[0].__name__ != "BSModel" and \
            model_object.__bases__[0].__name__ != "object":
            model_object = model_object.__bases__[0]
        if model_object.__bases__[0].__name__ == "object":
            model_object = False
        return model_object

    def add(self, columns, datasets):
        """
        Adds a single or multiple data-sets to the object's database-table.
        `columns` is a comma-separated list of column to be inserted, datasets
        a 2-dimensional tuple of sets of values. The number of values has to
        correspond with the number of columns passed.
        """
        # VALIDATE DATA
        # columns
        if not isinstance(columns, str) or \
            not re.search(bs.config.REGEX_PATTERN_COLUMNS, columns):
            logging.critical("%s: ValueError: Attribute 1 is in invalid format. "\
                             "Valid syntax: (<value1>[, <value2>]...), where "\
                             "values need to begin/end with an alphanumeric "\
                             "character and contain '_' in addition. with a "\
                             "length between 2 and 32 characters."
                             % (self.__class__.__name__, ))
            raise SystemExit()
        # datasets
        if not isinstance(datasets, (list, tuple, )):
            logging.critical("%s: ValueError: Attribute 2 needs to be a list "\
                             "containing lists of datasets/tuple containing "\
                             "tuples of datasets."
                             % (self.__class__.__name__, ))
            raise SystemExit()
        logging.info("%s: Saving data to database..."
                     % (self.__class__.__name__))
        # WRITE DATA TO DATABASE
        try:
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            db_table_name = self._get_model_superclass().__name__.lower()
            conn.executemany("INSERT INTO %s (%s) VALUES (%s)"
                             % (db_table_name,
                                columns,
                                str("?, " * len(datasets[0]))[:-2], ),
                             datasets)
            conn.commit()
            conn.close()
            logging.info("%s: Data successfully saved to database."
                         % (self.__class__.__name__))
            return True
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])

    def get(self, columns, conditions=""):
        """
        Loads and returns dataset from selected `columns` in associated table
        under selection-conditions `conditions`, `conds_neg`.
        """
        # VALIDATE PARAMETERS
        # columns
        # allowed: a-z0-9_
        # first character only: _a-z
        # at least 4 characters
        if not isinstance(columns, str) or \
            not re.search(bs.config.REGEX_PATTERN_COLUMNS, columns) and\
            not columns == "*":
            logging.critical("%s: Argument 1 has invalid data. The column(s) "\
                             "need to be defined as a single or "\
                             "comma-separated list of valid column-names "\
                             "(containing alpha-numeric plus '_', starting "\
                             "with alphabetic and ending with alphanumeric "\
                             "characters only) and be between 2 and 32 "\
                             "characters in length."
                             % (self.__class__.__name__, ))
            raise SystemExit()
        # conditions
        self._validate_conditions(conditions)

        logging.info("%s: Loading data from columns '%s'..."
                     % (self.__class__.__name__, columns, ))
        # build conditions
        conditions_sql = ""
        conditions_parameters = []
        if conditions != "":
            conditions_sql = " WHERE "
            for condition in conditions:
                conditions_sql += "%s %s ? AND " % (condition[0],
                                                    condition[1], )
                conditions_parameters.append(condition[2])
            conditions_sql = conditions_sql[:-5]
        # execute SQL call
        table_name = self._get_model_superclass().__name__.lower()
        try:
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            conn.commit()
            res = conn.execute("SELECT %s FROM %s%s"
                               % (columns,
                                  table_name,
                                  conditions_sql, ),
                               tuple(conditions_parameters)).fetchall()
            conn.close()
            logging.info("%s: Data from columns '%s' successfully loaded "\
                         "from database."
                         % (self.__class__.__name__, columns, ))
            return res
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])


    def remove(self, conditions=""):
        """
        Removes dataset(s) from the corresponding table in the database that
        match the passed `conditions`.
        """
        # VALIDATE DATA
        self._validate_conditions(conditions)

        logging.info("%s: Removing data..."
                     % (self.__class__.__name__, ))
        # build conditions
        conditions_sql = ""
        conditions_parameters = []
        if conditions != "":
            conditions_sql = " WHERE "
            for condition in conditions:
                conditions_sql += "%s %s ? AND " % (condition[0],
                                                    condition[1], )
                conditions_parameters.append(condition[2])
            conditions_sql = conditions_sql[:-5]
        table_name = self._get_model_superclass().__name__.lower()
        # execute SQL call
        try:
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            conn.execute("DELETE FROM %s%s"
                         % (table_name, conditions_sql, ),
                         tuple(conditions_parameters)).fetchall()
            conn.commit()
            conn.commit()
            conn.close()
            logging.info("%s: Data successfully deleted from database."
                         % (self.__class__.__name__, ))
            return True
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])


    def _validate_conditions(self, conditions):
        """
        Validates data passed in in `conditions` and throws an error if it
        fails or returns True on success.
        """
        # VALIDATE DATA
        validity_check_pass = False
        if isinstance(conditions, (list, tuple, )):
            for condition in conditions:
                if isinstance(condition, (list, tuple, )):
                    if len(condition) == 3:
                        if re.search(bs.config.REGEX_PATTERN_COLUMN, condition[0]) and\
                            re.search("^[\=\>\<]$", condition[1]):
                            validity_check_pass = True
                        else:
                            validity_check_pass = False
                    else:
                        validity_check_pass = False
                else:
                    validity_check_pass = False
        elif conditions == "":
            validity_check_pass = True
        else:
            validity_check_pass = False
        if not validity_check_pass:
            logging.critical("%s: Argument 2 has invalid data. The "\
                             "conditions need to be a 2-dimensional list or "\
                             "tuple in the following form: "\
                             "(('<column-name>', ('=' or '>' or '<'), ('<string>'), ), ...)"
                             % (self.__class__.__name__, ))
            raise SystemExit()
        else:
            return True
