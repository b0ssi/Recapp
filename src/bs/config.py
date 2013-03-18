# -*- coding: utf-8 -*-
from PyQt4 import QtCore
import os

###############################################################################
##    config.py                                                              ##
###############################################################################
###############################################################################
##    Author:         Frieder Czeschla                                       ##
##                    © 2012 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Nov 24, 2012                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################


# create config dir
CONFIG_PATH = os.path.normcase(os.path.join(str(QtCore.QDir.homePath()), ".backupshizzle"))

LOGFILE_PATH = os.path.join(CONFIG_PATH, "log.log")
CONFIGDB_PATH = os.path.join(CONFIG_PATH, "globalConfig.sqlite")
BT_BASEDIR_PATH = "backupshizzle"
BT_METAFILE_NAME = "config.conf"
USERID = int(-1)
LOGFILE = os.path.join(CONFIG_PATH, 'log.log')

VALID_NAME_MODEL_TABLE_PATTERN = "^([\_a-zA-Z]){1}([\_a-zA-Z0-9]){3,31}$"
VALID_NAME_ATTRIBUTE_COLUMN_PATTERN = "^([a-z]){1}([\_a-zA-Z0-9]){1,31}$"
