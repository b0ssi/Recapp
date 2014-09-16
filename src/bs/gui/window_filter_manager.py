#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

The window GUI that hosts the *Filter-Manager* and all its widgets.
"""

import re
import time

import bs.ctrl.session

from PySide import QtCore, QtGui


class WindowFilterManager(QtGui.QMainWindow):
    """ ..

    :param bs.ctrl.session.SessionsCtrl sessions_ctrl: The \
    :class:`bs.ctrl.session.SessionsCtrl` of the running application instance

    This is the filter manager that lists all filters for a user and offers the
    ability to edit them.
    """
    _layout = None
    _sessions_ctrl = None

    def __init__(self, sessions_ctrl):
        super(WindowFilterManager, self).__init__()

        self._sessions_ctrl = sessions_ctrl
        self._filter_edit_views = {}

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        # connect sessions activity signal to refresh of UI
        self._sessions_ctrl.session_activity_signal.connect(self.refresh)
        # geometry
        self.setMinimumWidth(1150)
        self.setMinimumHeight(350)
        # title
        self.setWindowTitle("Filter Manager")

        centralWidget = QtGui.QWidget(self)
        self._layout = QtGui.QGridLayout(centralWidget)
        self.setCentralWidget(centralWidget)
        # filter list
        filter_list = FilterListView(self, self._sessions_ctrl)
        self._layout.addWidget(filter_list, 0, 0, 1, 1)
        # load placeholder edit widget
        self.load_filter(None)

    def load_filter(self, backup_filter):
        """ ..

        :param bs.ctrl.session.BackupFilterCtrl backup_filter:

        :rtype: `void`

        Loads the filter ``backup_filter`` into the details widget.
        """
        # remove currently loaded widget
        current_edit_widget_item = self._layout.itemAtPosition(0, 1)
        if current_edit_widget_item:
            # remove widget; this also deletes the C++ object
            widget = current_edit_widget_item.widget()
            self._layout.removeWidget(widget)
            widget.deleteLater()
        # load placeholder widget
        if not backup_filter:
            # set placeholder widget
            widget = FilterEditEmptyView(self)
            self._layout.addWidget(widget, 0, 1, 1, 1)
        else:  # load details view
            widget = FilterEditView(self, backup_filter)
            self._layout.addWidget(widget, 0, 1, 1, 1)

    def refresh(self):
        """ ..

        :rtype: `void`

        Refreshes the contents of all child widgets. They need to implement a
        ``refresh()`` method to be refreshed.
        """
        # refresh all widgets
        for widget in [self._layout.itemAt(x).widget() for x in range(self._layout.count())]:
            try:
                widget.refresh()
            except:
                pass

    def request_exit(self):
        """ ..

        :rtype: `void`

        Requests exit from all hosted widgets where required and closes itself.
        """
        self.close()
        return True


class FilterEditInterface(QtGui.QWidget):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    This is the interface for all FilterEdit*View's.
    """
    _layout = None

    def __init__(self, parent):
        """ ..
        """
        super(FilterEditInterface, self).__init__(parent)

        # layout
        self._layout = QtGui.QGridLayout(self)
        # geometry
        self.setMinimumWidth(200)


