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

PROJECT_NAME = "Backupshizzle"

# create config dir
CONFIG_PATH = os.path.normcase(os.path.join(str(QtCore.QDir.homePath()),
                                            ".backupshizzle"))

LOGFILE_PATH = os.path.join(CONFIG_PATH, "log.log")
CONFIGDB_PATH = os.path.join(CONFIG_PATH, "globalConfig.sqlite")
BT_BASEDIR_PATH = "backupshizzle"
BT_METAFILE_NAME = "config.conf"
USERID = int(-1)
LOGFILE = os.path.join(CONFIG_PATH, 'log.log')


REGEX_PATTERN_TABLE = "^[a-zA-Z][a-zA-Z0-9\_]{2,30}[a-zA-Z0-9]$"
REGEX_PATTERN_COLUMN = "^[a-zA-Z][a-zA-Z0-9\_]{0,30}[a-zA-Z0-9]$"
REGEX_PATTERN_COLUMNS = "^([a-zA-Z][a-zA-Z0-9\_]{0,30}[a-zA-Z0-9](\,[\ ]*)?)+$"
REGEX_PATTERN_USERNAME = "^[a-zA-Z][a-zA-Z0-9\_]{2,30}[a-zA-Z0-9]$"
# names for sources, targets, filters... etc.
REGEX_PATTERN_NAME = "^[a-zA-Z][a-zA-Z0-9\_\-\ \#]{3,31}$"
