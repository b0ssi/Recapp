#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

This is the *controller* package that contains the application's business \
logic.
"""

from PySide import QtCore

import binascii
import bs.config
import bs.ctrl.backup
import bs.gui.window_main
import bs.gui.window_backup_monitor
import bs.gui.window_filter_manager
import bs.messages
import bs.model.models
import Crypto.Protocol.KDF
import hashlib
import json
import logging
import os
import platform
import random
import re
import sqlite3
import time
if platform.system().startswith("win"):
    import win32file


class BackupFilterCtrl(bs.model.models.Filters):
    """ ..

    :param bs.ctrl.session.SessionCtrl session: The corresponding session \
    controller.
    :param int backup_filter_id: The filter's ID identifying it uniquely in \
    the database.

    The *BackupFilterCtrl* represents an instance of a backup-filter.
    """
    _session = None
    _backup_filter_id = None
    _backup_filter_name = None

    _backup_entity_ass = None
    _backup_filter_rules = None
    _backup_filter_rules_mode = None

    #: ..
    backup_filter_rules_mode_and = "backup_filter_rules_mode_and"
    #: ..
    backup_filter_rules_mode_or = "backup_filter_rules_mode_or"
    #: ..
    backup_filter_rules_mode_xor = "backup_filter_rules_mode_xor"

    def __init__(self, session, backup_filter_id):
        self._session = session
        self._backup_filter_id = backup_filter_id
        # if flter_id == None, this is a new filter, add to database
        if not self._backup_filter_id:
            res = self._add("user_id",
                            (self._session.user.id, ))
            self._backup_filter_id = res.lastrowid

        self._update_signal = bs.utils.Signal()

        self._backup_entity_ass = []
        self._backup_filter_rules = []

    def __repr__(self):
        return "Filter #%d <%s>" % (self._backup_filter_id, self.__class__.__name__, )

    @property
    def backup_filter_id(self):
        """ ..

        :type: *int*

        The filter's *ID*.
        """
        return self._backup_filter_id

    @property
    def backup_filter_rules_mode(self):
        """ ..

        :type: `enum`

        The mode this filter's rules are to interpreted in. This is an enum on \
        :class:`bs.ctrl.session.BackupFilterCtrl`.
        """
        if not self._backup_filter_rules_mode:
            self._backup_filter_rules_mode = self._get("filter_rules_mode",
                                                       (("user_id", "=", self._session.user.id, ),
                                                        ("id", "=", self._backup_filter_id),
                                                        ))[0][0]
        return self._backup_filter_rules_mode

    @backup_filter_rules_mode.setter
    def backup_filter_rules_mode(self, backup_filter_rules_mode):
        self._backup_filter_rules_mode = backup_filter_rules_mode

    @property
    def backup_filter_name(self):
        """ ..

        :type: *str*

        The filter's *name*.
        """
        if not self._backup_filter_name:
            self._backup_filter_name = self._get("name", (("id", "=", self._backup_filter_id, ), ), )[0][0]
        return self._backup_filter_name

    @backup_filter_name.setter
    def backup_filter_name(self, backup_filter_name):
        self._backup_filter_name = backup_filter_name

    @property
    def backup_filter_rules(self):
        """ ..

        :type: *list*

        A list of one or more \
        :class:`~bs.ctrl.session.BackupFilterRuleAttributesCtrl` that make up \
        this filter.
        """
        if not self._backup_filter_rules:
            data_sets = self._get("filter_rules_data",
                                  (("user_id", "=", self._session.user.id, ),
                                   ("id", "=", self._backup_filter_id),
                                   )
                                  )[0][0]
            data_sets = json.loads(data_sets)
            # extract data_set, generate filter_rule objects
            for key_id in data_sets.keys():
                category = data_sets[key_id]["category"]
                file_folder = data_sets[key_id]["file_folder"]
                include_subfolders = data_sets[key_id]["include_subfolders"]
                truth = data_sets[key_id]["truth"]
                # instantiate object
                if category == BackupFilterRuleCtrl.category_size:
                    mode_size = data_sets[key_id]["mode_size"]
                    size = data_sets[key_id]["size"]
                    obj = BackupFilterRuleSizeCtrl(key_id,
                                                   category,
                                                   file_folder,
                                                   include_subfolders,
                                                   truth,
                                                   mode_size,
                                                   size)
                if category == BackupFilterRuleCtrl.category_path:
                    mode_path = data_sets[key_id]["mode_path"]
                    match_case = data_sets[key_id]["match_case"]
                    path_pattern = data_sets[key_id]["path_pattern"]
                    obj = BackupFilterRulePathCtrl(key_id,
                                                   category,
                                                   file_folder,
                                                   include_subfolders,
                                                   truth,
                                                   mode_path,
                                                   match_case,
                                                   path_pattern)
                if category == BackupFilterRuleCtrl.category_date:
                    timestamp_type = data_sets[key_id]["timestamp_type"]
                    position = data_sets[key_id]["position"]
                    reference_date_time_type = data_sets[key_id]["reference_date_time_type"]
                    reference_date_time_timestamp = data_sets[key_id]["reference_date_time_timestamp"]
                    reference_date_time_offsets = data_sets[key_id]["reference_date_time_offsets"]
                    obj = BackupFilterRuleDateCtrl(key_id,
                                                   category,
                                                   file_folder,
                                                   include_subfolders,
                                                   truth,
                                                   timestamp_type,
                                                   position,
                                                   reference_date_time_type,
                                                   reference_date_time_timestamp,
                                                   reference_date_time_offsets)
                if category == BackupFilterRuleCtrl.category_attributes:
                    attribute_type = data_sets[key_id]["attribute_type"]
                    attribute_value = data_sets[key_id]["attribute_value"]
                    obj = BackupFilterRuleAttributesCtrl(key_id,
                                                         category,
                                                         file_folder,
                                                         include_subfolders,
                                                         truth,
                                                         attribute_type,
                                                         attribute_value)
                self.add_backup_filter_rule(obj)
        return self._backup_filter_rules

    @property
    def backup_entity_ass(self):
        """ ..

        :type: *list*

        Returns an associative array (dictionary) in the following format:
        {:class:`~bs.ctrl.session.BackupSetCtrl`: <backup_entity>, ...: ...}, \
        where *backup_entity* is one of the following: \
        :class:`~bs.ctrl.session.BackupFilterCtrl` \
        :class:`~bs.ctrl.session.BackupTargetCtrl`
        """
        if not self._backup_entity_ass:
            backup_entity_ass = {}
            # Follows the "dumb" model: Sets don't know the associations, have to check the sets table here to get them
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            res = conn.execute("SELECT id, filter_ass FROM sets WHERE user_id = ?", (self._session.user.id, )).fetchall()
            # run through set-results
            for dataset in res:
                set_id = dataset[0]
                filter_ass_dict = json.loads(dataset[1])
                # get set object
                backup_set_obj = [x for x in self._session.backup_sets.sets if x.backup_set_id == set_id][0]
                # run through associations in set
                for backup_filter_id in filter_ass_dict:
                    if self.backup_filter_id == int(backup_filter_id):
                        # list to store associations for set in
                        if backup_set_obj not in backup_entity_ass.keys():
                            backup_entity_ass[backup_set_obj] = []
                        # this can be either -1 for the set's target set or a natural number as a filter id
                        ass_ids = filter_ass_dict[backup_filter_id]
                        for ass_id in ass_ids:
                            # target set associated
                            if ass_id == -1:
                                backup_entity_ass[backup_set_obj].append(backup_set_obj.backup_targets)
                            # filter associated
                            else:
                                # get filter object with id that was found
                                for backup_filter_obj_iter in self._session.backup_filters.backup_filters:
                                    if backup_filter_obj_iter.backup_filter_id == ass_id:
                                        backup_entity_ass[backup_set_obj].append(backup_filter_obj_iter)
            self._backup_entity_ass = backup_entity_ass
        return self._backup_entity_ass

    @property
    def session(self):
        """ ..

        :rtype: :class:`bs.ctrl.session.SessionCtrl`

        The corresponding :class:`bs.ctrl.session.SessionCtrl`.
        """
        return self._session

    @property
    def update_signal(self):
        """ ..

        :type: :class:`bs.utils.Signal`

        This update signal signifies when a property of the filter is \
        changed/updated.
        """
        return self._update_signal

    def add_backup_filter_rule(self, backup_filter_rule):
        """ ..

        :param bs.ctrl.session.BackupFilterRuleCtrl backup_filter_rule:

        :rtype: `boolean`

        Adds a filter-rule to the filter. Returns ``True`` on success, ``False`` if filter already exists.
        """
        # set default id
        if not backup_filter_rule.id:
            backup_filter_rule.id = str(len(self._backup_filter_rules))
        if backup_filter_rule not in self._backup_filter_rules:
            self._backup_filter_rules.append(backup_filter_rule)
            self._backup_filter_rules = sorted(self._backup_filter_rules, key=lambda x: x.id)
            return True
        else:
            return False

    def associate(self, backp_set, backup_entity):
        """ ..

        :param bs.ctrl.session.BackupSetCtrl backup_set:
        :param bs.model.models_master.BSModel backup_entity: The \
        *backup-entity* to associate with. This is one of the following: \
        :class:`~bs.ctrl.session.BackupSourceCtrl` \
        :class:`~bs.ctrl.session.BackupFilterCtrl` \
        :class:`~bs.ctrl.session.BackupTargetCtrl`
        :rtype: *void*

        Associates entity with another backup_entitys. This is done when \
        connecting up nodes.
        """
        self._backup_entity_ass[backp_set].append(backup_entity)

    def disassociate(self, backup_set, backup_entity):
        """ ..

        :type: *void*

        Breaks connection to a given :meth:`backup_entity_ass`
        """
        self._backup_entity_ass[backup_set].pop(self._backup_entity_ass[backup_set].index(backup_entity))

    def remove_backup_filter_rule(self, backup_filter_rule):
        """ ..

        :rtype: `boolean`

        Removes ``backup_filter_rule`` from backup-filter. Returns ``True`` \
        on success, ``False`` if passed backup-filter-rule is not hosted by \
        this backup-filter.
        """
        if backup_filter_rule in self._backup_filter_rules:
            self._backup_filter_rules.remove(backup_filter_rule)
            return True
        else:
            return False

    def save(self):
        """ ..

        Saves the filter to the databse.
        """
        filter_rules_data = {}
        for backup_filter_rule in self._backup_filter_rules:
            filter_rule_id = backup_filter_rule.id
            filter_rule_data = {}
            # add fields
            filter_rule_data["category"] = backup_filter_rule.category
            filter_rule_data["file_folder"] = backup_filter_rule.file_folder
            filter_rule_data["include_subfolders"] = backup_filter_rule.include_subfolders
            filter_rule_data["truth"] = backup_filter_rule.truth
            if isinstance(backup_filter_rule, BackupFilterRuleAttributesCtrl):
                filter_rule_data["attribute_type"] = backup_filter_rule.attribute_type
                filter_rule_data["attribute_value"] = backup_filter_rule.attribute_value
            elif isinstance(backup_filter_rule, BackupFilterRuleDateCtrl):
                filter_rule_data["timestamp_type"] = backup_filter_rule.timestamp_type
                filter_rule_data["position"] = backup_filter_rule.position
                filter_rule_data["reference_date_time_type"] = backup_filter_rule.reference_date_time_type
                filter_rule_data["reference_date_time_timestamp"] = backup_filter_rule.reference_date_time_timestamp
                filter_rule_data["reference_date_time_offsets"] = backup_filter_rule.reference_date_time_offsets
            elif isinstance(backup_filter_rule, BackupFilterRulePathCtrl):
                filter_rule_data["mode_path"] = backup_filter_rule.mode_path
                filter_rule_data["match_case"] = backup_filter_rule.match_case
                filter_rule_data["path_pattern"] = backup_filter_rule.path_pattern
            elif isinstance(backup_filter_rule, BackupFilterRuleSizeCtrl):
                filter_rule_data["mode_size"] = backup_filter_rule.mode_size
                filter_rule_data["size"] = backup_filter_rule.size
            filter_rules_data[filter_rule_id] = filter_rule_data
        filter_rules_data_json = json.dumps(filter_rules_data, indent=4)
        self._update([["filter_rules_data", filter_rules_data_json]], [["id", "=", self.backup_filter_id]])
        self._update_signal.emit()


class BackupFiltersCtrl(bs.model.models.Filters):
    """ ..

    :param bs.ctrl.session.SessionGuiCtrl session_gui: The session's \
    :class:`~bs.ctrl.session.SessionGuiCtrl`.

    This class holds all :class:`~bs.ctrl.session.BackupFilterCtrl` for the current \
    :class:`~bs.ctrl.session.SessionCtrl` and is used to create and delete filters on a \
    session-level.
    """
    _session = None
    _backup_filters = None

    def __init__(self, session_gui):
        """ * """
        super(BackupFiltersCtrl, self).__init__()
        self._session = session_gui

        self._backup_filters = []

    def __repr__(self):
        return "Filters <%s>" % (self.__class__.__name__)

    @property
    def backup_filters(self):
        """ ..

        :type: *list*

        A list of all :class:`~bs.ctrl.session.BackupFilterCtrl` associated with the current \
        set.
        """
        # filter list is empty, load from db
        if len(self._backup_filters) == 0:
            res = self._get("id",
                            (("user_id", "=", self._session.user.id), ))
            for data_set in res:
                filter_id = data_set[0]
                new_filter_obj = BackupFilterCtrl(self._session,
                                                  filter_id)
                self._backup_filters.append(new_filter_obj)
        return self._backup_filters

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """ ..

        Re-implemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """ ..

        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """ ..

        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def create_backup_filter(self, filter_pattern):
        """ ..

        :param str filter_pattern: The regex pattern to be used.
        :rtype: *bool*

        Creates a new backup-filter and adds it to the set.
        """
        # VALIDATE DATA
        # filter
        if not re.match("$.*^", filter_pattern):
            logging.warning("%s: The filter_pattern contains invalid "
                            "characters. It needs to start with an "
                            "alphabetic and contain alphanumerical "
                            "characters plus '\_\-\#' and space."
                            % (self.__class__.__name__, ))
            return False
        # validate filter data here once decided on format
        # add obj
        filter_id = None
        new_filter_obj = BackupFilterCtrl(self._session,
                                          filter_id,
                                          filter_pattern)
        self._backup_filters.append(new_filter_obj)
        # out
        return True

    def delete_backup_filter(self, filter_obj):
        """ ..

        :param bs.ctrl.session.BackupFilterCtrl filter_obj: The \
        :class:`~bs.ctrl.session.BackupFilterCtrl` to be deleted from the set.

        Deletes an existing backup-filter.
        """
        # VALIDATE DATA
        # filter_id
        if not isinstance(filter_obj, BackupFilterCtrl):
            logging.warning("%s: The first argument needs to be of type integer."
                            % (self.__class__.__name__, ))
            return False
        # delete from DB
        self._remove((("id", "=", filter_obj._filter_id, ), ))
        # remove obj
        self._backup_filters.pop(self._backup_filters.index(filter_obj))
        # out
        return True