class FilterEditView(FilterEditInterface):
    """ ..

    :param QtGui.QWidget parent: \
    The :class:`QtGui.QWidget` that is to act as the widget's parent.

    :param bs.ctrl.session.BackupFilterCtrl backup_filter: The \
    :class:`bs.ctrl.session.BackupFilterCtrl` managed by this edit view.

    The edit view for a filter. This is where all details about a filter can be
    adjusted.
    """
    _backup_filter = None
    _filter_rules_container = None

    def __init__(self, parent, backup_filter):
        """ ..
        """
        super(FilterEditView, self).__init__(parent)

        self._backup_filter = backup_filter

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                        QtGui.QSizePolicy.Preferred)
        # geometry
        self.setMinimumWidth(950)
        # ======================================================================
        # Row 1/2
        # ======================================================================
        # title
        widget = QtGui.QLabel("Name", self)
        widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                             QtGui.QSizePolicy.Preferred)
        self._layout.addWidget(widget, 0, 0, 1, 1)
        line_edit = QtGui.QLineEdit(self._backup_filter.backup_filter_name, self)
        self._layout.addWidget(line_edit, 0, 1, 1, 4)
        # logical mode selector
        mode_cbox = QtGui.QComboBox(self)
        mode_cbox.setSizePolicy(size_policy)
        mode_cbox.addItems(["All filters (AND)", "Any filter (OR)", "Only one filter (XOR)"])
        self._layout.addWidget(mode_cbox, 1, 1, 1, 1)

        widget = QtGui.QLabel("must meet specified criteria.", self)
        widget.setSizePolicy(size_policy)
        self._layout.addWidget(widget, 1, 2, 1, 1)
        # spacer
        self._layout.addWidget(QtGui.QWidget(self), 1, 3, 1, 1)
        # add menu
        add_btn = QtGui.QPushButton(self)
        add_btn.setText("Add filter aspect")
        add_btn.setSizePolicy(size_policy)
        add_btn_menu = QtGui.QMenu(add_btn)
        # actions
        add_btn_menu_action_path = QtGui.QAction("Path", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_path)
        add_btn_menu_action_size = QtGui.QAction("Size", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_size)
        add_btn_menu_action_date = QtGui.QAction("Date/Time", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_date)
        add_btn_menu_action_attributes = QtGui.QAction("Attributes", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_attributes)

        add_btn.setMenu(add_btn_menu)
        self._layout.addWidget(add_btn, 1, 4, 1, 1)
        # ======================================================================
        # Row 3
        # ======================================================================
        # filter rule container, embedded in a scroll-area
        scroll_area = QtGui.QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        self._filter_rules_container = QtGui.QWidget(scroll_area)
        self._filter_rules_container._layout = QtGui.QVBoxLayout(self._filter_rules_container)
        self._filter_rules_container._layout.setContentsMargins(0, 0, 0, 0)
        self._filter_rules_container._layout.setSpacing(0)

        scroll_area.setWidget(self._filter_rules_container)
        self._layout.addWidget(scroll_area, 2, 0, 1, 5)
        # add filter rules
        for backup_filter_rule in self._backup_filter.backup_filter_rules:
            widget = None
            if isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRuleAttributesCtrl):
                widget = FilterEditRuleAttributesView(self._filter_rules_container, backup_filter_rule)
            elif isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRuleDateCtrl):
                widget = FilterEditRuleDateView(self._filter_rules_container, backup_filter_rule)
            elif isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRulePathCtrl):
                widget = FilterEditRulePathView(self._filter_rules_container, backup_filter_rule)
            elif isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRuleSizeCtrl):
                widget = FilterEditRuleSizeView(self._filter_rules_container, backup_filter_rule)
            if widget:
                self._filter_rules_container._layout.addWidget(widget)
        # buffer widget at bottom
        widget = QtGui.QWidget(self)
        self._filter_rules_container._layout.addWidget(widget)

    def refresh(self):
        """ ..

        :rtype: `void`

        Disables the view if user logged out or user session locked.
        """
        if (not self._backup_filter.session.is_logged_in or
                not self._backup_filter.session.is_unlocked):
            self.setDisabled(True)
        else:
            self.setEnabled(True)


class FilterEditEmptyView(FilterEditInterface):
    """ ..

    :param QtGui.QWidget parent: \
    The :class:`QtGui.QWidget` that is to act as the widget's parent.

    The placeholder widget for the details view of the filter manager that is \
    usually occupied by the \
    :class:`bs.gui.window_filter_manager.FilterEditView`.
    """

    def __init__(self, parent):
        """ ..
        """
        super(FilterEditEmptyView, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        # geometry
        self.setMinimumWidth(950)
        # buffer
        self._layout.addWidget(QtGui.QWidget(self), 0, 0, 1, 1)
        # info text
        widget = QtGui.QLabel("Select a filter to edit its details", self)
        widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                             QtGui.QSizePolicy.Preferred)
        self._layout.addWidget(widget, 0, 1, 1, 1)
        # buffer
        self._layout.addWidget(QtGui.QWidget(self), 0, 2, 1, 1)


