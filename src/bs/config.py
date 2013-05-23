# -*- coding: utf-8 -*-

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

""" * """

import os

PROJECT_NAME = "Backupshizzle"

# create config dir
CONFIG_PATH = os.path.normcase(os.path.join(os.path.expanduser('~'),
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
REGEX_PATTERN_NAME = "^[a-zA-Z][a-zA-Z0-9\_\-\ \#]{3,30}[a-zA-Z0-9\_\-\#]$"
# password-keys
REGEX_PATTERN_KEY = "^[a-zA-Z0-9]{8,64}$"

PALETTE = ["59554e",  # 0
           "6a665d",  # 1
           "c7c7ff",  # 2
           "33312d",  # 3
           "ffde02",  # 4
           "767167",  # 5
           "888277"]  # 6
# CSS
CSS = ""  # "QWidget {background: #c7c7ff; border-radius: 2px}"
# background: #59554e
CSS += "BSSetsCanvas {background: #59554e}"
# background: #6a665d
CSS += "nothing {background: #6a665d}"
# background: #c7c7ff
CSS += "BSFrame {background: #c7c7ff}"
# background: #33312d
CSS += "nothing {background: #33312d}"
# border-radius: 2px
#CSS += "BSMenuSetsItem, BSMenuSets {border-radius: 2px}"
CSS += "BSNodeItem, BSFrame {border-radius: 2px}"
# color: #33312d
CSS += "nothing {color: #33312d}"
# color: #ffde02