class BackupFilterRuleCtrl(object):
    """ ..

    :param int id: The filter-rule-attribute's ID.
    :param enum category: A *category* enum on :class:`~bs.ctrl.session.BackupFilterRuleCtrl`
    :param enum file_folder: A *file_folder* enum on :class:`~bs.ctrl.session.BackupFilterRuleCtrl`
    :param enum include_subfolders: An *include_subfolders* enum on :class:`~bs.ctrl.session.BackupFilterRuleCtrl`
    :param boolean truth: Indicates whether the rule is set to true ("is/does") or false ("is not/does not")

    This class is not to be instantiated directly but serves as an abstract
    superclass to

    * :class:`~bs.ctrl.session.BackupFilterRuleAttributesCtrl`
    * :class:`~bs.ctrl.session.BackupFilterRuleDateCtrl`
    * :class:`~bs.ctrl.session.BackupFilterRulePathCtrl`
    * :class:`~bs.ctrl.session.BackupFilterRuleSizeCtrl`
    """
    _id = None
    _category = None  # enum (self.category_size, ...
    _file_folder = None  # enum (file/file_folder/folder)
    _include_subfolders = None
    _truth = None  # is/is not / does/does not

    # enums
    #: ..
    attribute_hidden = "attribute_hidden"
    #: ..
    attribute_group = "attribute_group"
    #: ..
    attribute_owner = "attribute_owner"
    #: ..
    attribute_win_archive = "attribute_win_archive"
    #: ..
    attribute_win_encrypted = "attribute_win_encrypted"
    #: ..
    attribute_win_offline = "attribute_win_offline"
    #: ..
    attribute_unix_permissions = "attribute_unix_permissions"
    #: ..
    attribute_win_read_only = "attribute_win_read_only"
    #: ..
    attribute_win_system = "attribute_win_system"
    #: ..
    category_date = "category_date"
    #: ..
    category_path = "category_path"
    #: ..
    category_size = "category_size"
    #: ..
    category_attributes = "category_attributes"
    #: ..
    file_folder_file = "file_folder_file"
    #: ..
    file_folder_file_folder = "file_folder_file_folder"
    #: ..
    file_folder_folder = "file_folder_folder"
    #: ..
    mode_size_smaller = "mode_size_smaller"
    #: ..
    mode_size_smaller_equal = "mode_size_smaller_equal"
    #: ..
    mode_size_equal = "mode_size_equal"
    #: ..
    mode_size_larger_equal = "mode_size_larger_equal"
    #: ..
    mode_size_larger = "mode_size_larger"
    #: ..
    mode_path_contains = "mode_path_contains"
    #: ..
    mode_path_ends_with = "mode_path_ends_with"
    #: ..
    mode_path_match_pattern = "mode_path_match_pattern"
    #: ..
    mode_path_match_regex = "mode_path_match_regex"
    #: ..
    mode_path_starts_with = "mode_path_starts_with"
    #: ..
    position_before = "position_before"
    #: ..
    position_on = "position_on"
    #: ..
    position_after = "position_after"
    #: ..
    reference_date_current_date = "reference_date_current_date"
    #: ..
    reference_date_file_backup = "reference_date_file_backup"
    #: ..
    reference_date_folder_backup = "reference_date_folder_backup"
    #: ..
    reference_date_volume_backup = "reference_date_volume_backup"
    #: ..
    reference_date_fixed = "reference_date_fixed"
    #: ..
    timestamp_type_ctime = "timestamp_type_ctime"
    #: ..
    timestamp_type_mtime = "timestamp_type_mtime"
    #: ..
    timestamp_type_atime = "timestamp_type_atime"

    def __init__(self, key_id, category, file_folder, include_subfolders, truth):
        super(BackupFilterRuleCtrl, self).__init__()

        self._id = key_id
        self._category = category
        self._file_folder = file_folder
        self._include_subfolders = include_subfolders
        self._truth = truth

    def __repr__(self):
        """ *
        Building representational messages
        """
        out_subject = ""
        out_mode = ""
        out_size = ""
        out_object = ""
        out_subfolders = ""
        out_match_case = ""
        out_attribution = ""
        out_position = ""
        out_reference_date = ""
        out_offset = ""
        out_attribute = ""

        # file_folder
        if self._file_folder == self.file_folder_file:
            out_object = "<b>File</b> "
        elif self._file_folder == self.file_folder_file_folder:
            out_object = "<b>File/Folder</b> "
        elif self._file_folder == self.file_folder_folder:
            out_object = "<b>Folder</b> "
        # include_subfolders
        if self._include_subfolders:
            out_subfolders += ", incl. all enclosed items"

        # CATEGORY-SPECIFIC
        if isinstance(self, BackupFilterRuleSizeCtrl):
            out_subject = "<b>Size of</b> "
            if self._mode_size == self.mode_size_smaller:
                out_mode = "<b><</b> "
            if self._mode_size == self.mode_size_smaller_equal:
                out_mode = "<b><=</b> "
            if self._mode_size == self.mode_size_equal:
                out_mode = "<b>=</b> "
            if self._mode_size == self.mode_size_larger_equal:
                out_mode = "<b>>=</b> "
            if self._mode_size == self.mode_size_larger:
                out_mode = "<b>></b> "
            out_size = "<b>%s</b>" % (bs.utils.format_data_size(self._size), )
        elif isinstance(self, BackupFilterRulePathCtrl):
            out_subject = "<b>Path</b> of "
            if self._mode_path == self.mode_path_match_pattern:
                out_mode = "<b>matches pattern</b> "
            if self._mode_path == self.mode_path_starts_with:
                out_mode = "<b>starts with</b> "
            if self._mode_path == self.mode_path_ends_with:
                out_mode = "<b>ends with</b> "
            if self._mode_path == self.mode_path_contains:
                out_mode = "<b>contains</b> "
            if self._mode_path == self.mode_path_match_pattern:
                out_mode = "<b>matches pattern</b> "
            if self._mode_path == self.mode_path_match_regex:
                out_mode = "<b>matches regex</b> "
            if self._match_case:
                out_match_case = ", matching case"
            out_attribution = "<b>%s</b>" % (self._path_pattern, )
        elif isinstance(self, BackupFilterRuleDateCtrl):
            if self._timestamp_type == self.timestamp_type_ctime:
                out_subject = "<b>Creation time</b> of "
            elif self._timestamp_type == self.timestamp_type_mtime:
                out_subject = "<b>Modification time</b> of "
            elif self._timestamp_type == self.timestamp_type_atime:
                out_subject = "<b>Access time</b> of "
            if self._position == self.position_before:
                out_position = "is <b>before</b> "
            elif self._position == self.position_on:
                out_position = "is <b>on</b> "
            elif self._position == self.position_after:
                out_position = "is <b>after</b> "
            if self._reference_date_time_type == self.reference_date_current_date:
                out_reference_date = "<b>current date</b> "
            elif self._reference_date_time_type == self.reference_date_file_backup:
                out_reference_date = "<b>file backup</b> "
            elif self._reference_date_time_type == self.reference_date_folder_backup:
                out_reference_date = "<b>folder backup</b> "
            elif self._reference_date_time_type == self.reference_date_volume_backup:
                out_reference_date = "<b>volume backup</b> "
            elif self._reference_date_time_type == self.reference_date_fixed:
                out_reference_date = "<b>fixed date</b> "
            # offset
            if self._reference_date_time_offsets[1] == 1:
                out_offset += ", <b>%s year</b>" % (self._reference_date_time_offsets[1], )
            elif self._reference_date_time_offsets[1] > 1:
                out_offset += ", <b>%s years</b>" % (self._reference_date_time_offsets[1], )
            if self._reference_date_time_offsets[2] == 1:
                out_offset += ", <b>%s month</b>" % (self._reference_date_time_offsets[2], )
            elif self._reference_date_time_offsets[2] > 1:
                out_offset += ", <b>%s months</b>" % (self._reference_date_time_offsets[2], )
            if self._reference_date_time_offsets[3] == 1:
                out_offset += ", <b>%s week</b>" % (self._reference_date_time_offsets[3], )
            elif self._reference_date_time_offsets[3] > 1:
                out_offset += ", <b>%s weeks</b>" % (self._reference_date_time_offsets[3], )
            if self._reference_date_time_offsets[4] == 1:
                out_offset += ", <b>%s day</b>" % (self._reference_date_time_offsets[4], )
            elif self._reference_date_time_offsets[4] > 1:
                out_offset += ", <b>%s days</b>" % (self._reference_date_time_offsets[4], )
            if self._reference_date_time_offsets[5] == 1:
                out_offset += ", <b>%s hour</b>" % (self._reference_date_time_offsets[5], )
            elif self._reference_date_time_offsets[5] > 1:
                out_offset += ", <b>%s hours</b>" % (self._reference_date_time_offsets[5], )
            if self._reference_date_time_offsets[6] == 1:
                out_offset += ", <b>%s minute</b>" % (self._reference_date_time_offsets[6], )
            elif self._reference_date_time_offsets[6] > 1:
                out_offset += ", <b>%s minutes</b>" % (self._reference_date_time_offsets[6], )
            if self._reference_date_time_offsets[7] == 1:
                out_offset += ", <b>%s second</b>" % (self._reference_date_time_offsets[7], )
            elif self._reference_date_time_offsets[7] > 1:
                out_offset += ", <b>%s seconds</b>" % (self._reference_date_time_offsets[7], )
            if out_offset != "":
                out_offset = out_offset[2:]
                if self._reference_date_time_offsets[0] == 0:
                    out_offset += " <b>subsequent</b> to "
                if self._reference_date_time_offsets[0] == -1:
                    out_offset += " <b>prior</b> to "
        elif isinstance(self, BackupFilterRuleAttributesCtrl):
            if self._attribute_type == self.attribute_hidden:
                out_attribute_tmp = "<b>hidden</b> "
            if self._attribute_type == self.attribute_group:
                out_attribute_tmp = "<b>group</b> "
            if self._attribute_type == self.attribute_owner:
                out_attribute_tmp = "<b>owner</b> "
            elif self._attribute_type == self.attribute_win_archive:
                out_attribute_tmp = "<b>archive</b> "
            elif self._attribute_type == self.attribute_win_encrypted:
                out_attribute_tmp = "<b>encrypted</b> "
            elif self._attribute_type == self.attribute_win_offline:
                out_attribute_tmp = "<b>offline</b> "
            elif self._attribute_type == self.attribute_unix_permissions:
                out_attribute_tmp = "<b>permissions</b> "
            elif self._attribute_type == self.attribute_win_read_only:
                out_attribute_tmp = "<b>read only</b> "
            elif self._attribute_type == self.attribute_win_system:
                out_attribute_tmp = "<b>system</b> "
            out_attribute = "has "
            out_attribute += out_attribute_tmp
            out_attribute += "flag set"

        out = out_subject
        out += out_object
        out += out_position
        out += out_offset
        out += out_reference_date
        out += out_mode
        out += out_size
        out += out_attribution
        out += out_attribute
        out += out_match_case
        out += out_subfolders
        return out

    @property
    def id(self):
        """ ..

        :type: `int`

        Holds the id of the backup-filter.
        """
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def category(self):
        """ ..

        :type: `string`

        Holds a ``enum`` of :class:`bs.ctrl.session.BackupFilterRuleCtrl`.
        """
        return self._category

    @category.setter
    def category(self, category):
        self._category = category

    @property
    def file_folder(self):
        """ ..

        :type: `enum`

        Holds an ``enum`` of :class:`bs.ctrl.session.BackupFilterRuleCtrl`.
        """
        return self._file_folder

    @file_folder.setter
    def file_folder(self, file_folder):
        self._file_folder = file_folder

    @property
    def include_subfolders(self):
        """ ..

        :type: `boolean`

        Holds ``boolean`` that expresses whether or not subfolders are to be \
        included.
        """
        return self._include_subfolders

    @include_subfolders.setter
    def include_subfolders(self, include_subfolders):
        self._include_subfolders = include_subfolders

    @property
    def truth(self):
        """ ..

        :rtype: `boolean`

        Holds the truth value about this rule, as in "does/does not" and \
        "is/is not" respectively.
        """
        return self._truth

    @truth.setter
    def truth(self, truth):
        self._truth = truth


