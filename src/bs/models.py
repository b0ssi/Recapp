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

import bs.models_master


class Users(bs.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    username = ["TEXT", "UNIQUE"]
    password = ["TEXT"]

    def __init__(self):
        pass


class Sources(bs.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    source_name = ["TEXT"]
    source_path = ["TEXT"]

    def __init__(self):
        pass


class Targets(bs.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    target_name = ["TEXT"]
    target_id = ["INTEGER", "UNIQUE"]

    def __init__(self):
        pass


class Filters(bs.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    filter_pattern = ["TEXT"]

    def __init__(self):
        pass


class Sets(bs.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    sources = ["TEXT"]
    targets = ["TEXT"]
    filters = ["TEXT"]

    def __init__(self):
        pass
