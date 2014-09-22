#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

The window GUI that hosts the *Filter-Manager* and all its widgets.
"""

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
        self.setMinimumWidth(1200)
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


class FilterEditView(FilterEditInterface):
    """ ..

    :param QtGui.QWidget parent: The :class:`QtGui.QWidget` that is to act as \
    the widget's parent.

    :param bs.ctrl.session.BackupFilterCtrl backup_filter: The \
    :class:`bs.ctrl.session.BackupFilterCtrl` managed by this edit view.

    The edit view for a filter. This is where all details about a filter can be
    adjusted.
    """
    _backup_filter = None
    _filter_rules_container = None
    _filter_rules_mode_widget = None
    _save_widget = None
    _discard_widget = None

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
        self.setMinimumWidth(1000)
        # ======================================================================
        # Row 0/1
        # ======================================================================
        # title
        widget = QtGui.QLabel("Name", self)
        widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                             QtGui.QSizePolicy.Preferred)
        self._layout.addWidget(widget, 0, 0, 1, 1)
        line_edit = QtGui.QLineEdit(self._backup_filter.backup_filter_name, self)
        self._layout.addWidget(line_edit, 0, 1, 1, 4)
        # logical mode selector
        self._filter_rules_mode_widget = QtGui.QComboBox(self)
        self._filter_rules_mode_widget.setSizePolicy(size_policy)
        self._filter_rules_mode_widget.addItems(["All filters (AND)", "Any filter (OR)", "Only one filter (XOR)"])
        self._layout.addWidget(self._filter_rules_mode_widget, 1, 1, 1, 1)

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
        # Row 2
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
                widget.update_signal.connect(self._update_event)
                self._filter_rules_container._layout.addWidget(widget)
        # buffer widget at bottom
        widget = QtGui.QWidget(self)
        self._filter_rules_container._layout.addWidget(widget)
        # ======================================================================
        # Row 3
        # ======================================================================
        self._save_widget = QtGui.QPushButton("Save", self)
        self._layout.addWidget(self._save_widget, 3, 3, 1, 1)
        self._save_widget.clicked.connect(self.save)

        self._discard_widget = QtGui.QPushButton("Reset", self)
        self._layout.addWidget(self._discard_widget, 3, 4, 1, 1)
        self._discard_widget.clicked.connect(self.refresh)
        # ======================================================================
        # set-up
        # ======================================================================
        # logical mode selector
        index = self._backup_filter.backup_filter_rules_mode
        if index == bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_and:
            self._filter_rules_mode_widget.setCurrentIndex(0)
        elif index == bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_or:
            self._filter_rules_mode_widget.setCurrentIndex(1)
        elif index == bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_xor:
            self._filter_rules_mode_widget.setCurrentIndex(2)
        # save/discard buttons
        self._save_widget.setDisabled(True)
        self._discard_widget.setDisabled(True)

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

    def save(self):
        """ ..

        :rtype: `void`

        Saves the backup-filter.
        """
        # commit data from GUI to CTRL
        for i in range(self._filter_rules_container._layout.count()-1):
            widget = self._filter_rules_container._layout.itemAt(i).widget()
            widget.push_data()
        # save data on CTRL

    def _update_event(self, widget, modified):
        """ ..

        Is called when a registered rule-widget is updated.
        """
        if modified:
            self._save_widget.setEnabled(True)
            self._discard_widget.setEnabled(True)
        else:
            self._save_widget.setDisabled(True)
            self._discard_widget.setDisabled(True)


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
        self.setMinimumWidth(1000)
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

        self._row_layouts = {}  # holds the horizontal row layouts
        self._registered_widgets = {}  # holds all widgets to be watched for modification
        self._update_signal = bs.utils.Signal()
        self._update_signal.connect(self._update_event)

        self._backup_filter_rule_ctrl = backup_filter_rule_ctrl
        # layout
        self._layout = QtGui.QGridLayout(self)
        # style
        self.setFrameStyle(self.Panel | self.Raised)
        # del button
        icon = QtGui.QIcon("img/icons_forget.png")
        widget = QtGui.QPushButton(icon, None)
        widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                             QtGui.QSizePolicy.Fixed)
        self._layout.addWidget(widget, 0, 0, 1, 1)
        # geometry
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
                           QtGui.QSizePolicy.Fixed)

    @property
    def is_modified(self):
        """ ..

        :rtype: `boolean`

        Returns whether or not this rule is dirty.
        """
        modified = False
        for key in self._registered_widgets.keys():
            if (self._registered_widgets[key] and
                    key.isVisible()):
                modified = True
                break
        return modified

    @property
    def update_signal(self):
        """ ..

        :type: :class:`bs.ctrl.utils.Signal`

        This signal emits when registered sub-widget is updated/changed, by \
        the user or programmatically.
        """
        return self._update_signal

    def _pull_file_folder(self, direction="pull"):
        """ ..
        """
        options = [bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file_folder,
                   bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file,
                   bs.ctrl.session.BackupFilterRuleCtrl.file_folder_folder
                   ]
        if direction == "push":
            self._backup_filter_rule_ctrl.file_folder = options[self._file_folder_widget.currentIndex()]
        elif direction == "pull":
            self._file_folder_widget.setCurrentIndex(options.index(self._backup_filter_rule_ctrl.file_folder))

    def _pull_include_subfolders(self, direction="pull"):
        """ ..
        """
        options = {QtCore.Qt.Checked: True,
                   QtCore.Qt.Unchecked: False}
        if direction == "push":
            self._backup_filter_rule_ctrl.include_subfolders = options[self._incl_subfolders_widget.checkState()]
        elif direction == "pull":
            if self._backup_filter_rule_ctrl.include_subfolders:
                self._incl_subfolders_widget.setCheckState(QtCore.Qt.Checked)
            else:
                self._incl_subfolders_widget.setCheckState(QtCore.Qt.Unchecked)

    def _pull_truth(self, direction="pull"):
        """ ..
        """
        options = [True, False]
        if direction == "push":
            self._backup_filter_rule_ctrl.truth = options[self._truth_widget.currentIndex()]
        elif direction == "pull":
            self._truth_widget.setCurrentIndex(options.index(self._backup_filter_rule_ctrl.truth))

    def _push_file_folder(self):
        """ ..
        """
        self._pull_file_folder("push")

    def _push_include_subfolders(self):
        """ ..
        """
        self._pull_include_subfolders("push")

    def _push_truth(self):
        """ ..
        """
        self._pull_truth("push")

    def get_row_layout(self, row):
        """ ..

        :param int row: The row which layout is to be returned.

        :rtype: :class:`QtGui.QHBoxLayout`

        Returns the :class:`QtGui.QHBoxLayout` of the row ``row``.
        """
        if row not in self._row_layouts.keys():
            # row 0
            widget = QtGui.QWidget(self)
            widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                 QtGui.QSizePolicy.Preferred)
            widget.setMinimumHeight(32)
            self._row_layouts[row] = QtGui.QHBoxLayout(widget)
            self._row_layouts[row].setContentsMargins(0, 0, 0, 0)
            # SetFixedSize
            self._row_layouts[row].setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
            self._layout.addWidget(widget, row, 1, 1, 1)
            # spacer
            self._layout.addWidget(QtGui.QWidget(self), row, 2, 1, 1)
        return self._row_layouts[row]

    def _file_folder_update_event(self, index):
        """ ..

        Event that triggers when file/folder selector is changed.
        Enables/disables the "incl. subfolders" check box. Updates modified
        state.
        """
        # update modified state
        options = [bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file_folder,
                   bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file,
                   bs.ctrl.session.BackupFilterRuleCtrl.file_folder_folder
                   ]
        if self._backup_filter_rule_ctrl.file_folder == options[self._file_folder_widget.currentIndex()]:
            self._registered_widgets[self._file_folder_widget] = False
        else:
            self._registered_widgets[self._file_folder_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._file_folder_widget])
        # update ui
        if index == 1:
            self._incl_subfolders_widget.hide()
        else:
            self._incl_subfolders_widget.show()

    def _include_subfolders_update_event(self, state):
        """ ..

        Event that triggers when the include-subfolders selector is changed. \
        Updates modified state.
        """
        options = {QtCore.Qt.Unchecked: False,
                   QtCore.Qt.Checked: True
                   }
        if self._backup_filter_rule_ctrl.include_subfolders == options[state]:
            self._registered_widgets[self._incl_subfolders_widget] = False
        else:
            self._registered_widgets[self._incl_subfolders_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._incl_subfolders_widget])

    def _truth_update_event(self, index):
        """ ..

        Event that triggers when truth selector is changed. Updates modified
        state.
        """
        # update modified state
        options = [True, False]
        if self._backup_filter_rule_ctrl.truth == options[self._truth_widget.currentIndex()]:
            self._registered_widgets[self._truth_widget] = False
        else:
            self._registered_widgets[self._truth_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._truth_widget])

    def _update_event(self, widget, modified):
        """ ..

        Fires when a registered widget is updated.
        """
        # update modified state
        if self.is_modified:
            self.setStyleSheet(".%s {background: orange}" % self.__class__.__name__)
        else:
            self.setStyleSheet("")


class FilterEditRuleAttributesView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleAttributesCtrl backup_filter_ctrl: \
    The backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the attributes-rule.
    """
    _attribute_type_widget = None
    _file_folder_widget = None
    _incl_subfolders_widget = None
    _truth_widget = None

    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleAttributesView, self).__init__(parent,
                                                           backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        # ======================================================================
        # Row 0
        # ======================================================================
        # File/Folder/Either
        self._file_folder_widget = QtGui.QComboBox(self)
        self._file_folder_widget.addItems(["File/Folder", "File", "Folder"])
        self.get_row_layout(0).addWidget(self._file_folder_widget)
        # attribute type
        self._attribute_type_widget = QtGui.QComboBox(self)
        self._attribute_type_widget.addItems(["owner",
                                              "group",
                                              "hidden flag/file . prefix",
                                              "UNIX: permissions value",
                                              "WIN: archive",
                                              "WIN: encrypted flag",
                                              "WIN: offline flag",
                                              "WIN: read-only flag",
                                              "WIN: system flag"])
        self.get_row_layout(0).addWidget(self._attribute_type_widget)
        # is/is not set
        self._truth_widget = QtGui.QComboBox(self)
        self._truth_widget.addItems(["is", "is not"])
        self.get_row_layout(0).addWidget(self._truth_widget)
        # user/group value
        self._attribute_value_widget = QtGui.QLineEdit(self)
        self._attribute_value_widget.setMinimumWidth(500)
        self.get_row_layout(0).addWidget(self._attribute_value_widget)
        # "set"
        self._set_widget = QtGui.QLabel("set.", self)
        self.get_row_layout(0).addWidget(self._set_widget)
        # ======================================================================
        # Row 1
        # ======================================================================
        # user
        self._permissions_user_label_widget = QtGui.QLabel("user", self)
        self.get_row_layout(1).addWidget(self._permissions_user_label_widget)
        self._permissions_user_widget = QtGui.QComboBox(self)
        self._permissions_user_widget.addItems(["pass any",
                                                "0: none",
                                                "1: execute only",
                                                "2: write only",
                                                "3: write & execute",
                                                "4: read only",
                                                "5: read & execute",
                                                "6: read & write",
                                                "7: read, write & execute"])
        self.get_row_layout(1).addWidget(self._permissions_user_widget)
        # group
        self._permissions_group_label_widget = QtGui.QLabel("group", self)
        self.get_row_layout(1).addWidget(self._permissions_group_label_widget)
        self._permissions_group_widget = QtGui.QComboBox(self)
        self._permissions_group_widget.addItems(["pass any",
                                                 "0: none",
                                                 "1: execute only",
                                                 "2: write only",
                                                 "3: write & execute",
                                                 "4: read only",
                                                 "5: read & execute",
                                                 "6: read & write",
                                                 "7: read, write & execute"])
        self.get_row_layout(1).addWidget(self._permissions_group_widget)
        # others
        self._permissions_others_label_widget = QtGui.QLabel("others", self)
        self.get_row_layout(1).addWidget(self._permissions_others_label_widget)
        self._permissions_others_widget = QtGui.QComboBox(self)
        self._permissions_others_widget.addItems(["pass any",
                                                  "0: none",
                                                  "1: execute only",
                                                  "2: write only",
                                                  "3: write & execute",
                                                  "4: read only",
                                                  "5: read & execute",
                                                  "6: read & write",
                                                  "7: read, write & execute"])
        self.get_row_layout(1).addWidget(self._permissions_others_widget)
        # sub-folders
        self._incl_subfolders_widget = QtGui.QCheckBox("including subfolders",
                                                       self)
        self.get_row_layout(1).addWidget(self._incl_subfolders_widget)
        # ======================================================================
        # register
        #
        # To register and watch a widget for modification to update the rule
        # view, register widget here and connect to an update method that in
        # return updates the registered state.
        # ======================================================================
        self._registered_widgets[self._file_folder_widget] = False
        self._file_folder_widget.currentIndexChanged.connect(self._file_folder_update_event)

        self._registered_widgets[self._attribute_type_widget] = False
        self._attribute_type_widget.currentIndexChanged.connect(self._attribute_type_update_event)

        self._registered_widgets[self._truth_widget] = False
        self._truth_widget.currentIndexChanged.connect(self._truth_update_event)

        self._registered_widgets[self._permissions_user_widget] = False
        self._permissions_user_widget.currentIndexChanged.connect(self._permissions_user_update_event)

        self._registered_widgets[self._permissions_group_widget] = False
        self._permissions_group_widget.currentIndexChanged.connect(self._permissions_group_update_event)

        self._registered_widgets[self._permissions_others_widget] = False
        self._permissions_others_widget.currentIndexChanged.connect(self._permissions_others_update_event)

        self._registered_widgets[self._attribute_value_widget] = False
        self._attribute_value_widget.textChanged.connect(self._attribute_value_widget_update_event)

        self._registered_widgets[self._incl_subfolders_widget] = False
        self._incl_subfolders_widget.stateChanged.connect(self._include_subfolders_update_event)
        # ======================================================================
        # set-up
        # ======================================================================
        self._pull_file_folder()
        self._pull_attribute_type()
        self._pull_truth()
        self._pull_attribute_value()
        self._pull_include_subfolders()

    def _pull_attribute_type(self, direction="pull"):
        """ ..
        """
        options = [bs.ctrl.session.BackupFilterRuleCtrl.attribute_owner,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_group,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_hidden,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_unix_permissions,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_archive,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_encrypted,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_offline,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_read_only,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_system]
        if direction == "push":
            self._backup_filter_rule_ctrl.attribute_type = options[self._attribute_type_widget.currentIndex()]
        elif direction == "pull":
            index = options.index(self._backup_filter_rule_ctrl.attribute_type)
            if index == 0:
                self._attribute_type_widget.setCurrentIndex(1)
            self._attribute_type_widget.setCurrentIndex(index)

    def _pull_attribute_value(self, direction="pull"):
        """ ..
        """
        options = [True, False]
        if direction == "push":
            if self._attribute_value_widget.isVisible():
                self._backup_filter_rule_ctrl.attribute_value = [self._attribute_value_widget.text(), None, None]
            elif self._permissions_user_widget.isVisible():
                self._backup_filter_rule_ctrl.attribute_value = [self._permissions_user_widget.currentIndex(),
                                                                 self._permissions_group_widget.currentIndex(),
                                                                 self._permissions_others_widget.currentIndex()
                                                                 ]
        elif direction == "pull":
            if isinstance(self._backup_filter_rule_ctrl.attribute_value[0], str):
                self._attribute_value_widget.setText(self._backup_filter_rule_ctrl.attribute_value[0])
            elif isinstance(self._backup_filter_rule_ctrl.attribute_value[0], int):
                if isinstance(self._backup_filter_rule_ctrl.attribute_value[0], int):
                    self._permissions_user_widget.setCurrentIndex(self._backup_filter_rule_ctrl.attribute_value[0])
                    self._permissions_group_widget.setCurrentIndex(self._backup_filter_rule_ctrl.attribute_value[1])
                    self._permissions_others_widget.setCurrentIndex(self._backup_filter_rule_ctrl.attribute_value[2])

    def _push_attribute_type(self):
        """ ..
        """
        self._pull_attribute_type("push")

    def _push_attribute_value(self):
        """ ..
        """
        self._pull_attribute_value("push")

    def push_data(self):
        """ ..

        :rtype: `dictionary`

        Collects and serializes the rule(-widget)'s data and returns it in a \
        dictionary. This can be used to save it back to the database.
        """
        self._push_file_folder()
        self._push_attribute_type()
        self._push_truth()
        self._push_attribute_value()
        self._push_include_subfolders()
        # reset modification counters
        for item in self._registered_widgets.keys():
            self._registered_widgets[item] = False
        # send update signal
        self.update_signal.emit(self, False)

    def _attribute_type_update_event(self, index):
        """ ..

        Event that triggers when attribute type selector is changed. Updates \
        modified state as well as this rule-view, depending on the chosen index.
        """
        # update modified state
        options = [bs.ctrl.session.BackupFilterRuleCtrl.attribute_owner,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_group,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_hidden,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_unix_permissions,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_archive,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_encrypted,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_offline,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_read_only,
                   bs.ctrl.session.BackupFilterRuleCtrl.attribute_win_system
                   ]
        if self._backup_filter_rule_ctrl.attribute_type == options[self._attribute_type_widget.currentIndex()]:
            self._registered_widgets[self._attribute_type_widget] = False
        else:
            self._registered_widgets[self._attribute_type_widget] = True

        # update ui
        # show/hide widgets depending on context
        if index in [0, 1]:  # owner, group
            self._attribute_value_widget.show()
        else:
            self._attribute_value_widget.hide()

        # unix permissions
        if index in [3]:
            self._permissions_user_widget.show()
            self._permissions_user_label_widget.show()
            self._permissions_group_widget.show()
            self._permissions_group_label_widget.show()
            self._permissions_others_widget.show()
            self._permissions_others_label_widget.show()
        else:
            self._permissions_user_widget.hide()
            self._permissions_user_label_widget.hide()
            self._permissions_group_widget.hide()
            self._permissions_group_label_widget.hide()
            self._permissions_others_widget.hide()
            self._permissions_others_label_widget.hide()

        # binary flags
        if index in [2] or index >= 4:
            self._set_widget.show()
        else:
            self._set_widget.hide()

        self.update_signal.emit(self,
                                self._registered_widgets[self._attribute_type_widget])

    def _attribute_value_widget_update_event(self, text):
        """ ..

        Event that triggers when attribute value selector (owner/group) is \
        changed. Updates modified state as well as this rule-view, depending \
        on the chosen index.
        """
        # update modified state
        if self._backup_filter_rule_ctrl.attribute_value[0] == text:
            self._registered_widgets[self._attribute_value_widget] = False
        else:
            self._registered_widgets[self._attribute_value_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._attribute_value_widget])

    def _permissions_group_update_event(self, index):
        """ ..

        Event that triggers when attribute value selector (unix group \
        permissions) is changed. Updates modified state as well as this \
        rule-view, depending on the chosen index.
        """
        # update modified state
        if self._backup_filter_rule_ctrl.attribute_value[1] == self._permissions_group_widget.currentIndex():
            self._registered_widgets[self._permissions_group_widget] = False
        else:
            self._registered_widgets[self._permissions_group_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._permissions_group_widget])

    def _permissions_others_update_event(self, index):
        """ ..

        Event that triggers when attribute value selector (unix others \
        permissions) is changed. Updates modified state as well as this \
        rule-view, depending on the chosen index.
        """
        # update modified state
        if self._backup_filter_rule_ctrl.attribute_value[2] == self._permissions_others_widget.currentIndex():
            self._registered_widgets[self._permissions_others_widget] = False
        else:
            self._registered_widgets[self._permissions_others_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._permissions_others_widget])

    def _permissions_user_update_event(self, index):
        """ ..

        Event that triggers when attribute value selector (unix user \
        permissions) is changed. Updates modified state as well as this \
        rule-view, depending on the chosen index.
        """
        # update modified state
        if self._backup_filter_rule_ctrl.attribute_value[0] == self._permissions_user_widget.currentIndex():
            self._registered_widgets[self._permissions_user_widget] = False
        else:
            self._registered_widgets[self._permissions_user_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._permissions_user_widget])