class BackupFilterRuleAttributesCtrl(BackupFilterRuleCtrl):
    """ ..

    :param int id: The filter-rule-attribute's ID.

    :param enum category: A *category* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum file_folder: A *file_folder* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum include_subfolders: An *include_subfolders* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param boolean truth: Indicates whether the rule is set to true ("is set") \
    or false ("is not set")

    :param enum attribute: An *attribute* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    This class represent a *file-attribute filter* that is set for a
    :class:`~bs.ctrl.session.BackupFilterCtrl`.

    **Inherits from:** :class:`~bs.ctrl.session.BackupFilterRuleCtrl`
    """
    _attribute_type = None  # owner, group, backup flag, hidden flag/file prefix
    _attribute_value = None  # list: [<username> | <group>] | [<x>, <w>, <r>]

    def __init__(self, key_id, category, file_folder, include_subfolders, truth,
                 attribute_type, attribute_value):
        super(BackupFilterRuleAttributesCtrl, self).__init__(key_id,
                                                             category,
                                                             file_folder,
                                                             include_subfolders,
                                                             truth)

        self._attribute_type = attribute_type
        self._attribute_value = attribute_value

    @property
    def attribute_type(self):
        """
        :type: *enum*

        The attribute type set on this object.
        """
        return self._attribute_type

    @attribute_type.setter
    def attribute_type(self, attribute_type):
        self._attribute_type = attribute_type

    @property
    def attribute_value(self):
        """ ..

        :type: *list*: [<str username> | <str group>] | [<int x>, <int w>, <int r>]

        The attribute value set on this object.
        """
        return self._attribute_value

    @attribute_value.setter
    def attribute_value(self, attribute_value):
        self._attribute_value = attribute_value


class BackupFilterRuleDateCtrl(BackupFilterRuleCtrl):
    """ ..

    :param int id: The filter-rule-attribute's ID.

    :param enum category: A *category* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum file_folder: A *file_folder* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum include_subfolders: An *include_subfolders* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param boolean truth: Indicates whether the rule is set to true \
    ("is set") or false ("is not set")

    :param enum timestamp_type: A *typestamp_type* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum position: A *position* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum reference_date_time_type: A *reference_date* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param int reference_date_time_timestamp: The unix timestamp of \
    the offset for a fixed reference date/time.

    :param list reference_date_time_offsets: A list of offsets in the \
    following format: \
    ``[<int negative/positive>, <int years>, <int months>, <int weeks>, <int days>, <int hours>, <int minutes>, <int seconds>]``

    This class represent a *date filter* that is set for a
    :class:`~bs.ctrl.session.BackupFilterCtrl`.

    **Inherits from:** :class:`~bs.ctrl.session.BackupFilterRuleCtrl`
    """
    _timestamp_type = None  # cdate, ctime, mdate, mtime, ...
    _position = None  # before, on, after, exactly
    _reference_date_time_type = None  # current date, file, folder, volume backup, fixed date, ...
    _reference_date_time_timestamp = None  # the timestamp for a fixed date.
    _reference_date_time_offsets = None  # time offset in milliseconds

    def __init__(self, key_id, category, file_folder, include_subfolders, truth,
                 timestamp_type, position, reference_date_time_type,
                 reference_date_time_timestamp, reference_date_time_offsets):
        super(BackupFilterRuleDateCtrl, self).__init__(key_id,
                                                       category,
                                                       file_folder,
                                                       include_subfolders,
                                                       truth)

        self._timestamp_type = timestamp_type
        self._position = position
        self._reference_date_time_type = reference_date_time_type
        self._reference_date_time_timestamp = reference_date_time_timestamp
        self._reference_date_time_offsets = reference_date_time_offsets

    @property
    def position(self):
        """
        :type: *enum*

        The position value set on this object.
        """
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def reference_date_time_offsets(self):
        """
        :type: *enum*

        The time-offset value set on this object.
        """
        return self._reference_date_time_offsets

    @reference_date_time_offsets.setter
    def reference_date_time_offsets(self, reference_date_time_offsets):
        self._reference_date_time_offsets = reference_date_time_offsets

    @property
    def reference_date_time_timestamp(self):
        """
        :type: *enum*

        The timestamp for a fixed reference-time set on this object.
        """
        return self._reference_date_time_timestamp

    @reference_date_time_timestamp.setter
    def reference_date_time_timestamp(self, reference_date_time_timestamp):
        self._reference_date_time_timestamp = reference_date_time_timestamp

    @property
    def reference_date_time_type(self):
        """
        :type: *enum*

        The reference-date value set on this object.
        """
        return self._reference_date_time_type

    @reference_date_time_type.setter
    def reference_date_time_type(self, reference_date_time_type):
        self._reference_date_time_type = reference_date_time_type

    @property
    def timestamp_type(self):
        """
        :type: *enum*

        The timestamp-type value set on this object.
        """
        return self._timestamp_type

    @timestamp_type.setter
    def timestamp_type(self, timestamp_type):
        self._timestamp_type = timestamp_type


class BackupFilterRulePathCtrl(BackupFilterRuleCtrl):
    """ ..

    :param int id: The filter-rule-attribute's ID.

    :param enum category: A *category* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum file_folder: A *file_folder* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum include_subfolders: An *include_subfolders* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param boolean truth: Indicates whether the rule is set to true ("is set") \
    or false ("is not set")

    :param enum mode_path: A *mode-path* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param bool match_case: If `True`, filter will be evaluated case-sensitively.

    :param str path_pattern: The (file-/directory path-)pattern that is to be \
    matched.

    This class represent a *file-/directory-path filter* that is set for a
    :class:`~bs.ctrl.session.BackupFilterCtrl`.

    **Inherits from:** :class:`~bs.ctrl.session.BackupFilterRuleCtrl`
    """
    _mode_path = None  # contains, starts with, ends with, ...
    _match_case = None  # bool
    _path_pattern = None  # pattern, path, regex, ...

    def __init__(self, key_id, category, file_folder, include_subfolders, truth,
                 mode_path, match_case, path_pattern):
        super(BackupFilterRulePathCtrl, self).__init__(key_id,
                                                       category,
                                                       file_folder,
                                                       include_subfolders,
                                                       truth)

        self._mode_path = mode_path
        self._match_case = match_case
        self._path_pattern = path_pattern

    @property
    def mode_path(self):
        """
        :type: *enum*

        The mode the :attr:`path_pattern` is evaluated as.
        """
        return self._mode_path

    @mode_path.setter
    def mode_path(self, mode_path):
        self._mode_path = mode_path

    @property
    def match_case(self):
        """
        :type: *bool*

        If `True`, file-/directory paths will be evaluated case-sensitively.
        """
        return self._match_case

    @match_case.setter
    def match_case(self, match_case):
        self._match_case = match_case

    @property
    def path_pattern(self):
        """
        :type: *str*

        The (file-/directory path-)pattern that is to be matched.
        """
        return self._path_pattern

    @path_pattern.setter
    def path_pattern(self, path_pattern):
        self._path_pattern = path_pattern


