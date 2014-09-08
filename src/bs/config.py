#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

This module contains the global configuration.
"""

import json
import platform
import os
import sys
import time
if platform.system().startswith("win"):
    import winreg

# --------------------------------------------------------------- Generated Data
bs_config_path = os.path.realpath("bs/config.json")
# store data in JSON
if "-dev" in sys.argv:
    json_obj = {}
    json_obj["BUILD_TIMESTAMP"] = time.time()

    f = open(bs_config_path, "w")
    json.dump(json_obj, f)
    f.close()

# ---------------------------------------------------------- read data from JSON
d = {}
if os.path.isfile(bs_config_path):
    f = open(bs_config_path, "r")
    d = json.load(f)
    f.close()
BUILD_TIMESTAMP = d.get("BUILD_TIMESTAMP", 0)

# Static Data
PROJECT_NAME = "Recapp"
VERSION = "0.0.3.13"

COPYRIGHT_TIMEFRAME = "2012-%s" % (time.strftime("%Y"), )
COPYRIGHT_HOLDER = "Frieder Czeschla"
MANUFACTURER = "Isotoxin"
FQP = "de.isotoxin.recapp"

# create config dir
if platform.system().startswith("win"):
    # true for Win >= Vista
    CONFIG_PATH = os.path.join(os.getenv("PROGRAMDATA"), FQP)
    if not os.path.isdir(CONFIG_PATH):
        # Cater for WinXP
        CONFIG_PATH = os.path.join(os.getenv("ALLUSERSPROFILE"), "Application Data", FQP)
else:
    CONFIG_PATH = os.path.join(os.path.expanduser("~"), "." + FQP)

LOGFILE_PATH = os.path.join(CONFIG_PATH, "log.log")
CONFIGDB_PATH = os.path.join(CONFIG_PATH, "globalConfig.sqlite")
BT_BASEDIR_PATH = "%s" % (PROJECT_NAME.lower(), )
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
           "888277",  # 6
           "ff0000",  # 7
           "ff2a2a",  # 8
           "393632",  # 9
           "48453f",  # 10
           ]
# CSS
CSS = ""  # "QWidget {background: #c7c7ff; border-radius: 2px}"
# background: #59554e
CSS += "BSSetsCanvas {background: #59554e}"
# background: #6a665d
CSS += "nothing {background: #6a665d}"
# background: #c7c7ff
CSS += "BSNode, BSMenu {background: #c7c7ff}"
# border-radius: 2px
# CSS += "BSMenuSetsItem, BSMenuSets {border-radius: 2px}"
CSS += "BSMenu, BSNodeItem, BSNode {border-radius: 2px}"
# color: #33312d
CSS += "nothing {color: #33312d}"
# color: #ffde02
