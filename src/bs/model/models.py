#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

"""

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
    filter_rules_data = ["TEXT"]
    name = ["TEXT"]

    def __init__(self):
        pass


class Sets(bs.model.models_master.BSModel):
    id = ["INTEGER", "PRIMARY KEY"]
    set_uid = ["TEXT", "UNIQUE"]
    user_id = ["INTEGER"]
    set_name = ["TEXT"]
    salt_dk = ["TEXT"]
    set_db_path = ["TEXT"]
    source_ass = ["TEXT"]
    filter_ass = ["TEXT"]
    targets = ["TEXT"]
    gui_data = ["TEXT"]

    def __init__(self):
        pass