class BackupFilterRuleSizeCtrl(BackupFilterRuleCtrl):
    """ ..

    :param int id: The filter-rule-attribute's ID.

    :param enum category: A *category* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum file_folder: A *file_folder* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param enum include_subfolders: An *include_subfolders* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param boolean truth: Indicates whether the rule is set to true ("is set") \
    or false ("is not set")

    :param enum mode_size: A *mode_size* enum on \
    :class:`~bs.ctrl.session.BackupFilterRuleCtrl`

    :param int size: The *data-size* in bytes to be compared against.

    This class represent a *file-/directory-size filter* that is set for a
    :class:`~bs.ctrl.session.BackupFilterCtrl`.

    **Inherits from:** :class:`~bs.ctrl.session.BackupFilterRuleCtrl`
    """
    _mode_size = None  # >, >=, =, <=, <
    _size = None  # int bytes

    def __init__(self, key_id, category, file_folder, include_subfolders, truth,
                 mode_size, size):
        super(BackupFilterRuleSizeCtrl, self).__init__(key_id,
                                                       category,
                                                       file_folder,
                                                       include_subfolders,
                                                       truth)

        self._mode_size = mode_size
        self._size = size

    @property
    def mode_size(self):
        """
        :type: *enum*

        The mode the size attribution is evaluated as.
        """
        return self._mode_size

    @mode_size.setter
    def mode_size(self, mode_size):
        self._mode_size = mode_size

    @property
    def size(self):
        """
        :type: *int*

        The size to be used as reference, in bytes.
        """
        return self._size

    @size.setter
    def size(self, size):
        self._size = size


class BackupSetCtrl(bs.model.models.Sets):
    """ ..

    :param bs.ctrl.session.SessionCtrl session: The :class:`~bs.ctrl.session.SessionCtrl` this set-controller \
    is accessed in.

    :param int set_id: The set's unique ID.

    :param str set_uid: The set's UID. The UID is used as a unique identifier \
    in *external* contexts (in contrast to internal identification such as \
    the database) and will be used as a name for the parent-folder that \
    groups all archive files belonging to the set.

    :param str set_name: The set's name.

    :param str salt_dk: The *derived key* to the set's encryption key as \
    stored in the database e.g.

    :param  str set_db_path: The set's database path.

    :param list source_objs: A list of :class:`~bs.ctrl.session.BackupSourceCtrl` associated \
    with the set.

    :param list filter_objs: A list of :class:`~bs.ctrl.session.BackupFilterCtrl` associated \
    with the set.

    :param list target_objs: A list of :class:`~bs.ctrl.session.BackupTargetCtrl` associated \
    with the set.
    """
    _session = None
    _backup_set_id = None
    _set_uid = None
    _set_name = None
    _salt_dk = None
    _set_db_path = None
    _backup_sources = None
    _backup_filters = None
    _backup_targets = None
    _gui_data = None

    _authentication_thread = None
    _authentication_worker = None
    _backup_ctrls = None
    _is_authenticated = None
    _key_hash_32 = None

    def __init__(self, session, set_id, set_uid, set_name, salt_dk,
                 set_db_path, source_objs, filter_objs, target_objs):
        self._session = session
        self._backup_set_id = set_id
        self._set_uid = set_uid
        self._set_name = set_name
        self._salt_dk = salt_dk
        self._set_db_path = set_db_path
        self._backup_sources = source_objs
        self._backup_filters = filter_objs
        self._backup_targets = target_objs

        # build backup_ctrls
        self._backup_ctrls = {}
        for backup_source in self._backup_sources:
            self._backup_ctrls[backup_source] = bs.ctrl.backup.BackupCtrl(self,
                                                                          backup_source)
        # if set_id == None, this is a new set, add to database
        if not self._backup_set_id:
            target_ids_list = []
            for target_obj in target_objs:
                target_ids_list.append(target_obj._target_id)
            res = self._add("user_id, set_uid, set_name, salt_dk, set_db_path, source_ass, filter_ass, targets, gui_data",
                            (self._session.user.id,
                             set_uid,
                             set_name,
                             salt_dk,
                             set_db_path,
                             json.dumps({}),
                             json.dumps({}),
                             json.dumps(target_ids_list),
                             json.dumps({})
                             )
                            )
            self._backup_set_id = res.lastrowid
            # create db file
            conn = sqlite3.connect(set_db_path)
            conn.close()

    def __repr__(self):
        return "Sets #%d id(%d) <%s>" % (self._backup_set_id,
                                         id(self),
                                         self.__class__.__name__, )

    @property
    def backup_set_id(self):
        """
        :type: *int*

        The set's internal ID.
        """
        return self._backup_set_id

    @property
    def set_uid(self):
        """
        :type: *str*

        The set's UID.
        """
        return self._set_uid

    @property
    def set_name(self):
        """ ..

        :type: *str*
        :permissions: *read/write*

        The set's name.
        """
        return self._set_name

    @set_name.setter
    def set_name(self, set_name):
        # VERIFY DATA
        # set name
        if not re.match(bs.config.REGEX_PATTERN_NAME, set_name):
            logging.warning("%s: The name contains invalid characters. It "
                            "needs to start  with an alphabetic and contain "
                            "alphanumerical characters plus '\_\-\#' and "
                            "space." % (self.__class__.__name__, ))
            return False
        # set new name
        self._set_name = set_name
        # update db
        self._update((("set_name", set_name, ), ),
                     (("id", "=", self._backup_set_id, ), )
                     )

    @property
    def salt_dk(self):
        """
        :type: *str*

        The set's *derived key* used to en-/decrypt the set's data.
        """
        return self._salt_dk

    @property
    def set_db_path(self):
        """ ..

        :type: *str*
        :permissions: *read/write*

        The absolute file-system path that points to the set's database.
        """
        if os.path.exists(self._set_db_path):
            if not os.path.isfile(self._set_db_path):
                e = IOError()
                e.filename = self._set_db_path
                e.strerror = "Not a file or file not accessible."
                raise e
            else:
                return self._set_db_path
        else:
            e = IOError()
            e.filename = self._set_db_path
            e.strerror = "File not found."
            raise e

    @set_db_path.setter
    def set_db_path(self, set_db_path):
        """ ..

        """
        # validate existence of path
        if not os.path.isfile(self._set_db_path):
            set_db_path_new = ""
            while not os.path.isfile(set_db_path_new):
                set_db_path_new = input("The last used path ('%s') is "
                                        "invalid; please enter the current "
                                        "path of this set's database:"
                                        % (self._set_db_path, ))
            self._set_db_path = set_db_path_new
            # update db
            self._update((("set_db_path", set_db_path_new, ), ),
                         (("id", "=", self._backup_set_id, ), )
                         )
        return True

    @property
    def backup_sources(self):
        """ ..

        :type: *list*

        A list of :class:`~bs.ctrl.session.BackupSourceCtrl` set for this set.
        """
        return self._backup_sources

    @property
    def backup_filters(self):
        """ ..

        :type: *list*

        A list of :class:`~bs.ctrl.session.BackupFilterCtrl` set for this set.
        """
        return self._backup_filters

    @property
    def backup_targets(self):
        """ ..

        :type: *list*
        :permissions: *read/write*

        A list of :class:`~bs.ctrl.session.BackupTargetCtrl` set as *backup-targets* for \
        this set.
        """
        return self._backup_targets

    @backup_targets.setter
    def backup_targets(self, target_objs):
        # VALIDATE DATA
        # set_objs
        check = False
        if not isinstance(target_objs, (list, tuple, )):
            check = True
        else:
            for target_obj in target_objs:
                if not isinstance(target_obj, BackupTargetCtrl):
                    check = True
        if check:
            logging.warning("%s: The first argument needs to be a list or "
                            "tuple of backup target objects."
                            % (self.__class__.__name__, ))
            return False
        # set targets
        self._targets = target_objs
        # update db
        target_ids_list = [x._target_id for x in target_objs]
        self._update((("targets", json.dumps(target_ids_list)), ),
                     (("id", "=", self._backup_set_id, ), ))

    @property
    def gui_data(self):
        """ ..

        :type: *list*

        This associative array holds gui-specific data such as \
        node-coordinates and anything that might be added in the future.
        """
        if not self._gui_data:
            # get data from db
            res = self._get("gui_data",
                            (("id", "=", self.backup_set_id, ), ))
            gui_data = json.loads(res[0][0])
            self._gui_data = gui_data
        return self._gui_data

    @property
    def backup_ctrls(self):
        """
        :type: *list*

        A list of :class:`~bs.ctrl.backup.BackupCtrl` associated with the set.
        """
        return self._backup_ctrls

    @property
    def is_authenticated(self):
        """
        :type: *bool*

        If `True`, user is authenticated with the set.
        """
        if self._is_authenticated:
            return True
        else:
            return False

    @property
    def key_hash_32(self):
        """
        :type: *str*

        If authenticated, this field stores the encryption key
        that the set is encrypted with. Is derived from the set's password.
        """
        return self._key_hash_32

    def add_backup_source(self, backup_source):
        """ ..

        :rtype: *void*

        Adds a backup-source to this backup-set.
        """
        # add backup_source as member to this set
        if backup_source not in self.backup_sources:
            self.backup_sources.append(backup_source)
        # add set association to backup_source
        if self not in backup_source.backup_entity_ass.keys():
            backup_source.backup_entity_ass[self] = []
        # add backup_ctrl for new source
        if backup_source not in self._backup_ctrls.keys():
            self._backup_ctrls[backup_source] = bs.ctrl.backup.BackupCtrl(self, backup_source)

    def add_backup_filter(self, backup_filter):
        """ ..

        :param bs.ctrl.session.BackupFilterCtrl backup_filter: The \
        :class:`~bs.ctrl.session.BackupFilterCtrl` to add to the set.
        :rtype: *void*

        Adds a backup-filter to this backup-set.
        """
        # add backup_filter as member to this set
        if backup_filter not in self.backup_filters:
            self.backup_filters.append(backup_filter)
        # add set association to backup_filter
        if self not in backup_filter.backup_entity_ass.keys():
            backup_filter.backup_entity_ass[self] = []

    def authenticate(self, key_raw):
        """ ..

        :param str key_raw: The set's password.
        :rtype: *AuthWorker* (inner class, refer to source-code)

        Returns an ``AuthWorker`` object, which can then be used to \
        ``start()`` a thread that verifies the login ``key_raw`` and unlocks \
        the backup-set on success.
        """
        class AuthWorker(QtCore.QObject):
            _backup_set = None
            _key_raw = None
            _salt_dk = None
            _thread = None
            finished = QtCore.Signal()
            started = QtCore.Signal()

            def __init__(self, backup_set, key_raw, salt_dk, thread):
                super(AuthWorker, self).__init__()

                self._backup_set = backup_set
                self._key_raw = key_raw
                self._salt_dk = salt_dk
                self._thread = thread

                self.moveToThread(self._thread)
                self._thread.started.connect(self.started.emit)
                self._thread.started.connect(self._process)
                self._thread.finished.connect(self.finished.emit)
                self._thread.finished.connect(self._thread.deleteLater)

            def _process(self):
                # Calculate PBKDF2 ciphers
                dk_bin = Crypto.Protocol.KDF.PBKDF2(self._key_raw,
                                                    binascii.unhexlify(self._salt_dk[:128]),
                                                    dkLen=32,
                                                    count=16000)
                # compare hash of entered key against hash_64 in db/on set-obj
                dk_hex = binascii.hexlify(dk_bin).decode("utf-8")
                if dk_hex == self._salt_dk[128:]:
                    self._backup_set._is_authenticated = True
                    self._backup_set._key_hash_32 = hashlib.sha256(key_raw.encode()).hexdigest()
                else:
                    logging.warning("%s: The password is invalid."
                                    % (self.__class__.__name__, ))
                self._thread.quit()

            def start(self):
                self._thread.start()

        if (not self._authentication_thread or
                self._authentication_thread.isFinished()):

            def reset_refs():
                self._authentication_thread = None

            self._authentication_thread = QtCore.QThread()
            self._authentication_thread.finished.connect(reset_refs,
                                                         QtCore.Qt.QueuedConnection)
            self._authentication_worker = AuthWorker(self,
                                                     key_raw,
                                                     self._salt_dk,
                                                     self._authentication_thread)
        return self._authentication_worker

    def remove_backup_source(self, backup_source):
        """ ..

        :param bs.ctrl.session.BackupSourceCtrl: The \
        :class:`~bs.ctrl.session.BackupSourceCtrl` to remove from the set.
        :rtype: *void*

        Removes a backup-source from this backup-set.
        """
        backup_source_id = backup_source.source_id
        backup_sources_list_new = []
        # remove object from self.sources
        self._backup_sources.pop(self._backup_sources.index(backup_source))
        # compile new list for db
        for backup_source_in_current_set in [x.backup_source_id for x in self._backup_sources]:
            if not backup_source_in_current_set == backup_source_id:
                backup_sources_list_new.append(backup_source_in_current_set)
        # update db
        self._update((("sources", json.dumps(backup_sources_list_new), ), ),
                     (("id", "=", self.backup_set_id, ), ))

    def save_to_db(self):
        """ ..

        :rtype: *bool*

        Explicitly commits the source's state to the database.
        """
        logging.debug("%s: Saving gui_data to db..."
                      % (self.__class__.__name__, ))
        # gui_data
        self._update((("gui_data", json.dumps(self.gui_data)), ),
                     (("id", "=", self.backup_set_id, ), ))
        # source_ass
        source_ass = {}
        for backup_source in self.backup_sources:
            associated_objs = backup_source.backup_entity_ass[self]
            associated_obj_ids = []
            for associated_obj in associated_objs:
                if associated_obj:
                    # if ass: filter
                    if isinstance(associated_obj, BackupFilterCtrl):
                        associated_obj_id = associated_obj.backup_filter_id
                    # if ass: targets
                    elif (isinstance(associated_obj, list) and
                          isinstance(associated_obj[0], BackupTargetCtrl)):
                        associated_obj_id = -1
                    associated_obj_ids.append(associated_obj_id)
            # if ass: None
            if associated_objs == []:
                associated_obj_ids = []
            source_ass[str(backup_source.backup_source_id)] = associated_obj_ids
        self._update((("source_ass", json.dumps(source_ass)), ),
                     (("id", "=", self.backup_set_id, ), ))
        # filter_ass
        filter_ass = {}
        for backup_filter in self.backup_filters:
            associated_objs = backup_filter.backup_entity_ass[self]
            associated_obj_ids = []
            for associated_obj in associated_objs:
                if associated_obj:
                    # if ass: filter
                    if isinstance(associated_obj, BackupFilterCtrl):
                        associated_obj_id = associated_obj.backup_filter_id
                    # if ass: targets
                    elif (isinstance(associated_obj, list) and
                          isinstance(associated_obj[0], BackupTargetCtrl)):
                        associated_obj_id = -1
                    associated_obj_ids.append(associated_obj_id)
            # if ass: None
            if associated_objs == []:
                associated_obj_ids = []
            filter_ass[str(backup_filter.backup_filter_id)] = associated_obj_ids
        self._update((("filter_ass", json.dumps(filter_ass)), ),
                     (("id", "=", self.backup_set_id, ), ))
        logging.debug("%s: gui_data successfully saved to db."
                      % (self.__class__.__name__, ))
        return True