class FilterEditRuleInterface(QtGui.QFrame):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI. NB: This has to be the corresponding \
    subclass to :class:`bs.ctrl.session.BackupFilterRuleCtrl`.

    This is the superclass for all filter-rule widgets.
    """
    _backup_filter_rule_ctrl = None
    _layout = None

    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleInterface, self).__init__(parent)

        self._backup_filter_rule_ctrl = backup_filter_rule_ctrl
        self._layout = QtGui.QGridLayout(self)

        # style
        self.setFrameStyle(self.Panel | self.Raised)
        # geometry
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
                           QtGui.QSizePolicy.Fixed)

        # del button
        icon = QtGui.QIcon("img/icons_forget.png")
        widget = QtGui.QPushButton(icon, None)
        widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                             QtGui.QSizePolicy.Fixed)
        self._layout.addWidget(widget)


class FilterEditRuleAttributesView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleAttributesCtrl backup_filter_ctrl: \
    The backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the attributes-rule.
    """
    _attribute_type_c_box = None
    _attribute_value = None

    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleAttributesView, self).__init__(parent,
                                                           backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                        QtGui.QSizePolicy.Preferred)
        # "File"
        widget = QtGui.QLabel("File", self)
        widget.setSizePolicy(size_policy)
        self._layout.addWidget(widget, 0, 1, 1, 1)
        # attribute type
        self._attribute_type_c_box = QtGui.QComboBox(self)
        self._attribute_type_c_box.setSizePolicy(size_policy)
        self._attribute_type_c_box.addItems(["owner",
                                             "group",
                                             "hidden flag/file . prefix",
                                             "UNIX: permissions value",
                                             "WIN: backup flag",
                                             "WIN: encrypted flag",
                                             "WIN: offline flag",
                                             "WIN: read-only flag",
                                             "WIN: system flag"])
        self._attribute_type_c_box.currentIndexChanged.connect(self._on_attribute_type_changed)
        self._layout.addWidget(self._attribute_type_c_box, 0, 2, 1, 1)
        # is/is not set
        truth_c_box = QtGui.QComboBox(self)
        truth_c_box.setSizePolicy(size_policy)
        truth_c_box.addItems(["is", "is not"])
        # spacer
        self._layout.addWidget(QtGui.QWidget(self), 0, 5, 1, 1)
        # ======================================================================
        # set-up
        # ======================================================================
        # attribute_type
        if self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_hidden:
            self._attribute_type_c_box.setCurrentIndex(2)
        elif self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_group:
            self._attribute_type_c_box.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_owner:
            self._attribute_type_c_box.setCurrentIndex(1)
            self._attribute_type_c_box.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_archive:
            self._attribute_type_c_box.setCurrentIndex(4)
        elif self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_encrypted:
            self._attribute_type_c_box.setCurrentIndex(5)
        elif self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_offline:
            self._attribute_type_c_box.setCurrentIndex(6)
        elif self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_unix_permissions:
            self._attribute_type_c_box.setCurrentIndex(3)
        elif self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_read_only:
            self._attribute_type_c_box.setCurrentIndex(7)
        elif self._backup_filter_rule_ctrl.attribute_type == bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_system:
            self._attribute_type_c_box.setCurrentIndex(8)
        # truth
        if not self._backup_filter_rule_ctrl.truth:
            truth_c_box.setCurrentIndex(1)
        self._layout.addWidget(truth_c_box, 0, 3, 1, 1)

    def _on_attribute_type_changed(self, index):
        """ ..

        Fires when the attribute type combo box changes and context \
        sensitively changes the corresponding widgets.
        """
