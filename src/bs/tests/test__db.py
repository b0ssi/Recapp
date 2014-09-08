#!/usr/bin/python3
# -*- coding: utf-8 -*-
#@PydevCodeAnalysisIgnore

""" ..

"""

import bs.ctrl._db
import os
import time
import unittest

_mock_module_file_path_base = os.path.join(os.path.dirname(__file__), )
_mock_module_module_path_base = "bs.tests"


# need to generate new name for each test to make sure the module using that
# name has a unique name every time (to prevent caching)
def get_free_filename():
    free_filename = str(int(time.time() * 100))
    while os.path.isfile(os.path.join(_mock_module_file_path_base,
                                      free_filename) + ".py"):
        free_filename = int(time.time() * 100)
    return free_filename


def remove_mock_class(file_path):
    try:
        while os.path.isfile(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        raise


def write_mock_class_empty(file_path):
    try:
        with open(file_path, "w") as f:
            print("", file=f)
        f.close()
        return True
    except Exception as e:
        raise SystemExit("An Error Occurred: %s" % (e, ))


def write_mock_class_only_invalid_class_name(file_path):
    try:
        with open(file_path, "w") as f:
            out = "class 9Test(object):\n"
            out += "\ttest_attr = ['INTEGER']\n"

            print(out, file=f)
        f.close()
        return True
    except Exception as e:
        raise SystemExit("An Error Occurred: %s" % (e, ))


def write_mock_class_member(file_path, contents):
    try:
        with open(file_path, "w") as f:
            out = contents

            print(out, file=f)
        f.close()
        return True
    except Exception as e:
        raise SystemExit("An Error Occurred: %s" % (e, ))


class TestSyncDb_verify_schema(unittest.TestCase):
    """
    Tests `_verify_schema` to validate schema module correctly and raise
    exceptions appropriately if necessary.

    filter module name in:
        - start with [_A-Z]
        - length 4-32
        if module is empty:
            return: True
        else:
            if class completely empty:
                return: SystemExit
            if class is filled with invalid attributes (effectively empty):
                return: SystemExit
            if class has >= 1 valid attribute with invalid name:
                return: SystemExit
            if class has >= 1 valid attribute with valid name:
                return True
    """

    def test_module_is_empty(self):
        # create mock module
        filename = get_free_filename()
        file_path = os.path.join(_mock_module_file_path_base, filename) + ".py"
        module_path = _mock_module_module_path_base + "." + filename

        write_mock_class_empty(file_path)

        sync_db = bs.ctrl._db.SyncDb(module_path)
        self.assertTrue(sync_db._verify_schema())

        # clean-up mock-module
        remove_mock_class(file_path)

    def test_module_has_only_invalid_class_1(self):
        # create mock module
        filename = get_free_filename()
        file_path = os.path.join(_mock_module_file_path_base, filename) + ".py"
        module_path = _mock_module_module_path_base + "." + filename

        write_mock_class_only_invalid_class_name(file_path)

        with self.assertRaises(SystemExit):
            sync_db = bs.ctrl._db.SyncDb(module_path)

        # clean-up mock-module
        remove_mock_class(file_path)

    def test_member_has_invalid_data_only(self):
        contents_combinations = [
                                 "class Tetdjhhhhhhhhfhfhfhfhfhfhfhfhfhfd(object):\n"\
                                 "    testattr = ['INTEGER']",
                                 "class Tet(object):\n"\
                                 "    testattr = ['INTEGER']",
                                 "class Test(object):\n"\
                                 "    pass",
                                 "class Test(object):\n"\
                                 "    def test2(self):\n"
                                 "        pass",
                                 "class Test(object):\n"\
                                 "    def test2(self):\n"
                                 "        _test = ['INTEGER']",
                                 "class Test(object):\n"\
                                 "    test = []",
                                 "class Test(object):\n"\
                                 "    test = [\"WHATEVER\", \"UNIQUE\", \"17\"]",
                                 "class Test(object):\n"\
                                 "    test = [\"WHATEVER\", \"UNIQUE\"]",
                                 "class Test(object):\n"\
                                 "    test = [\"TEXT\", \"WHATEVER\"]",
                                 "class Test(object):\n"\
                                 "    test = [\"TEXT\", \"PRIMARY KEY\"]",
                                 "class Test(object):\n"\
                                 "    test = (\"one\", \"two\", )",
                                 "class Test(object):\n"\
                                 "    @property\n"
                                 "    def test2(self):\n"
                                 "        return list(['INTEGER'])",
                                 "class Test(object):\n"\
                                 "    @property\n"
                                 "    def test2(self):\n"
                                 "        return ['INTEGER']",
                                 "class Test(object):\n"\
                                 "    def test2(self):\n"
                                 "        return list(['INTEGER'])",
                                 "class Test(object):\n"\
                                 "    def test2(self):\n"
                                 "        return ['INTEGER']",
                                 ]
        for contents_combination in contents_combinations:
            # create mock module
            filename = get_free_filename()
            file_path = os.path.join(_mock_module_file_path_base, filename) + ".py"
            module_path = _mock_module_module_path_base + "." + filename

            write_mock_class_member(file_path, contents_combination)

            sync_db = bs.ctrl._db.SyncDb(module_path)
            with self.assertRaises(SystemExit):
                sync_db._verify_schema()

            # clean-up mock-module
            remove_mock_class(file_path)

    def test_member_has_valid_data_only(self):
        contents_combinations = [
                                 "class Test(object):\n"\
                                 "    test = ['INTEGER', 'PRIMARY KEY']",
                                 "class Test(object):\n"\
                                 "    test = ['INTEGER']",
                                 ]
        for contents_combination in contents_combinations:
            # create mock module
            filename = get_free_filename()
            file_path = os.path.join(_mock_module_file_path_base, filename) + ".py"
            module_path = _mock_module_module_path_base + "." + filename

            write_mock_class_member(file_path, contents_combination)

            sync_db = bs.ctrl._db.SyncDb(module_path)
            self.assertTrue(sync_db._verify_schema())

            # clean-up mock-module
            remove_mock_class(file_path)
#
#    def test_member_has_valid_attribute_with_valid_name(self):
#        pass