class BackupSetsCtrl(bs.model.models.Sets):
    """ ..

    :param SessionCtrl session: The session these sets belong to.

    Encapsulates all sets that are associated with a
    :class:`~bs.ctrl.session.SessionCtrl`.
    """
    _session = None
    _sets = None

    def __init__(self, session):
        super(BackupSetsCtrl, self).__init__()
        self._session = session

        self._sets = []

    def __repr__(self):
        return "Sets <%s>" % (self.__class__.__name__)

    @property
    def sets(self):
        """ ..

        :type: *list*

        The list of :class:`~bs.ctrl.session.BackupSetCtrl` that are associated with its
        session.
        """
        # sets list is empty, load from db
        if len(self._sets) == 0:
            res = self._get("id, set_uid, set_name, salt_dk, set_db_path, source_ass, filter_ass, targets",
                            (("user_id", "=", self._session.user.id, ), ))
            for data_set in res:
                set_id = data_set[0]
                set_uid = data_set[1]
                set_name = data_set[2]
                salt_dk = data_set[3]
                set_db_path = data_set[4]
                source_objs = []
                for source_id in json.loads(data_set[5]):
                    source_id = int(source_id)
                    for backup_source_obj in self._session.backup_sources.backup_sources:
                        if backup_source_obj.backup_source_id == source_id:
                            source_objs.append(backup_source_obj)
                filter_objs = []
                for filter_id in json.loads(data_set[6]):
                    filter_id = int(filter_id)
                    for filter_obj in self._session.backup_filters.backup_filters:
                        if filter_obj.backup_filter_id == filter_id:
                            filter_objs.append(filter_obj)
                target_objs = []
                for target_obj in self._session.backup_targets.targets:
                    if target_obj._target_id in json.loads(data_set[7]):
                        target_objs.append(target_obj)

                new_set_obj = BackupSetCtrl(self._session,
                                            set_id,
                                            set_uid,
                                            set_name,
                                            salt_dk,
                                            set_db_path,
                                            source_objs,
                                            filter_objs,
                                            target_objs)
                self._sets.append(new_set_obj)
        return self._sets

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def create_backup_set(self, set_name, key_raw, set_db_path, source_objs, filter_objs, target_objs):
        """ ..

        :param str set_name: The printed name for the new set.

        :param str key_raw: The password used for encryption of the set.

        :param str set_db_path: The absolute file-path where the \
        *backup-set*'s database will be created.

        :param list source_objs: A list of :class:`~bs.ctrl.session.BackupSourceCtrl` to \
        associate with the set.

        :param list filter_objs: A list of :class:`~bs.ctrl.session.BackupFilterCtrl` to \
        associate with the set.

        :param list target_objs: A list of :class:`~bs.ctrl.session.BackupTargetCtrl` to \
        associate with the set.

        :rtype: *boolean*

        Raises an `Exception` with a tuple as its ``args`` field that contains
        a boolean value for each of the following test outcomes:
        ``((<set_name_valid>, <msg>), (<key_raw_valid>, <msg>), (<set_db_path_valid>, <msg>), (<target_objs_valid>, <msg>))``

        Creates a new (empty) backup-set.
        """
        # VALIDATE DATA
        set_name_valid = True
        set_name_msg = ""
        key_raw_valid = True
        key_raw_msg = ""
        set_db_path_valid = True
        set_db_path_msg = ""
        target_objs_valid = True
        target_objs_msg = ""
        # set_name
        if not re.match(bs.config.REGEX_PATTERN_NAME, set_name):
            msg = "The name contains invalid characters: It needs to "\
                  "start with an alphabetical character and continue with "\
                  "alphanumerical characters, plus _ - # and space."
            logging.warning("%s: %s" % (self.__class__.__name__, msg, ))
            set_name_valid = False
            set_name_msg = msg
        # key_raw
        if not re.match(bs.config.REGEX_PATTERN_KEY, key_raw):
            msg = "The password contains invalid characters and/or is of "\
                  "invalid length. Valid characters are alphanumerical with a "\
                  "length between 8 and 128 characters."
            logging.warning("%s: %s" % (msg, self.__class__.__name__, ))
            key_raw_valid = False
            key_raw_msg = msg
        else:
            salt_dk = hashlib.sha512(key_raw.encode()).hexdigest()
        # set_db_path
        check = False
        msg = ""
        if not isinstance(set_db_path, str):
            check = True
            msg = "The given database-path is not of type string."
        elif not os.path.isdir(os.path.dirname(set_db_path)):
            check = True
            msg = "The given database-path does not point to an existing "\
                  "folder."
        elif not re.match(".*\.sqlite$", set_db_path):
            check = True
            msg = "The given database-path does not have the required .sqlite "\
                  "extension."
        elif os.path.isfile(set_db_path):
            check = True
            msg = "The given database-path points to an already existing file."
        else:
            try:
                with open(set_db_path, "w") as f:
                    f.write(".")
                    os.unlink(set_db_path)
            except:
                check = True
                msg = "The location the database-path points to cannot be "\
                      "written to."
        if check:
            logging.warning("%s: %s" % (msg, self.__class__.__name__, ))
            set_db_path_valid = False
            set_db_path_msg = msg
        # source_objs
        if not isinstance(source_objs, (list, tuple)):
            check = True
        else:
            for source_obj in source_objs:
                if not isinstance(source_obj, BackupSourceCtrl):
                    check = True
        # filter_objs
        if not isinstance(filter_objs, (list, tuple)):
            check = True
        else:
            for filter_obj in filter_objs:
                if not isinstance(filter_obj, BackupFilterCtrl):
                    check = True
        # target_objs
        if len(target_objs) == 0:
            msg = "At least one target needs to be added to the new backup-set."
            logging.warning("%s: %s" % (msg, self.__class__.__name__, ))
            target_objs_valid = False
            target_objs_msg = msg
            check = True
        else:
            for target_obj in target_objs:
                if not isinstance(target_obj, BackupTargetCtrl):
                    check = True
        # raise exception if necessary
        if (not set_name_valid or not key_raw_valid or not set_db_path_valid or
                not target_objs_valid):
            e = Exception()
            e.args = ((set_name_valid, set_name_msg),
                      (key_raw_valid, key_raw_msg),
                      (set_db_path_valid, set_db_path_msg),
                      (target_objs_valid, target_objs_msg)
                      )
            raise(e)

        if check:
            logging.warning("%s: The second, thrid and fourth arguments need "
                            "to be a list or tuple of backup "
                            "source/filter/target object respectively."
                            % (self.__class__.__name__, ))
            return False
        # ADD OBJ
        set_id = None
        # set_uid
        set_uid = None
        check = False
        conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
        while not check:
            # generate (new) set_uid
            timestamp = str(int(time.time() * 1000000))
            random_num = str(random.randint(1000000000000000, 9999999999999999))
            timestamp_random_num = timestamp + random_num
            set_uid = hashlib.md5(timestamp_random_num.encode()).hexdigest()
            # check if unique in db
            res = conn.execute("SELECT id FROM sets WHERE set_uid = ?",
                               (set_uid, )).fetchall()
            if len(res) == 0:
                check = True
                break
            time.sleep(0.005)
        conn.close()
        new_set_obj = BackupSetCtrl(self._session,
                                    set_id,
                                    set_uid,
                                    set_name,
                                    salt_dk,
                                    set_db_path,
                                    source_objs,
                                    filter_objs,
                                    target_objs)
        self._sets.append(new_set_obj)
        # out
        return True

    def delete_backup_set(self, backup_set):
        """ ..

        :param bs.ctrl.session.BackupSetCtrl backup_set: The \
        :class:`~bs.ctrl.session.BackupSetCtrl` to permanently delete.
        :rtype: *bool*

        Deletes an existing backup-set.
        """
        # VALIDATE DATA
        # backup_set
        if not isinstance(backup_set, BackupSetCtrl):
            logging.warning("%s: The first argument needs to be of "
                            "type BackupSetCtrl."
                            % (self.__class__.__name__, ))
            return False
        backup_set_id = backup_set.backup_set_id
        # delete from DB
        self._remove((("id", "=", backup_set_id, ), ))
        # remove corresponding object from self._sets
        for b_set in self._sets:
            if b_set == backup_set:
                self._sets.pop(self._sets.index(b_set))
        # out
        return True


