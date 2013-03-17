# -*- coding: utf-8 -*-

################################################################################
##    test_sessions                                                           ##
################################################################################
################################################################################
##    Author:         Bossi                                                   ##
##                    © 2013 All rights reserved                              ##
##                    www.isotoxin.de                                         ##
##                    frieder.czeschla@isotoxin.de                            ##
##    Creation Date:  Mar 10, 2013                                            ##
##    Version:        0.0.000000                                              ##
##                                                                            ##
##    Usage:                                                                  ##
##                                                                            ##
################################################################################

import os
import session
import sqlite3
import unittest

#import logging
#logging.basicConfig(format="--------------- %(module)s: %(lineno)s (%(funcName)s)\r%(levelname)s      \t%(message)s", level=logging.DEBUG)

class TestSessionsModel(unittest.TestCase):
    def test_add_session_runs_smooth(self):
        my_session = session.SessionsModel()
        self.assertTrue(my_session.add_session())


class TestUserModel(unittest.TestCase):
    _mock_db_file_path = os.path.join(os.path.dirname(__file__), "unitTestDb.sqlite")

    def clean_db_mock_file(self):
        # delete mock db file if exists...
        try:
            if os.path.isfile(self._mock_db_file_path):
                os.remove(self._mock_db_file_path)
        except Exception as e:
            raise Exception(e)

    def test_save_was_successful(self):
        # clean-up mock db (file) if still exists...
        self.clean_db_mock_file()

        conn = sqlite3.connect(self._mock_db_file_path)
        conn.execute("CREATE TABLE `users` (`username` TEXT, `password` TEXT)")
        conn.commit()
        test_username = 'testUser'
        test_password = '40b244112641dd78dd4f93b6c9190dd46e0099194d5a44257b7efad6ef9ff4683da1eda0244448cb343aa688f5d3efd7314dafe580ac0bcbf115aeca9e8dc114'
        conn.execute("INSERT INTO `users` (`username`, `password`) VALUES (?, ?)", (test_username, test_password))
        conn.commit()
        conn.close()

        new_user = session.UserModel()
        new_user._configdb_path = self._mock_db_file_path
        new_user.log_in(test_username, "2")
        self.assertTrue(new_user.sadd))

        # clean-up mock db (file)
        self.clean_db_mock_file()

    def test_save_was_unsuccessful(self):
        # clean-up mock db (file) if still exists...
        self.clean_db_mock_file()

        # create connection to db and lock it...
        conn = sqlite3.connect(self._mock_db_file_path)
        conn.execute("PRAGMA locking_mode=EXCLUSIVE")
        conn.execute("BEGIN EXCLUSIVE")

        new_user = session.UserModel()
        new_user._configdb_path = self._mock_db_file_path
        new_user._username = "testUser"
        new_user._password = "testPassword"
        with self.assertRaises(SystemExit):
            new_user.sadd)

        conn.commit()
        conn.close()


        # clean-up mock db (file)
        self.clean_db_mock_file()