#         # attribute value
#         if self._backup_filter_rule_ctrl.attribute in [bs.ctrl.session.BackupFilterRuleCtrl.attribute_group,
#                                                        bs.ctrl.session.BackupFilterRuleCtrl.attribute_owner]:
#             self._attribute_value.setValue(self._backup_filter_rule_ctrl.attribute_value[0])
        # read value & delete existing widget
        try:
            self._attribute_value.deleteLater()
        except:
            pass
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                        QtGui.QSizePolicy.Preferred)
        # create new widget depending on context
        if index in [0, 1]:  # owner, group
            self._attribute_value = QtGui.QLineEdit(self)
            self._layout.addWidget(self._attribute_value, 0, 4, 1, 1)

            # set value
            if (len(self._backup_filter_rule_ctrl.attribute_value) == 1 and
                    isinstance(self._backup_filter_rule_ctrl.attribute_value, str)):
                self._attribute_value.setText(self._backup_filter_rule_ctrl.attribute_value[0])
        elif index in [3]:  # unix permissions
            self._attribute_value = QtGui.QWidget(self)
            self._attribute_value.setSizePolicy(size_policy)
            self._attribute_value._layout = QtGui.QHBoxLayout(self._attribute_value)
            self._attribute_value._layout.setContentsMargins(0, 0, 0, 0)
            # read
            self._attribute_value._layout.addWidget(QtGui.QLabel("user", self._attribute_value))
            user_c_box = QtGui.QComboBox(self._attribute_value)
            user_c_box.addItems(["pass any",
                            "0: none",
                            "1: execute only",
                            "2: write only",
                            "3: write & execute",
                            "4: read only",
                            "5: read & execute",
                            "6: read & write",
                            "7: read, write & execute"])
            self._attribute_value._layout.addWidget(user_c_box)
            # write
            self._attribute_value._layout.addWidget(QtGui.QLabel("group", self._attribute_value))
            group_c_box = QtGui.QComboBox(self._attribute_value)
            group_c_box.addItems(["pass any",
                            "0: none",
                            "1: execute only",
                            "2: write only",
                            "3: write & execute",
                            "4: read only",
                            "5: read & execute",
                            "6: read & write",
                            "7: read, write & execute"])
            self._attribute_value._layout.addWidget(group_c_box)
            # execute
            self._attribute_value._layout.addWidget(QtGui.QLabel("others", self._attribute_value))
            others_c_box = QtGui.QComboBox(self._attribute_value)
            others_c_box.addItems(["pass any",
                            "0: none",
                            "1: execute only",
                            "2: write only",
                            "3: write & execute",
                            "4: read only",
                            "5: read & execute",
                            "6: read & write",
                            "7: read, write & execute"])
            self._attribute_value._layout.addWidget(others_c_box)

            self._layout.addWidget(self._attribute_value, 0, 4, 1, 1)

            if len(self._backup_filter_rule_ctrl.attribute_value) == 3:
                user_c_box.setCurrentIndex(self._backup_filter_rule_ctrl.attribute_value[0] + 1)
                group_c_box.setCurrentIndex(self._backup_filter_rule_ctrl.attribute_value[1] + 1)
                others_c_box.setCurrentIndex(self._backup_filter_rule_ctrl.attribute_value[2] + 1)
        else:  # binary flags
            self._attribute_value = QtGui.QLabel("set.", self)
            self._layout.addWidget(self._attribute_value, 0, 4, 1, 1)