class BackupSourceCtrl(bs.model.models.Sources):
    """ ..

    :param bs.ctrl.session.SessionGuiCtrl session_gui: The GUI controller \
    associated with current session.

    :param int backup_source_id: The *backup-source's* ID.

    :param str source_name: The *backup-source's* name.

    :param str source_path: The absolute folder-path that defines the \
    *backup-source*.

    This class defines a single source in the file-system, which is usually a \
    folder-location.
    """
    _session = None
    _backup_source_id = None
    _source_name = None
    _source_path = None

    _backup_entity_ass = None

    def __init__(self, session_gui, backup_source_id, source_name, source_path):
        self._session = session_gui
        self._backup_source_id = backup_source_id
        self._source_name = source_name
        self._source_path = source_path
        # if backup_source_id == None, this is a new source, add to database
        if not self._backup_source_id:
            res = self._add("user_id, source_name, source_path",
                            (self._session.user.id,
                             self._source_name,
                             self._source_path, ))
            self._backup_source_id = res.lastrowid

        self._backup_entity_ass = []

    def __repr__(self):
        return "Source #%d <%s>" % (self._backup_source_id, self.__class__.__name__, )

    @property
    def backup_source_id(self):
        """
        :type: *int*

        The *backup-source*'s ID.
        """
        return self._backup_source_id

    @property
    def source_name(self):
        """
        :type: *str*
        :permissions: *read/write*

        The *backup-source*'s name.
        """
        return self._source_name

    @source_name.setter
    def source_name(self, source_name):
        # VALIDATE DATA
        # source_name
        if not re.match(bs.config.REGEX_PATTERN_NAME, source_name):
            logging.warning("%s: The source_name contains invalid "
                            "characters. It needs to start  with an "
                            "alphabetic and contain alphanumerical "
                            "characters plus '\_\-\#' and space."
                            % (self.__class__.__name__, ))
            return False
        # change data in db
        self._update((("source_name", source_name), ),
                     (("id", "=", self._backup_source_id), )
                     )
        self._source_name = source_name
        # out
        return True

    @property
    def source_path(self):
        """
        :type: *str*
        :permissions: *read/write*

        The *backup_source*'s absolute folder-path in the file-system.
        """
        return self._source_path

    @source_path.setter
    def source_path(self, source_path):
        # VALIDATE DATA
        # source_path
        if not os.path.isdir(source_path):
            logging.warning("%s: The source-path is invalid. It needs to be "
                            "a valid directory-path on the current system."
                            % (self.__class__.__name__, ))
            return False
        # change data in db
        self._update((("source_path", source_path), ),
                     (("id", "=", self._backup_source_id), )
                     )
        self._source_path = source_path
        # out
        return True

    @property
    def backup_entity_ass(self):
        """ ..

        :type: *dict*

        Returns an associative array (dictionary) in the following format: \
        {:class:`~bs.ctrl.session.BackupSetCtrl`::class:`~bs.ctrl.session.BackupSourceCtrl`} or \
        {:class:`~bs.ctrl.session.BackupSetCtrl`::class:`~bs.ctrl.session.BackupTargetCtrl`}.
        """
        if not self._backup_entity_ass:
            backup_entity_ass = {}
            # Follows the "dumb" model: Sets don't know the associations, have to check the sets table here to get them
            conn = sqlite3.connect(bs.config.CONFIGDB_PATH)
            res = conn.execute("SELECT id, source_ass FROM sets WHERE user_id = ?", (self._session.user.id, )).fetchall()
            # run through set-results
            for dataset in res:
                set_id = dataset[0]
                source_ass_dict = json.loads(dataset[1])
                # get set object
                backup_set_obj = [x for x in self._session.backup_sets.sets if x.backup_set_id == set_id][0]
                # run through associations in set
                for backup_source_id in source_ass_dict:
                    if self.backup_source_id == int(backup_source_id):
                        # list to store associations for set in
                        if backup_set_obj not in backup_entity_ass.keys():
                            backup_entity_ass[backup_set_obj] = []
                        # this can be either -1 for the set's target set or a natural number as a source id
                        ass_ids = source_ass_dict[backup_source_id]
                        for ass_id in ass_ids:
                            # target set associated
                            if ass_id == -1:
                                backup_entity_ass[backup_set_obj].append(backup_set_obj.backup_targets)
                            # source associated
                            else:
                                # get source object with id that was found
                                for backup_filter_obj_iter in self._session.backup_filters.backup_filters:
                                    if backup_filter_obj_iter.backup_filter_id == ass_id:
                                        backup_entity_ass[backup_set_obj].append(backup_filter_obj_iter)
            self._backup_entity_ass = backup_entity_ass
        return self._backup_entity_ass

    def associate(self, backp_set, backup_entity):
        """ ..

        :param bs.ctrl.session.BackupSetCtrl backup_set: The *backup-set* for \
        which to associate the *backup-entity* with this *backup-source*.

        :param bs.model.models_master.BSModel backup_entity: The \
        *backup-entity* to associate with this *backup-source* on the \
        *backup-set*. This is one of the following: \
        :class:`~bs.ctrl.session.BackupFilterCtrl`, :class:`~bs.ctrl.session.BackupTargetsCtrl`

        :rtype: *void*

        Associates a *backup-entity* with this *backup-source*.
        """
        self._backup_entity_ass[backp_set].append(backup_entity)

    def disassociate(self, backup_set, backup_entity):
        """ ..

        :param bs.ctrl.session.BackupSetCtrl backup_set: The *backup-set* for \
        which to disassociate the *backup-entity* with this *backup-source*.

        :param bs.model.models_master.BSModel backup_entity: The \
        *backup-entity* to dissociate from this *backup-source*.

        :rtype: *void*

        Breaks connection to a given backup_entity_ass
        """
        self._backup_entity_ass[backup_set].pop(self._backup_entity_ass[backup_set].index(backup_entity))


class BackupSourcesCtrl(bs.model.models.Sources):
    """ ..

    :param SessionCtrl session: The :class:`~bs.ctrl.session.SessionCtrl` these \
    *backup-sources* are associated with.

    This class groups and manages all *backup-sources* for one *session*.
    """
    _session = None
    _backup_sources = None

    def __init__(self, session):
        """
        *
        """
        super(BackupSourcesCtrl, self).__init__()
        self._session = session

        self._backup_sources = []

    def __repr__(self):
        return "Sources <%s>" % (self.__class__.__name__, )

    @property
    def backup_sources(self):
        """ ..

        :type: *list*

        Returns all source objects that are associated with this \
        :class:`~bs.ctrl.session.BackupSourcesCtrl` and :class:`~bs.ctrl.session.SessionCtrl`.
        """
        # sources list is empty, load from db
        if not len(self._backup_sources):
            res = self._get("id, source_name, source_path",
                            (("user_id", "=", self._session.user.id, ), ))
            for data_set in res:
                source_id = data_set[0]
                source_name = data_set[1]
                source_path = data_set[2]
                new_source_obj = BackupSourceCtrl(self._session,
                                                  source_id,
                                                  source_name,
                                                  source_path)
                self._backup_sources.append(new_source_obj)
        return self._backup_sources

    # OVERLOADS
    @property
    def _add_is_permitted(self, *args, **kwargs):
        """..

        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    @property
    def _get_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    @property
    def _remove_is_permitted(self, *args, **kwargs):
        """
        *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def create_backup_source(self, source_name, source_path):
        """ ..

        :param str source_name: Name for the new *backup-source*.

        :param str source_path: Absolute file-system folder-path pointing \
        to the location to be defined as the new source.

        :rtype: *bool*

        Creates a new :class:`~bs.ctrl.session.BackupSourceCtrl`.
        """
        # VALIDATE DATA
        # source_name
        if not re.search(bs.config.REGEX_PATTERN_NAME, source_name):
            logging.warning("%s: The name contains invalid characters. It "
                            "needs to start  with an alphabetic and contain "
                            "alphanumerical characters plus '\_\-\#' and "
                            "space." % (self.__class__.__name__, ))
            return False
        # source_path
        if not os.path.isdir(source_path):
            logging.warning("%s: The source-path is invalid. It needs to be "
                            "a valid directory-path on the current system."
                            % (self.__class__.__name__, ))
            return False
        logging.info("%s: Adding source: '%s' (%s)"
                     % (self.__class__.__name__, source_name, source_path,))
        # check that the path does not already exist for current user.
        res = self._get("id", (("user_id", "=", self._session.user.id, ),
                               ("source_path", "=", source_path, ), ))
        if len(res) > 0:
            logging.warning("%s: This source-path is already defined: %s"
                            % (self.__class__.__name__, source_path, ))
            return False
        # add object
        source_id = None
        new_source_obj = BackupSourceCtrl(self._session,
                                          source_id,
                                          source_name,
                                          source_path)
        self._backup_sources.append(new_source_obj)
        logging.info("%s: Source successfully added: '%s' (%s)"
                     % (self.__class__.__name__, source_name, source_path))
        # out
        return True

    def delete_backup_source(self, source_obj):
        """ ..

        :param bs.ctrl.session.BackupSourceCtrl source_obj: The \
        *backup-source* to be deleted.

        :rtype: *bool*

        Deletes an existing :class:`~bs.ctrl.session.BackupSourceCtrl`.
        """
        # VALIDATE DATA
        # source_obj
        if not isinstance(source_obj, BackupSourceCtrl):
            logging.warning("%s: The first argument needs to be a backup "
                            "source object."
                            % (self.__class__.__name__, ))
            return False
        # remove data from database
        self._remove((("id", "=", source_obj._source_id, ), ))
        # delete obj
        self._backup_sources.pop(self._backup_sources.index(source_obj))
        # out
        logging.info("%s: Source has been successfully deleted: %s"
                     % (self.__class__.__name__, source_obj, ))
        return True