class FilterEditRuleDateView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleDateCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the date-rule.
    """
    _date_widget = None
    _time_widget = None
    _time_check_box_widget = None
    _offset_check_box = None
    _file_folder_widget = None
    _incl_subfolders_widget = None
    # the spin box widgets for the time units
    _time_offset_years = None
    _time_offset_months = None
    _time_offset_weeks = None
    _time_offset_days = None
    _time_offset_hours = None
    _time_offset_minutes = None
    _time_offset_seconds = None
    _time_offset_direction_c_box = None
    _timestamp_type_widget = None
    _position_widget = None

    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleDateView, self).__init__(parent,
                                                     backup_filter_rule_ctrl)

        self._date_display_pattern = "yyyy-MM-dd"
        self._time_display_pattern = "hh:mm:ss"

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        # ======================================================================
        # Row 0
        # ======================================================================
        # File/Folder/Either
        self._file_folder_widget = QtGui.QComboBox(self)
        self._file_folder_widget.addItems(["File/Folder", "File", "Folder"])
        self.get_row_layout(0).addWidget(self._file_folder_widget)
        # timestamp_type (creation|modification|access)
        self._timestamp_type_widget = QtGui.QComboBox(self)
        self._timestamp_type_widget.addItems(["creation", "modification", "access"])
        self.get_row_layout(0).addWidget(self._timestamp_type_widget)
        # "time"
        widget = QtGui.QLabel("time", self)
        self.get_row_layout(0).addWidget(widget)
        # truth
        self._truth_widget = QtGui.QComboBox(self)
        self._truth_widget.addItems(["does", "does not"])
        self.get_row_layout(0).addWidget(self._truth_widget)
        # "lie"
        widget = QtGui.QLabel("lie", self)
        self.get_row_layout(0).addWidget(widget)
        # position
        self._position_widget = QtGui.QComboBox(self)
        self._position_widget.addItems(["before", "on", "after"])
        self.get_row_layout(0).addWidget(self._position_widget)
        # reference_date_time_type
        self._reference_date_time_type_widget = QtGui.QComboBox(self)
        self._reference_date_time_type_widget.addItems(["current", "latest file backup", "latest folder backup", "latest volume backup", "fixed"])
        self.get_row_layout(0).addWidget(self._reference_date_time_type_widget)
        # "date"
        widget = QtGui.QLabel("date", self)
        self.get_row_layout(0).addWidget(widget)
        # [date-selector]
        self._date_widget = QtGui.QDateEdit(self)
        self._date_widget.setDisplayFormat(self._date_display_pattern)
        self._date_widget.setCalendarPopup(True)
        self._date_widget.calendarWidget().setVerticalHeaderFormat(QtGui.QCalendarWidget.ISOWeekNumbers)
        self.get_row_layout(0).addWidget(self._date_widget)
        # checkBox: "and time"
        self._time_check_box_widget = QtGui.QCheckBox("and time", self)
        self.get_row_layout(0).addWidget(self._time_check_box_widget)
        # [timeSelector]
        self._time_widget = QtGui.QTimeEdit(self)
        self._time_widget.setDisplayFormat(self._time_display_pattern)
        self.get_row_layout(0).addWidget(self._time_widget)
        # ======================================================================
        # Row 1
        # ======================================================================
        # checkbox: offset_timestamp
        self._offset_check_box = QtGui.QCheckBox("with an offset of", self)
        self.get_row_layout(1).addWidget(self._offset_check_box)
        # combo box: positive/negative
        self._time_offset_direction_c_box = QtGui.QComboBox(self)
        self._time_offset_direction_c_box.addItems(["positive", "negative"])
        self.get_row_layout(1).addWidget(self._time_offset_direction_c_box)
        # years
        self._time_offset_years = QtGui.QSpinBox(self)
        self._time_offset_years.setMaximum(99)
        self._time_offset_years.setSuffix(" years")
        self.get_row_layout(1).addWidget(self._time_offset_years)
        # months
        self._time_offset_months = QtGui.QSpinBox(self)
        self._time_offset_months.setMaximum(11)
        self._time_offset_months.setSuffix(" months")
        self.get_row_layout(1).addWidget(self._time_offset_months)
        # weeks
        self._time_offset_weeks = QtGui.QSpinBox(self)
        self._time_offset_weeks.setMaximum(51)
        self._time_offset_weeks.setSuffix(" weeks")
        self.get_row_layout(1).addWidget(self._time_offset_weeks)
        # days
        self._time_offset_days = QtGui.QSpinBox(self)
        self._time_offset_days.setMaximum(365)
        self._time_offset_days.setSuffix(" days")
        self.get_row_layout(1).addWidget(self._time_offset_days)
        # hours
        self._time_offset_hours = QtGui.QSpinBox(self)
        self._time_offset_hours.setMaximum(23)
        self._time_offset_hours.setSuffix(" hours")
        self.get_row_layout(1).addWidget(self._time_offset_hours)
        # minutes
        self._time_offset_minutes = QtGui.QSpinBox(self)
        self._time_offset_minutes.setMaximum(59)
        self._time_offset_minutes.setSuffix(" minutes")
        self.get_row_layout(1).addWidget(self._time_offset_minutes)
        # seconds
        self._time_offset_seconds = QtGui.QSpinBox(self)
        self._time_offset_seconds.setMaximum(59)
        self._time_offset_seconds.setSuffix(" seconds")
        self.get_row_layout(1).addWidget(self._time_offset_seconds)
        # ======================================================================
        # Row 2
        # ======================================================================
        # sub-folders
        self._incl_subfolders_widget = QtGui.QCheckBox("including subfolders",
                                                       self)
        self.get_row_layout(2).addWidget(self._incl_subfolders_widget)
        # ======================================================================
        # register
        #
        # To register and watch a widget for modification to update the rule
        # view, register widget here and connect to an update method that in
        # return updates the registered state.
        # ======================================================================
        self._registered_widgets[self._file_folder_widget] = False
        self._file_folder_widget.currentIndexChanged.connect(self._file_folder_update_event)

        self._registered_widgets[self._timestamp_type_widget] = False
        self._timestamp_type_widget.currentIndexChanged.connect(self._timestamp_type_update_event)

        self._registered_widgets[self._truth_widget] = False
        self._truth_widget.currentIndexChanged.connect(self._truth_update_event)

        self._registered_widgets[self._position_widget] = False
        self._position_widget.currentIndexChanged.connect(self._position_update_event)

        self._registered_widgets[self._reference_date_time_type_widget] = False
        self._reference_date_time_type_widget.currentIndexChanged.connect(self._reference_date_time_type_update_event)

        self._registered_widgets[self._date_widget] = False
        self._date_widget.dateChanged.connect(self._date_update_event)

        self._registered_widgets[self._time_check_box_widget] = False
        self._time_check_box_widget.stateChanged.connect(self._time_check_box_update_event)
        self._time_check_box_widget.stateChanged.connect(self._time_update_event)

        self._time_widget.timeChanged.connect(self._time_update_event)

        self._registered_widgets[self._offset_check_box] = False
        self._offset_check_box.toggled.connect(self._reference_date_time_offset_update_event)
        self._time_offset_direction_c_box.currentIndexChanged.connect(self._reference_date_time_offset_update_event)
        self._time_offset_years.valueChanged.connect(self._reference_date_time_offset_update_event)
        self._time_offset_months.valueChanged.connect(self._reference_date_time_offset_update_event)
        self._time_offset_weeks.valueChanged.connect(self._reference_date_time_offset_update_event)
        self._time_offset_days.valueChanged.connect(self._reference_date_time_offset_update_event)
        self._time_offset_hours.valueChanged.connect(self._reference_date_time_offset_update_event)
        self._time_offset_minutes.valueChanged.connect(self._reference_date_time_offset_update_event)
        self._time_offset_seconds.valueChanged.connect(self._reference_date_time_offset_update_event)

        self._registered_widgets[self._incl_subfolders_widget] = False
        self._incl_subfolders_widget.stateChanged.connect(self._include_subfolders_update_event)
        # ======================================================================
        # set-up
        # ======================================================================
        self._pull_file_folder()
        self._pull_timestamp_type()
        self._pull_truth()
        self._pull_position()
        self._pull_reference_date_time_type()
        self._pull_reference_date_time_timestamp()
        self._pull_reference_date_time_offsets()
        self._pull_include_subfolders()
        self._pull_include_subfolders()

    def _pull_position(self, direction="pull"):
        """ ..
        """
        options = [bs.ctrl.session.BackupFilterRuleCtrl.position_before,
                   bs.ctrl.session.BackupFilterRuleCtrl.position_on,
                   bs.ctrl.session.BackupFilterRuleCtrl.position_after
                   ]
        if direction == "push":
            self._backup_filter_rule_ctrl.position = options[self._position_widget.currentIndex()]
        elif direction == "pull":
            self._position_widget.setCurrentIndex(options.index(self._backup_filter_rule_ctrl.position))

    def _pull_reference_date_time_offsets(self, direction="pull"):
        """ ..
        """
        if direction == "push":
            if self._offset_check_box.isChecked():
                offset = []
                offset.append(1 - self._time_offset_direction_c_box.currentIndex())
                offset.append(self._time_offset_years.value())
                offset.append(self._time_offset_months.value())
                offset.append(self._time_offset_weeks.value())
                offset.append(self._time_offset_days.value())
                offset.append(self._time_offset_hours.value())
                offset.append(self._time_offset_minutes.value())
                offset.append(self._time_offset_seconds.value())
            else:
                offset = [0, 0, 0, 0, 0, 0, 0, 0]
            self._backup_filter_rule_ctrl.reference_date_time_offsets = offset
        elif direction == "pull":
            offset = self._backup_filter_rule_ctrl.reference_date_time_offsets
            self._offset_check_box.setCheckState(QtCore.Qt.Checked)
            if offset != [0, 0, 0, 0, 0, 0, 0, 0]:
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

    def _pull_reference_date_time_timestamp(self, direction="pull"):
        """ ..
        """
        if direction == "push":
            date_string = self._date_widget.text()
            if self._time_check_box_widget.isChecked():
                time_string = self._time_widget.text()
            else:
                time_string = "00:00:00"
            time_struct = time.strptime("%s %s" % (date_string,
                                                   time_string, ),
                                        "%s %s" % (self._date_display_pattern.replace("yyyy", "%Y").replace("MM", "%m").replace("dd", "%d"),
                                                   self._time_display_pattern.replace("hh", "%H").replace("mm", "%M").replace("ss", "%S"), )
                                        )
            timestamp = time.mktime(time_struct) - time.timezone
            self._backup_filter_rule_ctrl.reference_date_time_timestamp = timestamp
        elif direction == "pull":
            if self._backup_filter_rule_ctrl.reference_date_time_timestamp:  # date
                struct_time = time.gmtime(self._backup_filter_rule_ctrl.reference_date_time_timestamp)
                self._date_widget.setDate(QtCore.QDate(struct_time.tm_year,
                                                       struct_time.tm_mon,
                                                       struct_time.tm_mday))
                # time
                if (struct_time.tm_hour != 0 or
                        struct_time.tm_min != 0 or
                        struct_time.tm_sec != 0):
                    self._time_check_box_widget.setCheckState(QtCore.Qt.Checked)
                    self._time_widget.setTime(QtCore.QTime(struct_time.tm_hour,
                                                           struct_time.tm_min,
                                                           struct_time.tm_sec))
                else:
                    self._time_check_box_widget.setCheckState(QtCore.Qt.Checked)
                    self._time_check_box_widget.setCheckState(QtCore.Qt.Unchecked)

    def _pull_reference_date_time_type(self, direction="pull"):
        """ ..
        """
        options = [bs.ctrl.session.BackupFilterRuleCtrl.reference_date_current_date,
                   bs.ctrl.session.BackupFilterRuleCtrl.reference_date_file_backup,
                   bs.ctrl.session.BackupFilterRuleCtrl.reference_date_folder_backup,
                   bs.ctrl.session.BackupFilterRuleCtrl.reference_date_volume_backup,
                   bs.ctrl.session.BackupFilterRuleCtrl.reference_date_fixed
                   ]
        if direction == "push":
            self._backup_filter_rule_ctrl.reference_date_time_type = options[self._reference_date_time_type_widget.currentIndex()]
        elif direction == "pull":
            self._reference_date_time_type_widget.setCurrentIndex(options.index(self._backup_filter_rule_ctrl.reference_date_time_type))

    def _pull_timestamp_type(self, direction="pull"):
        """ ..
        """
        options = [bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_ctime,
                   bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_mtime,
                   bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_atime
                   ]
        if direction == "push":
            self._backup_filter_rule_ctrl.timestamp_type = options[self._timestamp_type_widget.currentIndex()]
        elif direction == "pull":
            self._timestamp_type_widget.setCurrentIndex(options.index(self._backup_filter_rule_ctrl.timestamp_type))

    def _push_position(self):
        self._pull_position("push")

    def _push_reference_date_time_offsets(self):
        self._pull_reference_date_time_offsets("push")

    def _push_reference_date_time_timestamp(self):
        self._pull_reference_date_time_timestamp("push")

    def _push_reference_date_time_type(self):
        self._pull_reference_date_time_type("push")

    def _push_timestamp_type(self):
        self._pull_timestamp_type("push")

    def push_data(self):
        """ ..

        :rtype: `dictionary`

        Collects and serializes the rule(-widget)'s data and returns it in a \
        dictionary. This can be used to save it back to the database.
        """
        self._push_file_folder()
        self._push_timestamp_type()
        self._push_truth()
        self._push_position()
        self._push_reference_date_time_offsets()
        self._push_reference_date_time_timestamp()
        self._push_reference_date_time_type()
        self._push_include_subfolders()
        # reset modification counters
        for item in self._registered_widgets.keys():
            self._registered_widgets[item] = False
        # send update signal
        self.update_signal.emit(self, False)

    def _date_update_event(self, text):
        """ ..

        Event that triggers when date selector is changed. Updates modified \
        state.
        """
        # update modified state
        saved_timestamp_time_struct = time.gmtime(self._backup_filter_rule_ctrl.reference_date_time_timestamp)
        form_date_time_struct = time.strptime(self._date_widget.text(),
                                              self._date_display_pattern.replace("yyyy", "%Y").replace("MM", "%m").replace("dd", "%d"))
        if (saved_timestamp_time_struct.tm_year == form_date_time_struct.tm_year and
                saved_timestamp_time_struct.tm_mon == form_date_time_struct.tm_mon and
                saved_timestamp_time_struct.tm_mday == form_date_time_struct.tm_mday):
            self._registered_widgets[self._date_widget] = False
        else:
            self._registered_widgets[self._date_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._date_widget])

    def _position_update_event(self, index):
        """ ..

        Event that triggers when position selector is changed. Updates \
        modified state.
        """
        # update modified state
        options = [bs.ctrl.session.BackupFilterRuleCtrl.position_before,
                   bs.ctrl.session.BackupFilterRuleCtrl.position_on,
                   bs.ctrl.session.BackupFilterRuleCtrl.position_after
                   ]
        if self._backup_filter_rule_ctrl.position == options[self._position_widget.currentIndex()]:
            self._registered_widgets[self._position_widget] = False
        else:
            self._registered_widgets[self._position_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._position_widget])

    def _reference_date_time_offset_update_event(self, checked_text):
        """ ..
 
        Event that fires when the "with an offset of" checkbox is clicked. \
        Shows/hides widgets used to specify the time-offset.
        """
        # update modified state
        if self._offset_check_box.isChecked():
            offset = []
            offset.append(0)
            offset.append(self._time_offset_years.value())
            offset.append(self._time_offset_months.value())
            offset.append(self._time_offset_weeks.value())
            offset.append(self._time_offset_days.value())
            offset.append(self._time_offset_hours.value())
            offset.append(self._time_offset_minutes.value())
            offset.append(self._time_offset_seconds.value())
        else:
            offset = [0, 0, 0, 0, 0, 0, 0, 0]
        if offset == self._backup_filter_rule_ctrl.reference_date_time_offsets:
            self._registered_widgets[self._offset_check_box] = False
        else:
            self._registered_widgets[self._offset_check_box] = True
        # update ui
        if self._offset_check_box.isChecked():
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

        self.update_signal.emit(self,
                                self._registered_widgets[self._offset_check_box])

    def _reference_date_time_type_update_event(self, index):
        """ ..

        Event that triggers when timestamp-type selector is changed. Updates \
        modified state and UI elements context-sensitively.
        """
        # update modified state
        options = [bs.ctrl.session.BackupFilterRuleCtrl.reference_date_current_date,
                   bs.ctrl.session.BackupFilterRuleCtrl.reference_date_file_backup,
                   bs.ctrl.session.BackupFilterRuleCtrl.reference_date_folder_backup,
                   bs.ctrl.session.BackupFilterRuleCtrl.reference_date_volume_backup,
                   bs.ctrl.session.BackupFilterRuleCtrl.reference_date_fixed
                   ]
        if self._backup_filter_rule_ctrl.reference_date_time_type == options[self._reference_date_time_type_widget.currentIndex()]:
            self._registered_widgets[self._reference_date_time_type_widget] = False
        else:
            self._registered_widgets[self._reference_date_time_type_widget] = True

        # update ui
        if index == 4:  # "fixed" is chosen, activate date/time widgets
            self._date_widget.show()
            if self._time_check_box_widget.isChecked():
                self._time_widget.show()
        else:  # anything else is chosen. Deactivate date/time widgets
            self._date_widget.hide()
            self._time_widget.hide()
        self.update_signal.emit(self,
                                self._registered_widgets[self._reference_date_time_type_widget])

    def _time_check_box_update_event(self, state):
        """ ..

        Event that triggers when timestamp-type selector is changed. Updates \
        UI elements context-sensitively.
        """
        # update modified state
        # update ui
        if self._reference_date_time_type_widget.currentIndex() == 4:
            if state:
                self._time_widget.show()
            else:
                self._time_widget.hide()

    def _time_update_event(self, text_state):
        """ ..

        Event that triggers when time selector is changed. Updates modified \
        state.
        """
        # update modified state
        saved_timestamp_time_struct = time.gmtime(self._backup_filter_rule_ctrl.reference_date_time_timestamp)
        # virtually set form time to 0 if box unchecked
        if self._time_check_box_widget.checkState() == QtCore.Qt.Checked:
            form_time_time_struct = time.strptime(self._time_widget.text(),
                                                  self._time_display_pattern.replace("hh", "%H").replace("mm", "%M").replace("ss", "%S"))
        else:
            form_time_time_struct = time.gmtime(0)
        if (saved_timestamp_time_struct.tm_hour == form_time_time_struct.tm_hour and
                saved_timestamp_time_struct.tm_min == form_time_time_struct.tm_min and
                saved_timestamp_time_struct.tm_sec == form_time_time_struct.tm_sec):
            self._registered_widgets[self._time_check_box_widget] = False
        else:
            self._registered_widgets[self._time_check_box_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._time_check_box_widget])

    def _timestamp_type_update_event(self, index):
        """ ..

        Event that triggers when timestamp-type selector is changed. Updates \
        modified state.
        """
        # update modified state
        options = [bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_ctime,
                   bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_mtime,
                   bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_atime
                   ]
        if self._backup_filter_rule_ctrl.timestamp_type == options[self._timestamp_type_widget.currentIndex()]:
            self._registered_widgets[self._timestamp_type_widget] = False
        else:
            self._registered_widgets[self._timestamp_type_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._timestamp_type_widget])


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
        # ======================================================================
        # Row 0
        # ======================================================================
        self.get_row_layout(0).addWidget(QtGui.QLabel("Path", self))
        # does/does not
        self._truth_widget = QtGui.QComboBox(self)
        self._truth_widget.addItems(["does", "does not"])
        self.get_row_layout(0).addWidget(self._truth_widget)
        # mode
        self._mode_widget = QtGui.QComboBox(self)
        self._mode_widget.addItems(["start with", "contain", "end with", "match pattern", "match regex"])
        self.get_row_layout(0).addWidget(self._mode_widget)
        # pattern
        self._pattern_widget = QtGui.QLineEdit(self)
        self._pattern_widget.setMinimumWidth(500)
        self.get_row_layout(0).addWidget(self._pattern_widget)
        # match case
        self._match_case_widget = QtGui.QCheckBox("matching case", self)
        self.get_row_layout(0).addWidget(self._match_case_widget)
        # ======================================================================
        # register
        #
        # To register and watch a widget for modification to update the rule
        # view, register widget here and connect to an update method that in
        # return updates the registered state.
        # ======================================================================
        self._registered_widgets[self._truth_widget] = False
        self._truth_widget.currentIndexChanged.connect(self._truth_update_event)

        self._registered_widgets[self._mode_widget] = False
        self._mode_widget.currentIndexChanged.connect(self._mode_update_event)

        self._registered_widgets[self._pattern_widget] = False
        self._pattern_widget.textChanged.connect(self._pattern_update_event)

        self._registered_widgets[self._match_case_widget] = False
        self._match_case_widget.stateChanged.connect(self._match_case_update_event)
        # ======================================================================
        # set-up
        # ======================================================================
        # truth
        if not self._backup_filter_rule_ctrl.truth:
            self._truth_widget.setCurrentIndex(1)
        # mode
        if self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_starts_with:
            self._mode_widget.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_contains:
            self._mode_widget.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_ends_with:
            self._mode_widget.setCurrentIndex(2)
        elif self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_match_pattern:
            self._mode_widget.setCurrentIndex(3)
        elif self._backup_filter_rule_ctrl.mode_path == bs.ctrl.session.BackupFilterRuleCtrl.mode_path_match_regex:
            self._mode_widget.setCurrentIndex(4)
        # pattern
        self._pattern_widget.setText(self._backup_filter_rule_ctrl.path_pattern)
        # match case
        if self._backup_filter_rule_ctrl.match_case:
            self._match_case_widget.setCheckState(QtCore.Qt.Checked)

    def push_data(self):
        """ ..

        :rtype: `dictionary`

        Collects and serializes the rule(-widget)'s data and returns it in a \
        dictionary. This can be used to save it back to the database.
        """

    def _mode_update_event(self, index):
        """ ..

        Event that triggers when mode selector is changed. Updates modified
        state.
        """
        # update modified state
        options = [bs.ctrl.session.BackupFilterRuleCtrl.mode_path_starts_with,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_path_contains,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_path_ends_with,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_path_match_pattern,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_path_match_regex
                   ]
        if self._backup_filter_rule_ctrl.mode_path == options[self._mode_widget.currentIndex()]:
            self._registered_widgets[self._mode_widget] = False
        else:
            self._registered_widgets[self._mode_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._mode_widget])

    def _pattern_update_event(self, text):
        """ ..

        :param str text:

        Event that triggers when pattern selector is changed. Updates modified
        state.
        """
        # update modified state
        if self._backup_filter_rule_ctrl.path_pattern == text:
            self._registered_widgets[self._pattern_widget] = False
        else:
            self._registered_widgets[self._pattern_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._pattern_widget])

    def _match_case_update_event(self, code):
        """ ..

        :param int code:

        Event that triggers when match-case selector is changed. Updates \
        modified state.
        """
        # update modified state
        if self._backup_filter_rule_ctrl.match_case == self._match_case_widget.isChecked():
            self._registered_widgets[self._match_case_widget] = False
        else:
            self._registered_widgets[self._match_case_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._match_case_widget])


class FilterEditRuleSizeView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleSizeCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the size-rule.
    """
    _file_folder_widget = None
    _incl_subfolders_widget = None
    _size_int_widget = None
    _size_float_widget = None

    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleSizeView, self).__init__(parent,
                                                     backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        # ======================================================================
        # Row 0
        # ======================================================================
        # File/Folder/Either
        self._file_folder_widget = QtGui.QComboBox(self)
        self._file_folder_widget.addItems(["File/Folder", "File", "Folder"])
        self.get_row_layout(0).addWidget(self._file_folder_widget)
        # truth
        self._truth_widget = QtGui.QComboBox(self)
        self._truth_widget.addItems(["is", "is not"])
        self.get_row_layout(0).addWidget(self._truth_widget)
        # mode size
        self._mode_size_widget = QtGui.QComboBox(self)
        self._mode_size_widget.addItems(["less than", "less or equal to", "equal to", "equal or larger than", "larger than"])
        self.get_row_layout(0).addWidget(self._mode_size_widget)
        # quantity
        self._size_int_widget = QtGui.QSpinBox(self)
        self._size_int_widget.setMaximum(1023)
        self.get_row_layout(0).addWidget(self._size_int_widget)

        self._size_float_widget = QtGui.QDoubleSpinBox(self)
        self._size_float_widget.setMaximum(1024.0)
        self._size_float_widget.setDecimals(2)
        self.get_row_layout(0).addWidget(self._size_float_widget)
        # unit
        self._unit_widget = QtGui.QComboBox(self)
        self._unit_widget.addItems(["byte(s)", "KiB", "MiB", "GiB", "TiB", "PiB"])
        self.get_row_layout(0).addWidget(self._unit_widget)
        # sub-folders
        self._incl_subfolders_widget = QtGui.QCheckBox("including subfolders",
                                                       self)
        self.get_row_layout(0).addWidget(self._incl_subfolders_widget)
        # ======================================================================
        # register
        #
        # To register and watch a widget for modification to update the rule
        # view, register widget here and connect to an update method that in
        # return updates the registered state.
        # ======================================================================
        self._registered_widgets[self._file_folder_widget] = False
        self._file_folder_widget.currentIndexChanged.connect(self._file_folder_update_event)

        self._registered_widgets[self._truth_widget] = False
        self._truth_widget.currentIndexChanged.connect(self._truth_update_event)

        self._registered_widgets[self._mode_size_widget] = False
        self._mode_size_widget.currentIndexChanged.connect(self._mode_size_update_event)

        self._registered_widgets[self._size_int_widget] = False
        self._size_int_widget.valueChanged.connect(self._size_unit_update_event)

        self._registered_widgets[self._size_float_widget] = False
        self._size_float_widget.valueChanged.connect(self._size_unit_update_event)

        self._registered_widgets[self._unit_widget] = False
        self._unit_widget.currentIndexChanged.connect(self._unit_update_event)
        self._unit_widget.currentIndexChanged.connect(self._size_unit_update_event)

        self._registered_widgets[self._incl_subfolders_widget] = False
        self._incl_subfolders_widget.stateChanged.connect(self._include_subfolders_update_event)
        # ======================================================================
        # set-up
        # ======================================================================
        # file/folder
        if self._backup_filter_rule_ctrl.file_folder == bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file_folder:
            self._file_folder_widget.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.file_folder == bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file:
            self._file_folder_widget.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.file_folder == bs.ctrl.session.BackupFilterRuleCtrl.file_folder_folder:
            self._file_folder_widget.setCurrentIndex(2)
        # truth
        if not self._backup_filter_rule_ctrl.truth:
            self._truth_widget.setCurrentIndex(1)
        # mode size
        if self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller:
            self._mode_size_widget.setCurrentIndex(0)
        elif self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller_equal:
            self._mode_size_widget.setCurrentIndex(1)
        elif self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_equal:
            self._mode_size_widget.setCurrentIndex(2)
        elif self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_larger_equal:
            self._mode_size_widget.setCurrentIndex(3)
        elif self._backup_filter_rule_ctrl.mode_size == bs.ctrl.session.BackupFilterRuleCtrl.mode_size_larger:
            self._mode_size_widget.setCurrentIndex(4)
        # size
        size = float(self._backup_filter_rule_ctrl.size)
        while size > 1023:
            size = size / 1024
        self._size_int_widget.setValue(size)
        self._size_float_widget.setValue(size)
        if self._backup_filter_rule_ctrl.size <= 1023:
            self._size_float_widget.hide()
        else:
            self._size_int_widget.hide()
        # unit
        unit_index = 0
        size = float(self._backup_filter_rule_ctrl.size)
        while True:
            if size > 1023:
                size = size / 1024
                unit_index += 1
            else:
                break
        self._unit_widget.setCurrentIndex(unit_index)
        # incl sub-folders
        if self._backup_filter_rule_ctrl.include_subfolders:
            self._incl_subfolders_widget.setCheckState(QtCore.Qt.Checked)
        else:
            self._incl_subfolders_widget.setCheckState(QtCore.Qt.Unchecked)

    def push_data(self):
        """ ..

        :rtype: `dictionary`

        Collects and serializes the rule(-widget)'s data and returns it in a \
        dictionary. This can be used to save it back to the database.
        """

    def _mode_size_update_event(self, index):
        """ ..

        Event that triggers when mode selector is changed. Updates modified
        state.
        """
        # update modified state
        options = [bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller_equal,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_size_equal,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_size_larger_equal,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_size_larger
                   ]
        if self._backup_filter_rule_ctrl.mode_size == options[self._mode_size_widget.currentIndex()]:
            self._registered_widgets[self._mode_size_widget] = False
        else:
            self._registered_widgets[self._mode_size_widget] = True
        self.update_signal.emit(self,
                                self._registered_widgets[self._mode_size_widget])

    def _size_unit_update_event(self, value_index):
        """ ..

        Event that triggers when size (int/float) and unit selectors are \
        changed. Updates modified state.
        """
        # update modified state
        self._registered_widgets[self._size_int_widget] = True
        self._registered_widgets[self._size_float_widget] = True
        if self._size_int_widget.isVisible():
            value = self._size_int_widget.value()
        else:
            value = self._size_float_widget.value()
        if int(value * pow(1024, self._unit_widget.currentIndex())) == self._backup_filter_rule_ctrl.size:
            self._registered_widgets[self._size_int_widget] = False
            self._registered_widgets[self._size_float_widget] = False
        self.update_signal.emit(self,
                                self._registered_widgets[self._size_float_widget])

    def _unit_update_event(self, index):
        """ ..

        Event that gets called when index of unit-selector is changed. \
        Switches between an integer or float combo box, depending on selected \
        unit.
        """
        # update modified state
        if index == 0 and self._size_float_widget.isVisible():  # "byte(s)" is chosen
            self._size_int_widget.show()
            self._size_float_widget.hide()
            self._size_int_widget.setValue(self._size_float_widget.value())
        elif index > 0 and self._size_int_widget.isVisible():  # any larger unit is chosen
            self._size_int_widget.hide()
            self._size_float_widget.show()
            self._size_float_widget.setValue(self._size_int_widget.value())


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
