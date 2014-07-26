#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This package contains the master-superclass(es) for all models used in \
the project.
"""

import bs.config
import bs.messages.database
import inspect
import logging
import re
import sqlite3


class BSModel(object):
    """ ..

    Abstract superclass inherited by all models.
    """
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

    def _get_model_superclass(self, parent=None):
        """ ..

        Returns the Model superclass (meant to be directly subclassed by \
        this BSModel).
        """
        if not parent:
            parent=self.__class__

        for child in parent.__bases__:
            if child.__name__ == "BSModel":
                return parent
            elif child.__name__ != "object":
                return self._get_model_superclass(child)

    @property
    def _add_is_permitted(self, *args, **kwargs):
        """ ..

        :param arbitrary args: Arbitrary arguments passed in by overloading \
        implementations.

        :param dict kwargs: A `dict` containing arbitrary data passed in by \
        overloading implementations.

        :type: *bool*

        This method is designed to be overloaded by inheriting classes to
        implement individual access checks to be performed to grant self._add()
        permissions to execute. The return value must be a boolean.
        """
        return True

    def _add(self, columns, datasets, **kwargs):
        """ ..

        :param list columns: A list/tuple of *str*-objects naming the \
        database-columns to be inserted into.

        :param list datasets: A 1- or 2-dimensional list/tuple of sets of \
        values. These sets of values have to correspond to the order in which \
        the *columns* are given. This list/tuple can be 1-dimensional if only \
        one dataset is to be added or it can be a list of lists/tuple of \
        tuples, if multiple datasets are to be added.

        :param dict kwargs: A dictionary holding extra-control-data. Valid \
        keys and values are: `bool no_auth_requred`: If `True`, bypasses the \
        authentication check.

        :rtype: *sqlite3.Cursor*

        Adds a single or multiple data-sets to the object's database-table.
        """
        # extract kwargs
        try:
            no_auth_required = kwargs["no_auth_required"]
        except:
            no_auth_required = False
        # get permissions
        if not no_auth_required:
            if not self._add_is_permitted:
                logging.warning("%s: PermissionError: Object cannot save "\
                                "data due to a lack of permission."
                                % (self.__class__.__name__))
                return False
        # VALIDATE DATA
        # columns
        if (not isinstance(columns, str) or
                not re.search(bs.config.REGEX_PATTERN_COLUMNS, columns)):
            logging.critical("%s: ValueError: Attribute 1 is in invalid "\
                             "format. Valid syntax: "\
                             "(<value1>[, <value2>]...), where values need "\
                             "to begin/end with an alphanumeric character "\
                             "and contain '_' in addition. with a length "\
                             "between 2 and 32 characters."
                             % (self.__class__.__name__, ))
            raise SystemExit()
        # datasets
        if not isinstance(datasets, (list, tuple, )):
            logging.critical("%s: ValueError: Attribute 2 needs to be a list "\
                             "containing lists of datasets/tuple containing "\
                             "tuples of datasets."
                             % (self.__class__.__name__, ))
            raise SystemExit()
        logging.debug("%s: Saving data to database..."
                      % (self.__class__.__name__))
        # WRITE DATA TO DATABASE
        try:
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            db_table_name = self._get_model_superclass().__name__.lower()
            # if datasets is tuple of tuples (/list of lists)
            if type(datasets[0]) is (list, tuple):
                res = conn.executemany("INSERT INTO %s (%s) VALUES (%s)"
                                 % (db_table_name,
                                    columns,
                                    str("?, " * len(datasets[0]))[:-2], ),
                                 datasets)
            # if dataset only contains one tuple/list
            else:
                res = conn.execute("INSERT INTO %s (%s) VALUES (%s)"
                                 % (db_table_name,
                                    columns,
                                    str("?, " * len(datasets))[:-2], ),
                                 datasets)
            conn.commit()
            conn.close()
            logging.debug("%s: Data successfully saved to database."
                         % (self.__class__.__name__))
            return res
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])

    @property
    def _get_is_permitted(self, *args, **kwargs):
        """ ..

        :param args: Arbitrary arguments passed in by overloading \
        implementations.
        :param dict kwargs: A `dict` containing arbitrary data passed in by \
        overloading implementations.
        :type: *bool*

        This method is designed to be overloaded by inheriting classes to
        implement individual access checks to be performed to grant self._get()
        permissions to execute. The return value must be a boolean.
        """
        return True

    def _get(self, columns, conditions="", **kwargs):
        """ ..

        :param str columns:
        :param tuple conditions: ! NB: not sure about type
        :param arbitrary kwargs:
        :rtype: *tuple*

        Loads and returns dataset from selected `columns` in associated table
        under selection-conditions `conditions`, `conds_neg`.

        It accepts the following keyword-arguments:
        - no_auth_required BOOL: bypasses the authentication check
        """
        # extract kwargs
        try:
            no_auth_required = kwargs["no_auth_required"]
        except:
            no_auth_required = False
        # get permissions
        if not no_auth_required:
            if not self._get_is_permitted:
                logging.warning("%s: PermissionError: Object cannot _get "\
                                "data due to a lack of permission."
                                % (self.__class__.__name__))
                return []
        # VALIDATE PARAMETERS
        # columns
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

        logging.debug("%s: Loading data from columns '%s'..."
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
            logging.debug("%s: Data from columns '%s' successfully loaded "\
                         "from database."
                         % (self.__class__.__name__, columns, ))
            return res
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])

    @property
    def _remove_is_permitted(self, *args, **kwargs):
        """ ..

        :param arbitrary args: Arbitrary arguments passed in by overwriting \
        implementations.
        :param dict kwargs: A `dict` containing arbitrary data passed in by \
        overloading implementations.
        :type: *bool*

        This method is designed to be overloaded by inheriting classes to
        implement individual access checks to be performed to grant
        self._remove() permissions to execute. The return value must be a
        boolean.
        """
        return True

    def _remove(self, conditions="", **kwargs):
        """
        Removes dataset(s) from the corresponding table in the database that
        match the passed `conditions`.

        It accepts the following keyword-arguments:
        - no_auth_required BOOL: bypasses the authentication check
        """
        # extract kwargs
        try:
            no_auth_required = kwargs["no_auth_required"]
        except:
            no_auth_required = False
        # get permissions
        if not no_auth_required:
            if not self._remove_is_permitted:
                logging.warning("%s: PermissionError: Object cannot _remove "\
                                "data due to a lack of permission."
                                % (self.__class__.__name__))
                return False
        # VALIDATE DATA
        self._validate_conditions(conditions)

        logging.debug("%s: Removing data..."
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
            logging.debug("%s: Data successfully deleted from database."
                         % (self.__class__.__name__, ))
            return True
        except Exception as e:
            logging.critical(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[0])
            raise SystemExit(bs.messages.database.general_error(bs.config.CONFIGDB_PATH, e)[1])

    @property
    def _update_is_permitted(self, *args, **kwargs):
        """ ..

        :param args: Arbitrary arguments passed in by overloading \
        implementations.
        :param dict kwargs: A ``dict`` containing arbitrary data passed in by \
        overloading implementations.
        :type: *bool*

        This method is designed to be overloaded by inheriting classes to \
        implement individual access checks to be performed to grant \
        self._update() permissions to execute. The return value must be a \
        boolean.
        """
        return True

    def _update(self, column_assignments, conditions, **kwargs):
        """
        Updates a dataset in db with matching id
        """
        # extract kwargs
        try:
            no_auth_required = kwargs["no_auth_required"]
        except:
            no_auth_required = False
        # get permissions
        if not no_auth_required:
            if not self._remove_is_permitted:
                logging.warning("%s: PermissionError: Object cannot _remove "\
                                "data due to a lack of permission."
                                % (self.__class__.__name__))
                return False
        # VALIDATE DATA
        # conditions
        self._validate_conditions(conditions)
        # column_assignments
        check = True
        if not type(column_assignments) in (tuple, list, ):
            check = False
        for column_assignment in column_assignments:
            if not re.match(bs.config.REGEX_PATTERN_COLUMN,
                            column_assignment[0]):
                check = False
        if not check:
            logging.warning("%s: The first argument is in a wrong format or "\
                            "contains invalid characters. It needs to be a "\
                            "list or tuple of lists or tuples containing two "\
                            "positions: "\
                            "(<column_name string>, <new_value string, int, float, ...>)"
                            % (self.__class__.__name__, ))
            return False
        logging.debug("%s: Updating data..."
                     % (self.__class__.__name__, ))
        # build column_assignments
        sql_parameters = []
        column_assignments_parameters = ""
        for column_assignment in column_assignments:
            column_assignments_parameters += str(column_assignment[0])
            column_assignments_parameters += " = "
            column_assignments_parameters += "?, "
            sql_parameters.append(column_assignment[1])
        column_assignments_parameters = column_assignments_parameters[:-2]
        # build conditions
        conditions_sql = ""
        if conditions != "":
            conditions_sql = " WHERE "
            for condition in conditions:
                conditions_sql += "%s %s ? AND " % (condition[0],
                                                    condition[1], )
                sql_parameters.append(condition[2])
            conditions_sql = conditions_sql[:-5]
        table_name = self._get_model_superclass().__name__.lower()
        # execute SQL call
        try:
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            conn.execute("UPDATE %s SET %s%s"
                         % (table_name,
                            column_assignments_parameters,
                            conditions_sql, ),
                         tuple(sql_parameters)).fetchall()
            conn.commit()
            conn.commit()
            conn.close()
            logging.debug("%s: Data successfully updated in database."
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