class BackupTargetCtrl(bs.model.models.Targets):
    """ ..

    :param bs.ctrl.session.SessionGuiCtrl session_gui: The \
    :class:`~bs.ctrl.session.SessionGuiCtrl` associated with the :class:`~bs.ctrl.session.SessionCtrl` this \
    *backup-target* is associated with.

    :param int target_id: The target's ID as used as a unique ID in the \
    database.

    :param str target_name: The target's literal name.

    :param str target_device_id: The *device-id* this target uses to uniquely \
    mark its location on the file-system. This decouples the target from the \
    physical drive-letter and makes it resistant against changing \
    drive-letters, which easily happens with removable storage e.g..

    This class defines a single target in the file-system, which is usually \
    needs to be the root of a drive that has valid backup-data on it.
    """
    _session = None
    _target_id = None
    _target_name = None
    _target_device_id = None
    # enums
    #: ..
    status_online = "status_online"
    #: ..
    status_offline = "status_offline"
    #: ..
    status_in_use = "status_in_use"

    def __init__(self, session_gui, target_id, target_name, target_device_id):
        self._session = session_gui
        self._target_id = target_id
        self._target_name = target_name
        self._target_device_id = target_device_id
        # if target_id == None, this is a new target, add to database
        if not self._target_id:
            res = self._add("user_id, target_name, target_device_id",
                            (self._session.user.id,
                             self._target_name,
                             self._target_device_id, ))
            self._target_id = res.lastrowid

    def __repr__(self):
        return "Target #%d <%s>" % (self._target_id, self.__class__.__name__, )

    @property
    def target_name(self):
        """
        :type: *str*
        :permissions: *read/write*

        The target's literal name.
        """
        return self._target_name

    @target_name.setter
    def target_name(self, target_name):
        """ * """
        # VALIDATE DATA
        # target_name
        if not re.match(bs.config.REGEX_PATTERN_NAME, target_name):
            logging.warning("%s: The target_name contains invalid "
                            "characters. It needs to start  with an "
                            "alphabetic and contain alphanumerical "
                            "characters plus '\_\-\#' and space."
                            % (self.__class__.__name__, ))
            return False
        # change data in db
        self._update((("target_name", target_name), ),
                     (("id", "=", self._target_id), )
                     )
        self._target_name = target_name
        # out
        return True

    @property
    def target_path(self):
        """ ..

        :type: *str*

        Gets physical path that currently points to target.

        Scans all connected drives and looks for valid backup folders that \
        contain the identifying metadata file with this target's \
        *target-device-ID*.

        Returns physical path that currently points to the target.
        """
        out = []
        for drive_root_path in bs.utils.get_drives(("fixed", )):
            target_config_file_path = os.path.join(drive_root_path,
                                                   bs.config.PROJECT_NAME,
                                                   "volume.json")
            if os.path.isfile(target_config_file_path):
                f = open(target_config_file_path, "r")
                data = f.read()
                target_device_id_drive = json.loads(data)[1]
                # if current target_device_id same as own device_id...
                if target_device_id_drive == self._target_device_id:
                    out.append(os.path.join(drive_root_path,
                                            bs.config.PROJECT_NAME))
                f.close()
        # out
        if len(out) > 1:
            logging.critical("%s: More than one drive carry the same ID. "
                             "Please make sure there are no duplicates on the "
                             "system: %s" % (self.__class__.__name__,
                                             out, ))
            raise SystemExit
        elif len(out) == 0:
            logging.info("%s: The physical location of this target could "
                         "not be found. The volume is probably offline "
                         " (target_device_id: %s)"
                         % (self.__class__.__name__,
                            self._target_device_id, ))
            return ""
        else:
            return out[0]


class BackupTargetsCtrl(bs.model.models.Targets):
    """ ..

    :param bs.ctrl.session.SessionGuiCtrl session_gui: The \
    :class:`~bs.ctrl.session.SessionCtrl` these *backup-targets* are associated with.

    This class groups and manages all *backup-targets* for one *session*.
    """
    _session = None
    _targets = None

    def __init__(self, session):
        super(BackupTargetsCtrl, self).__init__()
        self._session = session

        self._targets = []

    def __repr__(self):
        return "Targets <%s>" % (self.__class__.__name__)

    @property
    def targets(self):
        """ ..

        :type: *list*

        Returns a list of all :class:`bs.ctrl.session.BackupTargetCtrl` objects.
        """
        # targets list is empty, load from db
        if len(self._targets) == 0:
            res = self._get("id, target_name, target_device_id",
                            (("user_id", "=", self._session.user.id, ), ))
            for data_set in res:
                target_id = data_set[0]
                target_name = data_set[1]
                target_device_id = data_set[2]
                new_target_obj = BackupTargetCtrl(self._session,
                                                  target_id,
                                                  target_name,
                                                  target_device_id)
                self._targets.append(new_target_obj)
        return self._targets

    # OVERLOADS
    @property
    def _add_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    @property
    def _get_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False

    @property
    def _remove_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session._is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def create_backup_target(self, target_name, target_path):
        """ ..

        :param str target_name: The literal name to give to the new target.

        :param str target_path: The absolute drive-letter-path of the drive \
        to define the as the new target.

        :rtype: *bool*

        Creates a new *backup-target*.
        """
        # VERIFY DATA
        # target_name
        if not re.search(bs.config.REGEX_PATTERN_NAME, target_name):
            logging.warning("%s: The name contains invalid characters. It "
                            "needs to start  with an alphabetic and contain "
                            "alphanumerical characters plus '\_\-\#' and "
                            "space." % (self.__class__.__name__, ))
            return False
        # target_path
        if not re.search("^[a-zA-Z]\:\\\\$", target_path):
            logging.warning("%s: This is not a valid target path. Only "
                            "partition roots can be defined as targets."
                            % (self.__class__.__name__, ))
            return False
        # check if volume is already defined as target
        root_path = os.path.join(target_path,
                                 bs.config.PROJECT_NAME.capitalize())
        root_config_file_path = os.path.join(root_path, "volume.json")
        if (not os.path.isdir(root_path) and
                not os.path.isfile(root_config_file_path)):
            # generate target_device_id
            # timestamp at high sub-second-precision as string appended by
            # random 16-bit integer as string, encoded as HEX-SHA512
            timestamp = str(int(time.time() * 1000000))
            random_num = str(random.randint(1000000000000000, 9999999999999999))
            timestamp_random_num = timestamp + random_num
            target_device_id = hashlib.sha512(timestamp_random_num.encode()).hexdigest()
            # add obj
            target_id = None
            new_target_obj = BackupTargetCtrl(self._session,
                                              target_id,
                                              target_name,
                                              target_device_id)
            self._targets.append(new_target_obj)
            # create BS root directory on volume
            try:
                # create root_folder
                os.mkdir(root_path)
                with open(root_config_file_path, "w") as f:
                    json.dump([target_name, target_device_id], f)
                logging.info("%s: Target has been successfully created: %s"
                             % (self.__class__.__name__,
                                target_path, ))
                return True
            except Exception as e:
                logging.warning(bs.messages.general.general_error(e)[0])
                return False
        else:
            logging.warning("%s: This volume is already defined as a "
                            "target. Please try to importing it: %s"
                            % (self.__class__.__name__, target_path, ))
            return False

    def delete_backup_target(self, target_obj):
        """ ..

        :param bs.ctrl.session.BackupTargetCtrl target_obj: The \
        *backup-target* to delete.

        :rtype: *bool*

        Deletes an existing *backup-target*. Does **not** delete any \
        file-system data.
        """
        # VALIDATE DATA
        # target_obj
        if not isinstance(target_obj, BackupTargetCtrl):
            logging.warning("%s: The first argument needs to be a backup "
                            "target object."
                            % (self.__class__.__name__, ))
            return False
        # delete from DB
        self._remove((("id", "=", target_obj._target_id, ), ))
        # remove obj
        self._targets.pop(self._targets.index(target_obj))
        # out
        logging.info("%s: Target has been successfully removed; file-system "
                     "data has not been changed/removed: %s"
                     % (self.__class__.__name__,
                        target_obj, ))
        return True


class SessionCtrl(object):
    """

    :param bs.ctrl.session.SessionsCtrl sessions_ctrl: The central \
    :class:`bs.ctrl.session.SessionsCtrl` hosting this session.

    Stores and manages contents of a single session. user, sources, targets,
    filters, sets, etc..

    This class is not to be instantiated directly.
    :meth:`SessionsCtrl.add_session` should be used to add sessions.
    """
    _user = None
    _backup_sources = None
    _backup_targets = None
    _backup_filters = None
    _backup_sets = None
    _is_unlocked = None
    _is_logged_in = None
    _sessions_ctrl = None

    def __init__(self, sessions_ctrl):
        super(SessionCtrl, self).__init__()

        self._user = UserCtrl(self)
        self._backup_sources = BackupSourcesCtrl(self)
        self._backup_targets = BackupTargetsCtrl(self)
        self._backup_filters = BackupFiltersCtrl(self)
        self._backup_sets = BackupSetsCtrl(self)
        self._is_unlocked = False
        self._is_logged_in = False
        self._sessions_ctrl = sessions_ctrl

    def __repr__(self):
        return(str((self._user,
                    self._backup_sources,
                    self._backup_targets,
                    self._backup_filters,
                    self._backup_sets))
               )

    @property
    def user(self):
        """
        :type: :class:`~bs.ctrl.session.UserCtrl`

        The :class:`~bs.ctrl.session.UserCtrl` associated with this *backup-session*.
        """
        return self._user

    @property
    def backup_sources(self):
        """
        :type: *list*

        A list of *backup-sources* associated with this session.
        """
        return self._backup_sources

    @property
    def backup_targets(self):
        """
        :type: *list*

        A list of *backup-targets* associated with this session.
        """
        return self._backup_targets

    @property
    def backup_filters(self):
        """
        :type: *list*

        A list of *backup-filters* associated with this session.
        """
        return self._backup_filters

    @property
    def backup_sets(self):
        """
        :type: *list*

        A list of *backup-sets* associated with this session.
        """
        return self._backup_sets

    @property
    def is_unlocked(self):
        """
        :type: *bool*
        :permissions: *read/write*

        `False`, if this session is locked, `True` if unlocked.
        """
        return self._is_unlocked

    @is_unlocked.setter
    def is_unlocked(self, arg):
        if not isinstance(arg, bool):
            logging.warning("%s: The first argument needs to be of type "
                            "boolean."
                            % (self.__class__.__name__, ))
            return False
        self._is_unlocked = arg
        return True

    @property
    def is_logged_in(self):
        """
        :type: *bool*
        :permissions: *read/write*

        `True`, if this session's user is logged in, `False` if not.
        """
        return self._is_logged_in

    @is_logged_in.setter
    def is_logged_in(self, arg):
        if not isinstance(arg, bool):
            logging.warning("%s: Argument one needs to be of type boolean."
                            % (self.__class__.__name__, ))
            return False
        self._is_logged_in = arg
        return True

    def log_in(self, username, password):
        """ ..

        :param str username: The user's username to log-in with.
        :param str password: The user's password to log-in with.

        :rtype: *bool*

        Logs the user associated with this *backup-session* in.
        """
        # VALIDATE DATA
        # username
        if not re.search(bs.config.REGEX_PATTERN_USERNAME, username):
            logging.warning("%s: The username is invalid. A valid username "
                            "needs to start with an alphabetic, "
                            "contain alphanumeric plus '_' "
                            "and have a length between 4 and 32 characters."
                            % (self.__class__.__name__, ))
            return False
        # CONTEXT CHECKS & SET-UP
        if (not self.is_logged_in or
                self.is_logged_in and not self._is_unlocked):
            if self.user._validate_credentials(self, username, password):
                self.is_unlocked = True
                self.is_logged_in = True
                logging.info("%s: Session successfully logged in."
                             % (self.__class__.__name__, ))
                self._sessions_ctrl.session_activity_signal.emit()
                return True
            else:
                logging.warning("%s: Session login failed: Invalid credentials."
                                % (self.__class__.__name__, ))
                return False
        elif self.is_unlocked:
            logging.warning("%s: Session already logged in."
                            % (self.__class__.__name__, ))
            return False

    def log_out(self):
        """ ..

        :rtype: *bool*

        Logs the logged-in user out of this session.
        """
        if self.is_logged_in:
            # save sets
            for backup_set in self._backup_sets.sets:
                backup_set.save_to_db()
            self.is_unlocked = False
            self.is_logged_in = False
            logging.info("%s: Session successfully logged out."
                         % (self.__class__.__name__, ))
            self._sessions_ctrl.session_activity_signal.emit()
            return True
        else:
            logging.warning("%s: Session logout failed: Already logged out."
                            % (self.__class__.__name__, ))
            return False

    def lock(self):
        """ ..

        :rtype: *bool*

        Locks the session.
        """
        if self.is_logged_in:
            if self.is_unlocked:
                self.is_unlocked = False
                logging.info("%s: Session successfully locked."
                             % (self.__class__.__name__, ))
                self._sessions_ctrl.session_activity_signal.emit()
                return True
            else:
                logging.warning("%s: Session lock failed: Already locked."
                                % (self.__class__.__name__, ))
                return False
        else:
            logging.warning("%s: Session lock failed: Not logged in."
                            % (self.__class__.__name__, ))
            return False

    def unlock(self, username, password):
        """ ..

        :param str username: The user's username to log-in with.
        :param str password: The user's password to log-in with.

        :rtype: *bool*

        Unlocks the session.
        """
        # VALIDATE DATA
        # username
        if not re.search(bs.config.REGEX_PATTERN_USERNAME, username):
            logging.warning("%s: The username is invalid. A valid username "
                            "needs to start with an alphabetic, "
                            "contain alphanumeric plus '_' "
                            "and have a length between 4 and 32 characters."
                            % (self.__class__.__name__, ))
            return False
        if self.is_logged_in:
            if not self.is_unlocked:
                if self.user._validate_credentials(self, username, password):
                    self.is_unlocked = True
                    logging.info("%s: Session successfully unlocked."
                                 % (self.__class__.__name__, ))
                    self._sessions_ctrl.session_activity_signal.emit()
                    return True
                else:
                    logging.warning("%s: Session unlock failed: Invalid "
                                    "credentials."
                                    % (self.__class__.__name__, ))
            else:
                logging.warning("%s: Session unlock failed: Already "
                                "unlocked."
                                % (self.__class__.__name__, ))
                return False
        else:
            logging.warning("%s: Session unlock failed: Not logged in."
                            % (self.__class__.__name__, ))
            return False