class FilterEditRuleDateView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleDateCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the date-rule.
    """
    _date_edit = None
    _time_edit = None
    _time_edit_check_box = None
    _offset_check_box = None
    # the spin box widgets for the time units
    _time_offset_years = None
    _time_offset_months = None
    _time_offset_weeks = None
    _time_offset_days = None
    _time_offset_hours = None
    _time_offset_minutes = None
    _time_offset_seconds = None
    _reference_date_time_type_c_box = None
    _time_offset_direction_c_box = None

    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleDateView, self).__init__(parent,
                                                     backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                        QtGui.QSizePolicy.Preferred)
        # ======================================================================
        # Row 1
        # ======================================================================
        widget = QtGui.QWidget(self)
        widget.setMinimumHeight(50)
        self._layout.addWidget(widget, 0, 1, 1, 1)
        layout = QtGui.QHBoxLayout(widget)
        # "File"
        widget = QtGui.QLabel("File", self)
        widget.setSizePolicy(size_policy)
        layout.addWidget(widget)
        # timestamp_type (creation|modification|access)
        c_box = QtGui.QComboBox(self)
        c_box.setSizePolicy(size_policy)
        c_box.addItems(["creation", "modification", "access"])
        if self._backup_filter_rule_ctrl.timestamp_type == bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_ctime:
            c_box.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.timestamp_type == bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_mtime:
            c_box.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.timestamp_type == bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_atime:
            c_box.setCurrentIndex(2)
        layout.addWidget(c_box)
        # "time"
        widget = QtGui.QLabel("time", self)
        widget.setSizePolicy(size_policy)
        layout.addWidget(widget)
        # truth
        c_box = QtGui.QComboBox(self)
        c_box.setSizePolicy(size_policy)
        c_box.addItems(["does", "does not"])
        if not self._backup_filter_rule_ctrl.truth:
            c_box.setCurrentIndex(1)
        layout.addWidget(c_box)
        # "lie"
        widget = QtGui.QLabel("lie", self)
        widget.setSizePolicy(size_policy)
        layout.addWidget(widget)
        # position
        c_box = QtGui.QComboBox(self)
        c_box.setSizePolicy(size_policy)
        c_box.addItems(["before", "on", "after"])
        if self._backup_filter_rule_ctrl.position == bs.ctrl.session.BackupFilterRuleCtrl.position_before:
            c_box.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.position == bs.ctrl.session.BackupFilterRuleCtrl.position_on:
            c_box.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.position == bs.ctrl.session.BackupFilterRuleCtrl.position_after:
            c_box.setCurrentIndex(2)
        layout.addWidget(c_box)
        # reference_date_time_type
        self._reference_date_time_type_c_box = QtGui.QComboBox(self)
        self._reference_date_time_type_c_box.setSizePolicy(size_policy)
        self._reference_date_time_type_c_box.addItems(["current", "latest file backup", "latest folder backup", "latest volume backup", "fixed"])
        self._reference_date_time_type_c_box.currentIndexChanged.connect(self._on_date_time_reference_changed)
        layout.addWidget(self._reference_date_time_type_c_box)
        # "date"
        widget = QtGui.QLabel("date", self)
        widget.setSizePolicy(size_policy)
        layout.addWidget(widget)
        # [date-selector]
        self._date_edit = QtGui.QDateEdit(self)
        self._date_edit.setSizePolicy(size_policy)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        self._date_edit.setCalendarPopup(True)
        self._date_edit.calendarWidget().setVerticalHeaderFormat(QtGui.QCalendarWidget.ISOWeekNumbers)
        layout.addWidget(self._date_edit)
        # checkBox: "and time"
        self._time_edit_check_box = QtGui.QCheckBox("and time", self)
        self._time_edit_check_box.setSizePolicy(size_policy)
        self._time_edit_check_box.toggled.connect(self._on_time_edit_check_box_toggled)
        layout.addWidget(self._time_edit_check_box)
        # [timeSelector]
        self._time_edit = QtGui.QTimeEdit(self)
        self._time_edit.setSizePolicy(size_policy)
        self._time_edit.setDisplayFormat("hh:mm:ss")
        layout.addWidget(self._time_edit)
        # buffer
        layout.addWidget(QtGui.QWidget())
        # ======================================================================
        # Row 2
        # ======================================================================
        widget = QtGui.QWidget(self)
        widget.setMinimumHeight(50)
        self._layout.addWidget(widget, 2, 1, 1, 1)
        layout = QtGui.QHBoxLayout(widget)
        # checkbox: offset_timestamp
        self._offset_check_box = QtGui.QCheckBox("with an offset of", self)
        self._offset_check_box.toggled.connect(self._on_offset_check_box_toggled)
        layout.addWidget(self._offset_check_box)
        # combo box: positive/negative
        self._time_offset_direction_c_box = QtGui.QComboBox(self)
        self._time_offset_direction_c_box.addItems(["positive", "negative"])
        layout.addWidget(self._time_offset_direction_c_box)
        # [lineEdit]
        self._time_offset_years = QtGui.QSpinBox(self)
        self._time_offset_years.setMaximum(99)
        self._time_offset_years.setSuffix(" years")
        layout.addWidget(self._time_offset_years)
        # [lineEdit]
        self._time_offset_months = QtGui.QSpinBox(self)
        self._time_offset_months.setMaximum(11)
        self._time_offset_months.setSuffix(" months")
        layout.addWidget(self._time_offset_months)
        # [lineEdit]
        self._time_offset_weeks = QtGui.QSpinBox(self)
        self._time_offset_weeks.setMaximum(51)
        self._time_offset_weeks.setSuffix(" weeks")
        layout.addWidget(self._time_offset_weeks)
        # [lineEdit]
        self._time_offset_days = QtGui.QSpinBox(self)
        self._time_offset_days.setMaximum(365)
        self._time_offset_days.setSuffix(" days")
        layout.addWidget(self._time_offset_days)
        # [lineEdit]
        self._time_offset_hours = QtGui.QSpinBox(self)
        self._time_offset_hours.setMaximum(23)
        self._time_offset_hours.setSuffix(" hours")
        layout.addWidget(self._time_offset_hours)
        # [lineEdit]
        self._time_offset_minutes = QtGui.QSpinBox(self)
        self._time_offset_minutes.setMaximum(59)
        self._time_offset_minutes.setSuffix(" minutes")
        layout.addWidget(self._time_offset_minutes)
        # [lineEdit]
        self._time_offset_seconds = QtGui.QSpinBox(self)
        self._time_offset_seconds.setMaximum(59)
        self._time_offset_seconds.setSuffix(" seconds")
        layout.addWidget(self._time_offset_seconds)
        # ======================================================================
        # set-up
        # ======================================================================
        # reference_date_time_type
        if self._backup_filter_rule_ctrl.reference_date_time_type == bs.ctrl.session.BackupFilterRuleCtrl.reference_date_current_date:
            self._reference_date_time_type_c_box.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.reference_date_time_type == bs.ctrl.session.BackupFilterRuleCtrl.reference_date_file_backup:
            self._reference_date_time_type_c_box.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.reference_date_time_type == bs.ctrl.session.BackupFilterRuleCtrl.reference_date_folder_backup:
            self._reference_date_time_type_c_box.setCurrentIndex(2)
        elif self._backup_filter_rule_ctrl.reference_date_time_type == bs.ctrl.session.BackupFilterRuleCtrl.reference_date_volume_backup:
            self._reference_date_time_type_c_box.setCurrentIndex(3)
        elif self._backup_filter_rule_ctrl.reference_date_time_type == bs.ctrl.session.BackupFilterRuleCtrl.reference_date_fixed:
            self._reference_date_time_type_c_box.setCurrentIndex(4)
        # set timestamp
        if self._backup_filter_rule_ctrl.reference_date_time_timestamp:  # date
            struct_time = time.gmtime(self._backup_filter_rule_ctrl.reference_date_time_timestamp)
            self._date_edit.setDate(QtCore.QDate(struct_time.tm_year,
                                                 struct_time.tm_mon,
                                                 struct_time.tm_mday))
            # time
            if (struct_time.tm_hour != 0 or
                    struct_time.tm_min != 0 or
                    struct_time.tm_sec != 0):
                self._time_edit_check_box.setCheckState(QtCore.Qt.Checked)
                self._time_edit.setTime(QtCore.QTime(struct_time.tm_hour,
                                                     struct_time.tm_min,
                                                     struct_time.tm_sec))
            else:
                self._time_edit_check_box.setCheckState(QtCore.Qt.Unchecked)
        # offset: timestamp
        offset = self._backup_filter_rule_ctrl.reference_date_time_offsets
        self._offset_check_box.setCheckState(QtCore.Qt.Checked)
        if offset:
            self._time_offset_direction_c_box.setCurrentIndex(1 - offset[0])
            self._time_offset_years.setValue(offset[1])
            self._time_offset_months.setValue(offset[2])
            self._time_offset_weeks.setValue(offset[3])
            self._time_offset_days.setValue(offset[4])
            self._time_offset_hours.setValue(offset[5])
            self._time_offset_minutes.setValue(offset[6])
            self._time_offset_seconds.setValue(offset[7])
        else:
            self._offset_check_box.setCheckState(QtCore.Qt.Unchecked)

    def _on_date_time_reference_changed(self, index):
        """ ..

        Event that fires when the value of the date-time-reference (current \
        file, latest backup, etc.) selection is changed.
        """
        if index == 4:  # "fixed" is chosen, activate date/time widgets
            self._date_edit.show()
            if self._time_edit_check_box.isChecked():
                self._time_edit.show()
        else:  # anything else is chosen. Deactivate date/time widgets
            self._date_edit.hide()
            self._time_edit.hide()

    def _on_time_edit_check_box_toggled(self, checked):
        """ ..

        Event that fires when the "and time" checkbox is clicked. \
        Shows/hides time chooser widget.
        """
        if self._reference_date_time_type_c_box.currentIndex() == 4:
            if checked:
                self._time_edit.show()
            else:
                self._time_edit.hide()

    def _on_offset_check_box_toggled(self, checked):
        """ ..

        Event that fires when the "with an offset of" checkbox is clicked. \
        Shows/hides widgets used to specify the time-offset.
        """
        if checked:
            self._time_offset_direction_c_box.show()
            self._time_offset_years.show()
            self._time_offset_months.show()
            self._time_offset_weeks.show()
            self._time_offset_days.show()
            self._time_offset_hours.show()
            self._time_offset_minutes.show()
            self._time_offset_seconds.show()
        else:
            self._time_offset_direction_c_box.hide()
            self._time_offset_years.hide()
            self._time_offset_months.hide()
            self._time_offset_weeks.hide()
            self._time_offset_days.hide()
            self._time_offset_hours.hide()
            self._time_offset_minutes.hide()
            self._time_offset_seconds.hide()


class FilterEditRulePathView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRulePathCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the path-rule.
    """
    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRulePathView, self).__init__(parent,
                                                     backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        self._layout.addWidget(QtGui.QLabel("Path", self), 0, 1, 1, 1)
        # does/does not
        widget = QtGui.QComboBox(self)
        widget.addItems(["does", "does not"])
        if not self._backup_filter_rule_ctrl.truth:
            widget.setCurrentIndex(1)
        self._layout.addWidget(widget, 0, 2, 1, 1)
        # mode
        c_box = QtGui.QComboBox(self)
        c_box.addItems(["start with", "contain", "end with", "match pattern", "match regex"])
        if self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_starts_with:
            c_box.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_contains:
            c_box.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_ends_with:
            c_box.setCurrentIndex(2)
        elif self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_matches:
            c_box.setCurrentIndex(3)
        elif self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_match_pattern:
            c_box.setCurrentIndex(4)
        self._layout.addWidget(c_box, 0, 3, 1, 1)
        # pattern
        self._layout.addWidget(QtGui.QLineEdit(self._backup_filter_rule_ctrl.path_pattern, self),
                               0, 4, 1, 1)
        # match case
        check_box = QtGui.QCheckBox("matching case", self)
        if self._backup_filter_rule_ctrl.match_case:
            check_box.setCheckState(QtCore.Qt.Checked)
        self._layout.addWidget(check_box, 0, 5, 1, 1)


class FilterEditRuleSizeView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleSizeCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the size-rule.
    """
    _size_widget = None
    _size_policy = None

    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleSizeView, self).__init__(parent,
                                                     backup_filter_rule_ctrl)

        self._size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                              QtGui.QSizePolicy.Preferred)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        # "File size"
        widget = QtGui.QLabel("File size")
        widget.setSizePolicy(self._size_policy)
        self._layout.addWidget(widget, 0, 1, 1, 1)
        # is/is not
        widget = QtGui.QComboBox(self)
        widget.setSizePolicy(self._size_policy)
        widget.addItems(["is", "is not"])
        if not self._backup_filter_rule_ctrl.truth:
            widget.setCurrentIndex(1)
        self._layout.addWidget(widget, 0, 2, 1, 1)
        # less, less/equal, equal, equal/larger, larger
        widget = QtGui.QComboBox(self)
        widget.setSizePolicy(self._size_policy)
        widget.addItems(["less than", "less or equal to", "equal to", "equal or larger than", "larger than"])
        if self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller:
            widget.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller_equal:
            widget.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_equal:
            widget.setCurrentIndex(2)
        elif self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_larger_equal:
            widget.setCurrentIndex(3)
        elif self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_larger:
            widget.setCurrentIndex(4)
        self._layout.addWidget(widget, 0, 3, 1, 1)
        # quantity
        unit_index = 0
        size = float(self._backup_filter_rule_ctrl.size)
        while True:
            if size > 1023:
                size = size / 1024
                unit_index += 1
            else:
                break
        self._size_widget = QtGui.QSpinBox(self)
        self._layout.addWidget(self._size_widget, 0, 4, 1, 1)
        # unit
        widget = QtGui.QComboBox(self)
        widget.setSizePolicy(self._size_policy)
        widget.addItems(["byte(s)", "KiB", "MiB", "GiB", "TiB", "PiB"])
        widget.currentIndexChanged.connect(self._on_unit_changed)
        widget.setCurrentIndex(unit_index)
        self._layout.addWidget(widget, 0, 5, 1, 1)
        # spacer
        self._layout.addWidget(QtGui.QWidget(self), 0, 6, 1, 1)

    def _on_unit_changed(self, index):
        """ ..

        Event that gets called when index of unit-selector is changed. \
        Switches between an integer or float combo box, depending on selected \
        unit.
        """
        size = float(self._backup_filter_rule_ctrl.size)
        while True:
            if size > 1023:
                size = size / 1024
            else:
                break
        if index == 0:  # "byte(s)" is chosen
            self._size_widget.deleteLater()
            self._size_widget = QtGui.QSpinBox(self)
            self._size_widget.setSizePolicy(self._size_policy)
            self._size_widget.setMaximum(1023)
            self._size_widget.setValue(size)
            self._layout.addWidget(self._size_widget, 0, 4, 1, 1)
        else:  # any larger unit is chosen
            self._size_widget.deleteLater()
            self._size_widget = QtGui.QDoubleSpinBox(self)
            self._size_widget.setSizePolicy(self._size_policy)
            self._size_widget.setMaximum(1024.0)
            self._size_widget.setDecimals(2)
            self._size_widget.setValue(size)
            self._layout.addWidget(self._size_widget, 0, 4, 1, 1)


class FilterListView(QtGui.QListWidget):
    """ ..

    :param bs.gui.window_filter_manager.WindowFilterManager window_filter_manager: \
    The :class:`bs.gui.window_filter_manager.WindowFilterManager` this list \
    view is nested in.

    :param bs.ctrl.session.SessionsCtrl sessions_ctrl: The \
    :class:`bs.ctrl.session.SessionsCtrl` that hosts the runtime.

    This is the list view that lists all available filters in the filter
    manager.
    """
    _window_filter_manager = None
    _sessions_ctrl = None

    def __init__(self, window_filter_manager, sessions_ctrl):
        """ ..
        """
        super(FilterListView, self).__init__()

        self._window_filter_manager = window_filter_manager
        self._sessions_ctrl = sessions_ctrl

        self._init_ui()

    @property
    def items(self):
        """ ..

        :rtype: `list`

        A list of all \
        :class:`bs.gui.window_filter_manager.FilterListItemView` in the list.
        """
        return [self.item(x) for x in range(self.count())]

    def _init_ui(self):
        """ ..
        """
        self.itemSelectionChanged.connect(self.load_current_item)
        # (re)populate list
        self.refresh()

    def refresh(self):
        """ ..

        :rtype: `void`

        Refreshes the list of filters depending on what user is currently
        logged in, if any. Empties the list if no user is logged in.
        """
        # iterate through filters of current sessions and add items where
        # necessary
        for session in self._sessions_ctrl.sessions:
            for backup_filter in session.backup_filters.backup_filters:
                # add, if not in list yet
                if backup_filter not in [x.backup_filter for x in self.items]:
                    item = FilterListItemView(backup_filter)
                    self.addItem(item)
        # iterate through items and lock/unlock if necessary
        for item in self.items:
            if not item.backup_filter.session.is_logged_in or not item.backup_filter.session.is_unlocked:
                item.set_disabled()
            else:
                item.set_enabled()

    def load_current_item(self):
        """ ..

        Loads the currently selected item.
        """
        item = None
        if len(self.selectedItems()) > 0:
            item = self.selectedItems()[0]
        if item and item.is_enabled:
            self._window_filter_manager.load_filter(item._backup_filter)


class FilterListItemView(QtGui.QListWidgetItem):
    """ ..

    :param bs.ctrl.session.BackupFilterCtrl backup_filter: The \
    :class:`bs.ctrl.session.BackupFilterCtrl` associated with this item.

    A single item in :class:`bs.gui.window_filter_manager.FilterListView`.
    """
    _backup_filter = None
    _enabled = None

    def __init__(self, backup_filter):
        super(FilterListItemView, self).__init__()

        self._backup_filter = backup_filter
        self._enabled = True

        self._init_ui()

    @property
    def backup_filter(self):
        """ ..

        :rtype: :class:`bs.ctrl.session.BackupFilterCtrl`

        The :class:`bs.ctrl.session.BackupFilterCtrl` associated with this item.
        """
        return self._backup_filter

    @property
    def is_disabled(self):
        """ ..

        :rtype: `boolean`
        """
        return not self._enabled

    @property
    def is_enabled(self):
        """ ..

        :rtype: `boolean`
        """
        return self._enabled

    def _init_ui(self):
        """ ..
        """
        self.setText(self._backup_filter.backup_filter_name)

    def set_enabled(self):
        """ ..

        :rtype: `void`

        Enables the item.
        """
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self._enabled = True

    def set_disabled(self):
        """ ..

        :rtype: `void`

        Disables the item.
        """
        self.setFlags(QtCore.Qt.NoItemFlags)
        self._enabled = False
