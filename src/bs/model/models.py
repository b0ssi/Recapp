# -*- coding: utf-8 -*-

###############################################################################
##    models                                                                 ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Mar 13, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################

""" * """

import bs.model.models_master


class Users(bs.model.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    username = ["TEXT", "UNIQUE"]
    password = ["TEXT"]

    def __init__(self):
        pass


class Sources(bs.model.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    source_name = ["TEXT"]
    source_path = ["TEXT"]

    def __init__(self):
        pass


class Targets(bs.model.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    target_name = ["TEXT"]
    target_device_id = ["INTEGER", "UNIQUE"]

    def __init__(self):
        pass


class Filters(bs.model.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    filter_pattern = ["TEXT"]

    def __init__(self):
        pass


class Sets(bs.model.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    set_uid = ["TEXT", "UNIQUE"]
    user_id = ["INTEGER"]
    set_name = ["TEXT"]
    key_hash_64 = ["TEXT"]
    set_db_path = ["TEXT"]
    source_ass = ["TEXT"]
    filter_ass = ["TEXT"]
    targets = ["TEXT"]

    def __init__(self):
        pass