class SessionsCtrl(object):
    """ x
    :param bool gui_mode: Indicated whether or not to run the application \
    with a graphical user interface. If set to *False* it will be run from \
    the console.

    Stores and manages sessions for all is_unlocked users.
    """
    _sessions = None  # holds currently is_unlocked sessions
    # gui
    _app = None
    _guis = None  # holds currently is_unlocked guis that (actively) respectively manage a session
    _session_activity_signal = None
    _window_backup_monitor = None
    _window_filter_manager = None
    _gui_mode = None

    def __init__(self, gui_mode=False):
        super(SessionsCtrl, self).__init__()

        self._gui_mode = gui_mode
        self._session_activity_signal = bs.utils.Signal()
        self._sessions = []
        self._guis = []
        # gui stuff
        if self._gui_mode:
            self._app = bs.gui.window_main.Application("recapp")
            self.add_session_gui()
            self._window_backup_monitor = bs.gui.window_backup_monitor.WindowBackupMonitor(self)
            self._window_filter_manager = bs.gui.window_filter_manager.WindowFilterManager(self)
            self._app.exec_()

    def __repr__(self):
        return str(self._sessions)

    @property
    def app(self):
        """
        :type: :class:`~bs.gui.window_main.Application`

        The central :class:`~bs.gui.window_main.Application` hosting this \
        application gui-instance.
        """
        return self._app

    @property
    def guis(self):
        """
        :type: *list*

        A list of :class:`~bs.ctrl.session.SessionGuiCtrl` hosted by this \
        session.
        """
        return self._guis

    @property
    def session_activity_signal(self):
        """ ..

        This signal fires when a session loggs in, out, locks or unlocks.
        """
        return self._session_activity_signal

    @property
    def sessions(self):
        """
        :type: :class:`~bs.ctrl.session.SessionsCtrl`

        The :class:`~bs.ctrl.session.SessionsCtrl` this session is associated with.
        """
        return self._sessions

    @property
    def window_backup_monitor(self):
        """ ..

        :type: :class:`~bs.gui.window_backup_monitor.WindowBackupMonitor`

        The central Backup-Monitor window that displays state of and \
        management options for all dispatched and currently idle/active \
        backup-jobs.
        """
        return self._window_backup_monitor

    @property
    def window_filter_manager(self):
        """ ..

        :type: :class:`~bs.gui.window_filter_manager.WindowFilterManager`

        The central Filter-Manager window that displays all filters for the \
        current user and offers editing and management options.
        """
        return self._window_filter_manager

    def add_session(self, username, password):
        """
        :param str username: The username for the session to be created.

        :param str password: The password for the user.

        :rtype: :class:`~bs.ctrl.session.SessionCtrl`

        If attributed credentials are valid, return logged on, unlocked session
        for user.
        Returns existing session if one was previously created (used) for user.
        Fails if session for requested user is already logged in and unlocked.
        """
        logging.info("%s: Creating session for user %s..."
                     % (self.__class__.__name__,
                        username, ))
        # check if session for user already exists
        new_session = None
        for session in self._sessions:
            if session.user.username == username:
                new_session = session
                break
        # if no existing session for user was found
        if not new_session:
            # create new session
            new_session = SessionCtrl(self)
        # verify scenarios
        if new_session.is_logged_in:  # logged in but locked
            if not new_session.is_unlocked:
                if new_session not in self._sessions:
                    self._sessions.append(new_session)
                if new_session.log_in(username, password):
                    logging.info("%s: New session successfully unlocked."
                                 % (self.__class__.__name__, ))
                    return new_session
                else:
                    logging.warning("%s: No session created: Log-on failed."
                                    % (self.__class__.__name__, ))
                    return False
            else:
                logging.warning("%s: The session for this user is already "
                                "active." % (self.__class__.__name__, ))
                return -1
        else:  # not logged in, new session
            self._sessions.append(new_session)
            if new_session.log_in(username, password):
                logging.info("%s: New session successfully logged in and "
                             "unlocked." % (self.__class__.__name__, ))
                return new_session
            else:
                logging.warning("%s: No session created: Log-on failed."
                                % (self.__class__.__name__, ))
                # remove session again since invalid
                self._sessions.remove(new_session)
                return False

    def add_session_gui(self):
        """ ..

        :rtype: :class:`~bs.ctrl.session.SessionGuiCtrl`

        Adds a new UI instance to host a separate *gui-session*.
        """
        session_gui = SessionGuiCtrl(self, self._app)
        self._guis.append(session_gui)
        return session_gui

    def remove_session(self, session):
        """ ..

        :param bs.ctrl.session.SessionCtrl SessionCtrl: The \
        :class:`~bs.ctrl.session.SessionCtrl` to remove.

        :rtype: *bool*

        Removes an existing session including all of its associated objects. \
        This is usually used when a user logs out and the session is destroyed.
        """
        if session:
            self._sessions.pop(self._sessions.index(session))
            logging.info("%s: Session successfully removed: %s"
                         % (self.__class__.__name__, session, ))
        else:
            logging.warning("%s: The session does not exist: %s"
                            % (self.__class__.__name__, session, ))

    def remove_session_gui(self, session_gui):
        """ ..

        :param bs.ctrl.session.SessionGuiCtrl session_gui: The \
        :class:`~bs.ctrl.session.SessionGuiCtrl` to remove.

        :rtype: *bool*

        Removes the session_gui instance from this Sessions. This is usually \
        done after a GUI window is being closed.
        """
        self._guis.pop(self._guis.index(session_gui))
        return True

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all \
        children.
        """
        # request exit for all children
        for child in self.children():
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        return True


class SessionGuiCtrl(object):
    """ ..

    :param bs.ctrl.session.SessionsCtrl sessions: The \
    :class:`~bs.ctrl.session.SessionsCtrl` to associate with this :class:`~bs.ctrl.session.SessionGuiCtrl`.

    :param bs.gui.window_main.Application app: The central \
    :class:`~bs.gui.window_main.Application` that is running this GUI \
    instance.

    This is a container that hosts a single GUI session. A unique instance is \
    required for each GUI instance that is requested by the user.
    """
    _sessions = None
    _app = None

    _main_window = None
    _session = None

    def __init__(self, sessions, app):

        self._sessions = sessions
        self._app = app

        self._main_window = bs.gui.window_main.WindowMain(self._sessions, self, self._app)

    @property
    def main_window(self):
        """
        :type: :class:`~bs.gui.window_main.WindowMain`

        The :class:`~bs.gui.window_main.WindowMain` associated with this
        (*gui-*)*session*.
        """
        return self._main_window

    @property
    def sessions(self):
        """
        :type: :class:`~bs.ctrl.session.SessionsCtrl`

        The central :class:`~bs.ctrl.session.SessionsCtrl` managing this application instance.
        """
        return self._sessions

    @property
    def session(self):
        """
        :type: :class:`~bs.ctrl.session.SessionCtrl`
        :permissions: *read/write*

        The :class:`~bs.ctrl.session.SessionCtrl` representing the current session.
        """
        return self._session

    @session.setter
    def session(self, session):
        """ * """
        if not isinstance(session, SessionCtrl) and session:
            logging.warning("%s: The first argument needs to be of type "
                            "`SessionCtrl`."
                            % (self.__class__.__name__, ))
            return False
        self._session = session
        return session


class UserCtrl(bs.model.models.Users):
    """ ..

    :param bs.ctrl.session.SessionGuiCtrl session_gui: The \
    :class:`~bs.ctrl.session.SessionGuiCtrl` associated with the session this user is \
    associated with.

    Represents a user in the system.
    """
    _id = None
    _username = None
    _session = None

    def __init__(self, session_gui):
        super(UserCtrl, self).__init__()
        self._session = session_gui

        self._id = -1
        self._username = ""
        # create default user
        if len(self._get("*", no_auth_required=True)) == 0:
            self._add("username, password",
                      [['alpha', '4dff4ea340f0a823f15d3f4f01ab62eae0e5da579ccb851f8db9dfe84c58b2b37b89903a740e1ee172da793a6e79d560e5f7f9bd058a12a280433ed6fa46510a']],
                      no_auth_required=True)
            self._add("username, password",
                      [['bravo', '40b244112641dd78dd4f93b6c9190dd46e0099194d5a44257b7efad6ef9ff4683da1eda0244448cb343aa688f5d3efd7314dafe580ac0bcbf115aeca9e8dc114']],
                      no_auth_required=True)

    def __repr__(self):
        return "User '%s' <%s>" % (self._username, self.__class__.__name__, )

    @property
    def id(self):
        """
        :type: *int*

        The user's ID.
        """
        return self._id

    @property
    def username(self):
        """
        :type: *str*

        The user's name.
        """
        return self._username

    # OVERLOADS
    def _add_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session.is_logged_in:
            return True
        else:
            return False

    def _get_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session.is_logged_in:
            return True
        else:
            return False

    def _remove_is_permitted(self, *args, **kwargs):
        """ *
        Reimplemented from BSModel()
        """
        if self._session.is_logged_in:
            return True
        else:
            return False
    # /OVERLOADS

    def _validate_credentials(self, parent, username, password):
        """ *
        Verifies `username`, `password` for correctness and returns boolean.
        This method can only be called from `parent=isinstance(SessionCtrl)`
        """
        if isinstance(parent, SessionCtrl):
            password_hash = hashlib.sha512(password.encode())
            res = self._get("id", (("username", "=", username),
                                   ("password", "=", password_hash.hexdigest(), ), ),
                            no_auth_required=True
                            )
            if len(res) == 1:
                self._id = res[0][0]
                self._username = username
                logging.debug("%s: Credentials valid for user: '%s'."
                              % (self.__class__.__name__, self._username, ))
                return True
            elif len(res) > 1:
                logging.critical("%s: More than one user exist with the same "
                                 "username/password combination! Please "
                                 "check the integrity of the database."
                                 % (self.__class__.__name__, ))
                raise SystemExit()
                return False
            elif len(res) < 1:
                logging.debug("%s: Credentials invalid for user: '%s'"
                              % (self.__class__.__name__, self._username, ))
                return False
        else:
            logging.warning("%s: This method can only be called from certain"
                            "classes (SessionCtrl(, ...))"
                            % (self.__class__.__name__, ))
            return False
