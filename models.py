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

import models_master


class Users(models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    username = ["TEXT", "UNIQUE"]
    password = ["TEXT"]

    def __init__(self):
        pass


class Sources(models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    source_path = ["TEXT"]

    def __init__(self):
        pass


class Targets(models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    target_path = ["TEXT"]

    def __init__(self):
        pass


class Filters(models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    user_id = ["INTEGER"]
    filter_pattern = ["TEXT"]

    def __init__(self):
        pass
