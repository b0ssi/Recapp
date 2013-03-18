# -*- coding: utf-8 -*-

################################################################################
##    test__db                                                                ##
################################################################################
################################################################################
##    Author:         Bossi                                                   ##
##                    © 2013 All rights reserved                              ##
##                    www.isotoxin.de                                         ##
##                    frieder.czeschla@isotoxin.de                            ##
##    Creation Date:  Mar 9, 2013                                             ##
##    Version:        0.0.000000                                              ##
##                                                                            ##
##    Usage:                                                                  ##
##                                                                            ##
################################################################################

import _db
import os
import unittest

class TestDb(unittest.TestCase):
    _mock_db_file_path = os.path.join(os.path.dirname(__file__), "unitTestDb.sqlite")
    
    def clean_db_mock_file(self):
        # delete mock db file if exists...
        try:
            if os.path.isfile(self._mock_db_file_path):
                os.remove(self._mock_db_file_path)
        except Exception as e:
            raise Exception(e)

    def test_database_file_does_exist_and_is_valid(self):
        # clean-up mock db (file) if still exists...
        self.clean_db_mock_file()
        # create mock db (file)
        my_class = _db.Db()
        my_class._configdb_path = self._mock_db_file_path
        my_class.initialize()
        
        self.assertTrue(my_class.initialize())
        # clean-up mock db (file)
        self.clean_db_mock_file()
    
    def test_database_file_does_exist_but_is_invalid_or_access_denied(self):
        my_class = _db.Db()
        my_class._configdb_path = __file__
        
        with self.assertRaises(SystemExit):
            my_class.initialize()
    
    def test_database_file_does_exist_but_is_invalid_and_of_zero_lenght(self):
        # clean-up mock db (file) if still exists...
        self.clean_db_mock_file()
        # create mock database (file)
        f = open(self._mock_db_file_path, "w")
        f.close()

        my_class = _db.Db()
        my_class._configdb_path = self._mock_db_file_path
        
        with self.assertRaises(SystemExit):
            my_class.initialize()
        # clean-up mock db (file)
        self.clean_db_mock_file()

    def test_database_file_does_not_exist_but_can_be_initialized(self):
        # clean-up mock db (file) if still exists...
        self.clean_db_mock_file()
        
        my_class = _db.Db()
        my_class._configdb_path = self._mock_db_file_path
        
        self.assertTrue(my_class.initialize())
        # clean-up mock db (file)
        self.clean_db_mock_file()
    
    def test_database_file_does_not_exist_and_can_not_be_initialized(self):
        # mock db...
        mock_db_file_path = os.path.realpath("B:/testdb.sqlite")
        
        my_class = _db.Db()
        my_class._configdb_path = mock_db_file_path
        
        with self.assertRaises(SystemExit):
            my_class.initialize()
