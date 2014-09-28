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

    @property
    def current_filter_edit_view(self):
        """ ..
        """
        widget_item = self._layout.itemAtPosition(0, 1)
        if widget_item:
            widget = widget_item.widget()
            if isinstance(widget, FilterEditView):
                return widget
            else:
                return None

    def _init_ui(self):
        """ ..
        """
        # connect sessions activity signal to refresh of UI
        self._sessions_ctrl.session_activity_signal.connect(self.refresh)
        # geometry
        self.setMinimumWidth(1200)
        self.setMinimumHeight(350)
        available_geometry = QtGui.QApplication.desktop().availableGeometry(screen=0)
        x = available_geometry.width() / 2 - self.width() / 2
        y = available_geometry.height() / 2 - self.height() / 2
        self.setGeometry(x, y, self.width(), self.height())
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

        :rtype: :class:`bs.gui.window_filter_manager.FilterEditView`

        Loads the filter ``backup_filter`` into the details widget.
        """
        # remove currently loaded widget
        current_edit_widget_item = self._layout.itemAtPosition(0, 1)
        if current_edit_widget_item:
            if isinstance(current_edit_widget_item.widget(), FilterEditView):
                current_edit_widget_item.widget().save()
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
        return widget

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

    def closeEvent(self, e):
        """ ..

        Override. Saves the current filter when window is closed.
        """
        if isinstance(self.current_filter_edit_view, FilterEditView):
            self.current_filter_edit_view.save()


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
    _revert_widget = None
    _backup_filter_name_widget = None
    _update_signal = None

    def __init__(self, parent, backup_filter):
        """ ..
        """
        super(FilterEditView, self).__init__(parent)

        self._backup_filter = backup_filter
        self._registered_widgets = {}  # holds all widgets to be watched for modification

        self._update_signal = bs.utils.Signal()
        self._update_signal.connect(self._update_event)

        self._init_ui()

    @property
    def is_modified(self):
        """ ..

        :rtype: `boolean`

        Returns whether or not this filter is dirty.
        """
        modified = False
        # check itself
        for key in self._registered_widgets.keys():
            if self._registered_widgets[key]:
                modified = True
                break
        # check rule views
        for rule_view in [self._filter_rules_container._layout.itemAt(i).widget() for i in range(self._filter_rules_container._layout.count() - 1)]:
            if rule_view.is_modified:
                modified = True
                break
        return modified

    @property
    def update_signal(self):
        """ ..

        :type: `bs.ctrl.utils.Signal`

        The signal emits when anything in the filter-ui has (been) updated.
        """
        return self._update_signal

    def _add_view(self, widget, is_new=False):
        """ ..

        :param int is_new: Indicates whether or not this rule-widget is newly added to the filter. \
        Will set the rule/filter as modified so it saves even if rule is not changed at all after \
        adding.

        Does the tasks common to all self._add_view_* methods.
        """
        # register
        self._registered_widgets[widget] = False
        widget.update_signal.connect(self._update_signal.emit)
        index = self._filter_rules_container._layout.count()
        if index > 0:
            index = index - 1
        self._filter_rules_container._layout.insertWidget(index, widget)

        # set new widget modified so it is saved even if not edited
        if is_new:
            widget._registered_widgets[widget._revert_widget] = True
            self.update_signal.emit()

    def _add_view_attributes(self, backup_filter_rule=None):
        # create new controller if not provided
        if not backup_filter_rule:
            backup_filter_rule = bs.ctrl.session.BackupFilterRuleAttributesCtrl(key_id=None,
                                                                                category=bs.ctrl.session.BackupFilterRuleCtrl.category_attributes,
                                                                                file_folder=bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file_folder,
                                                                                include_subfolders=True,
                                                                                truth=True,
                                                                                attribute_type=bs.ctrl.session.BackupFilterRuleCtrl.attribute_owner,
                                                                                attribute_value=["", None, None])
            self._backup_filter.add_backup_filter_rule(backup_filter_rule)
        # add gui
        widget = FilterEditRuleAttributesView(self._filter_rules_container,
                                              backup_filter_rule)
        self._add_view(widget, is_new=True)

    def _add_view_date(self, backup_filter_rule=None):
        # create new controller if not provided
        if not backup_filter_rule:
            backup_filter_rule = bs.ctrl.session.BackupFilterRuleDateCtrl(key_id=None,
                                                                          category=bs.ctrl.session.BackupFilterRuleCtrl.category_date,
                                                                          file_folder=bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file_folder,
                                                                          include_subfolders=True,
                                                                          truth=True,
                                                                          timestamp_type=bs.ctrl.session.BackupFilterRuleCtrl.timestamp_type_atime,
                                                                          position=bs.ctrl.session.BackupFilterRuleCtrl.position_before,
                                                                          reference_date_time_type=bs.ctrl.session.BackupFilterRuleCtrl.reference_date_current_date,
                                                                          reference_date_time_timestamp=0,
                                                                          reference_date_time_offsets=[0, 0, 0, 0, 0, 0, 0, 0])
            self._backup_filter.add_backup_filter_rule(backup_filter_rule)
        # add gui
        widget = FilterEditRuleDateView(self._filter_rules_container,
                                        backup_filter_rule)
        self._add_view(widget, is_new=True)

    def _add_view_path(self, backup_filter_rule=None):
        # create new controller if not provided
        if not backup_filter_rule:
            backup_filter_rule = bs.ctrl.session.BackupFilterRulePathCtrl(key_id=None,
                                                                          category=bs.ctrl.session.BackupFilterRuleCtrl.category_path,
                                                                          file_folder=bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file_folder,
                                                                          include_subfolders=True,
                                                                          truth=True,
                                                                          mode_path=bs.ctrl.session.BackupFilterRuleCtrl.mode_path_starts_with,
                                                                          match_case=False,
                                                                          path_pattern="")
            self._backup_filter.add_backup_filter_rule(backup_filter_rule)
        # add gui
        widget = FilterEditRulePathView(self._filter_rules_container,
                                        backup_filter_rule)
        self._add_view(widget, is_new=True)

    def _add_view_size(self, backup_filter_rule=None):
        # create new controller if not provided
        if not backup_filter_rule:
            backup_filter_rule = bs.ctrl.session.BackupFilterRuleSizeCtrl(key_id=None,
                                                                          category=bs.ctrl.session.BackupFilterRuleCtrl.category_size,
                                                                          file_folder=bs.ctrl.session.BackupFilterRuleCtrl.file_folder_file_folder,
                                                                          include_subfolders=True,
                                                                          truth=True,
                                                                          mode_size=bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller_equal,
                                                                          size=0)
            self._backup_filter.add_backup_filter_rule(backup_filter_rule)
        # add gui
        widget = FilterEditRuleSizeView(self._filter_rules_container,
                                        backup_filter_rule)
        self._add_view(widget, is_new=True)

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
        self._backup_filter_name_widget = QtGui.QLineEdit(self)
        self._layout.addWidget(self._backup_filter_name_widget, 0, 1, 1, 4)
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
        add_btn_menu_action_path.activated.connect(self._add_view_path)
        add_btn_menu.addAction(add_btn_menu_action_path)

        add_btn_menu_action_size = QtGui.QAction("Size", add_btn_menu)
        add_btn_menu_action_size.activated.connect(self._add_view_size)
        add_btn_menu.addAction(add_btn_menu_action_size)

        add_btn_menu_action_date = QtGui.QAction("Date/Time", add_btn_menu)
        add_btn_menu_action_date.activated.connect(self._add_view_date)
        add_btn_menu.addAction(add_btn_menu_action_date)

        add_btn_menu_action_attributes = QtGui.QAction("Attributes", add_btn_menu)
        add_btn_menu_action_attributes.activated.connect(self._add_view_attributes)
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
                self._add_view_attributes(backup_filter_rule)
            elif isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRuleDateCtrl):
                self._add_view_date(backup_filter_rule)
            elif isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRulePathCtrl):
                self._add_view_path(backup_filter_rule)
            elif isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRuleSizeCtrl):
                self._add_view_size(backup_filter_rule)
        # buffer widget at bottom
        widget = QtGui.QWidget(self)
        self._filter_rules_container._layout.addWidget(widget)
        # ======================================================================
        # Row 3
        # ======================================================================
        self._save_widget = QtGui.QPushButton("Save", self)
        self._layout.addWidget(self._save_widget, 3, 3, 1, 1)

        self._revert_widget = QtGui.QPushButton("Revert", self)
        self._layout.addWidget(self._revert_widget, 3, 4, 1, 1)
        # ======================================================================
        # register
        #
        # To register and watch a widget for modification to update the rule
        # view, register widget here and connect to an update method that in
        # return updates the registered state.
        # ======================================================================
        self._registered_widgets[self._backup_filter_name_widget] = False
        self._backup_filter_name_widget.textChanged.connect(self._backup_filter_name_update_event)

        self._registered_widgets[self._filter_rules_mode_widget] = False
        self._filter_rules_mode_widget.currentIndexChanged.connect(self._backup_filter_rules_update_event)

        self._save_widget.clicked.connect(self.save)
        self._revert_widget.clicked.connect(self._revert)
        # ======================================================================
        # set-up
        # ======================================================================
        self.pull_data()
        # save/discard buttons
        self._save_widget.setDisabled(True)
        self._save_widget.hide()
        self._revert_widget.setDisabled(True)

    def _pull_backup_filter_name(self, direction="pull"):
        if direction == "pull":
            self._backup_filter_name_widget.setText(self._backup_filter.backup_filter_name)
        elif direction == "push":
            self._backup_filter.backup_filter_name = self._backup_filter_name_widget.text()

    def _pull_backup_filter_rules_mode(self, direction="pull"):
        options = [bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_and,
                   bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_or,
                   bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_xor
                   ]
        if direction == "pull":
            self._filter_rules_mode_widget.setCurrentIndex(options.index(self._backup_filter.backup_filter_rules_mode))
        elif direction == "push":
            self._backup_filter.backup_filter_rules_mode = options[self._filter_rules_mode_widget.currentIndex()]

    def _push_backup_filter_name(self):
        self._pull_backup_filter_name("push")

    def _push_backup_filter_rules_mode(self):
        self._pull_backup_filter_rules_mode("push")

    def _revert(self):
        """ ..

        Reverts the view to its initial state, discarding any changes made.
        """
        self.pull_data()
        # unhide all rule views
        for filter_edit_view in [self._filter_rules_container._layout.itemAt(i).widget() for i in range(self._filter_rules_container._layout.count() - 1)]:
            if filter_edit_view.isHidden():
                filter_edit_view.show()
        self._update_signal.emit()

    def pull_data(self):
        """ ..

        :rtype: `void`

        Pulls the current data off the controller onto the view, resetting it.
        """
        self._pull_backup_filter_name()
        self._pull_backup_filter_rules_mode()
        for i in range(self._filter_rules_container._layout.count() - 1):
            widget = self._filter_rules_container._layout.itemAt(i).widget()
            widget.pull_data()

    def push_data(self):
        """ ..

        :rtype: `void`

        Pushes all GUI data onto controllers.
        """
        for i in range(self._filter_rules_container._layout.count() - 1):
            widget = self._filter_rules_container._layout.itemAt(i).widget()
            widget.push_data()
        self._push_backup_filter_name()
        self._push_backup_filter_rules_mode()
        # reset modification states
        for item in self._registered_widgets:
            self._registered_widgets[item] = False

    def save(self):
        """ ..

        :rtype: `void`

        Saves the backup-filter.
        """
        if self.is_modified:
            # commit data from GUI to CTRL
            self.push_data()
            # delete rules deleted in GUI (hidden) from CTRL
            for filter_edit_view in [self._filter_rules_container._layout.itemAt(i).widget() for i in range(self._filter_rules_container._layout.count() - 1)]:
                if filter_edit_view.isHidden():
                    self._backup_filter.remove_backup_filter_rule(filter_edit_view.backup_filter_rule_ctrl)
            # save data on CTRL
            self._backup_filter.save()
            self._update_signal.emit()

    def _backup_filter_name_update_event(self, text):
        if self._backup_filter_name_widget.text() == self._backup_filter.backup_filter_name:
            self._registered_widgets[self._backup_filter_name_widget] = False
        else:
            self._registered_widgets[self._backup_filter_name_widget] = True
        self._update_signal.emit()

    def _backup_filter_rules_update_event(self, index):
        """ ..
        """
        options = [bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_and,
                   bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_or,
                   bs.ctrl.session.BackupFilterCtrl.backup_filter_rules_mode_xor
                   ]
        # set modified state
        if options[self._filter_rules_mode_widget.currentIndex()] == self._backup_filter.backup_filter_rules_mode:
            self._registered_widgets[self._filter_rules_mode_widget] = False
        else:
            self._registered_widgets[self._filter_rules_mode_widget] = True
        self._update_signal.emit()

    def _update_event(self):
        """ ..

        Is called when a registered rule-widget or detail on filter itself \
        (such as the name) is updated.
        """
        if (self._save_widget and self._revert_widget):
            if self.is_modified:
                self._save_widget.setEnabled(True)
                self._revert_widget.setEnabled(True)
            else:
                self._save_widget.setDisabled(True)
                self._revert_widget.setDisabled(True)


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
    _revert_widget = None

    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleInterface, self).__init__(parent)

        self._row_layouts = {}  # holds the horizontal row layouts
        self._registered_widgets = {}  # holds all widgets to be watched for modification
        self._update_signal = bs.utils.Signal()

        self._backup_filter_rule_ctrl = backup_filter_rule_ctrl
        # layout
        self._layout = QtGui.QGridLayout(self)
        # style
        self.setFrameStyle(self.Panel | self.Raised)
        # revert button
        icon = QtGui.QIcon("img/icons_forget.png")
        self._revert_widget = QtGui.QPushButton(icon, None)
        self._revert_widget.permanently_registered = True  # get the ``is_modified`` attributes to always consider this key
        self._revert_widget.setSizePolicy(QtGui.QSizePolicy.Fixed,
                                          QtGui.QSizePolicy.Fixed)
        self._layout.addWidget(self._revert_widget, 0, 0, 1, 1)
        # geometry
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
                           QtGui.QSizePolicy.Fixed)
        # ======================================================================
        # register
        #
        # To register and watch a widget for modification to update the rule
        # view, register widget here and connect to an update method that in
        # return updates the registered state.
        # ======================================================================
        self._update_signal.connect(self._update_event)

        self._registered_widgets[self._revert_widget] = False
        self._revert_widget.clicked.connect(self._remove)
        # ======================================================================
        # set-up
        # ======================================================================

    @property
    def backup_filter_rule_ctrl(self):
        """ ..
        """
        return self._backup_filter_rule_ctrl

    @property
    def is_modified(self):
        """ ..

        :rtype: `boolean`

        Returns whether or not this rule is dirty.
        """
        modified = False
        for key in self._registered_widgets.keys():
            if self._registered_widgets[key]:
                if key.isVisible():
                    modified = True
                    break
                elif "permanently_registered" in dir(key):
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

    def _remove(self):
        """ ..
        "Removes" the current rule-view from the layout, hiding it and sending \
        an update event.
        """
        self.hide()
        self._registered_widgets[self._revert_widget] = True
        self.update_signal.emit()

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

    def pull_data(self):
        """ ..

        Pulls the current data off the controller onto the view, resetting it.
        """
        # reset revert widget modification to mark it as not removed
        self._registered_widgets[self._revert_widget] = False
        self._update_event()

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
        self.update_signal.emit()
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
        self.update_signal.emit()

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
        self.update_signal.emit()

    def _update_event(self):
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
        self.pull_data()

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

    def pull_data(self):
        """ ..

        Pulls the current data off the controller onto the view, resetting it.
        """
        self._pull_file_folder()
        self._pull_attribute_type()
        self._pull_truth()
        self._pull_attribute_value()
        self._pull_include_subfolders()

        super(FilterEditRuleAttributesView, self).pull_data()

    def push_data(self):
        """ ..

        :rtype: `dictionary`

        Collects and serializes the rule(-widget)'s data and returns it in a \
        dictionary. This can be used to save it back to the database.
        """
        if self.is_modified:
            self._push_file_folder()
            self._push_attribute_type()
            self._push_truth()
            self._push_attribute_value()
            self._push_include_subfolders()
            # reset modification states
            for item in self._registered_widgets:
                self._registered_widgets[item] = False
            self.update_signal.emit()

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

        self.update_signal.emit()

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
        self.update_signal.emit()

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
        self.update_signal.emit()

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
        self.update_signal.emit()

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
        self.update_signal.emit()


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
        self.pull_data()

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
                offsets = []
                offsets.append(0)
                offsets.append(self._time_offset_years.value())
                offsets.append(self._time_offset_months.value())
                offsets.append(self._time_offset_weeks.value())
                offsets.append(self._time_offset_days.value())
                offsets.append(self._time_offset_hours.value())
                offsets.append(self._time_offset_minutes.value())
                offsets.append(self._time_offset_seconds.value())
                for item in offsets[1:]:
                    if item != 0:
                        offsets[0] = 1 - self._time_offset_direction_c_box.currentIndex()
                        break
            else:
                offsets = [0, 0, 0, 0, 0, 0, 0, 0]
            self._backup_filter_rule_ctrl.reference_date_time_offsets = offsets
        elif direction == "pull":
            offsets = self._backup_filter_rule_ctrl.reference_date_time_offsets
            self._offset_check_box.setCheckState(QtCore.Qt.Checked)
            if offsets != [0, 0, 0, 0, 0, 0, 0, 0]:
                self._time_offset_direction_c_box.setCurrentIndex(1 - offsets[0])
                self._time_offset_years.setValue(offsets[1])
                self._time_offset_months.setValue(offsets[2])
                self._time_offset_weeks.setValue(offsets[3])
                self._time_offset_days.setValue(offsets[4])
                self._time_offset_hours.setValue(offsets[5])
                self._time_offset_minutes.setValue(offsets[6])
                self._time_offset_seconds.setValue(offsets[7])
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
            index = options.index(self._backup_filter_rule_ctrl.reference_date_time_type)
            if index == 0:
                self._reference_date_time_type_widget.setCurrentIndex(1)
            self._reference_date_time_type_widget.setCurrentIndex(index)

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

    def pull_data(self):
        """ ..

        Pulls the current data off the controller onto the view, resetting it.
        """
        self._pull_file_folder()
        self._pull_timestamp_type()
        self._pull_truth()
        self._pull_position()
        self._pull_reference_date_time_type()
        self._pull_reference_date_time_timestamp()
        self._pull_reference_date_time_offsets()
        self._pull_include_subfolders()
        self._pull_include_subfolders()

        super(FilterEditRuleDateView, self).pull_data()

    def push_data(self):
        """ ..

        :rtype: `dictionary`

        Collects and serializes the rule(-widget)'s data and returns it in a \
        dictionary. This can be used to save it back to the database.
        """
        if self.is_modified:
            self._push_file_folder()
            self._push_timestamp_type()
            self._push_truth()
            self._push_position()
            self._push_reference_date_time_offsets()
            self._push_reference_date_time_timestamp()
            self._push_reference_date_time_type()
            self._push_include_subfolders()
            # reset modification states
            for item in self._registered_widgets:
                self._registered_widgets[item] = False
            self.update_signal.emit()

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
        self.update_signal.emit()

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
        self.update_signal.emit()

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
            for item in offset[1:]:
                if item != 0:
                    offset[0] = 1 - self._time_offset_direction_c_box.currentIndex()
                    break
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

        self.update_signal.emit()

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
        self.update_signal.emit()

    def _time_check_box_update_event(self, state):
        """ ..

        Event that triggers when timestamp-type selector is changed. Updates \
        UI elements context-sensitively.
        """
        # update modified state
        # update ui
        if self._reference_date_time_type_widget.currentIndex() == 4:
            if state == QtCore.Qt.Checked:
                self._time_widget.show()
            elif state == QtCore.Qt.Unchecked:
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
        self.update_signal.emit()

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
        self.update_signal.emit()


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
        self.pull_data()

    def _pull_match_case(self, direction="pull"):
        """ ..
        """
        options = {True: QtCore.Qt.Checked,
                   False: QtCore.Qt.Unchecked
                   }
        if direction == "push":
            if self._match_case_widget.checkState() == QtCore.Qt.Checked:
                self._backup_filter_rule_ctrl.match_case = True
            elif self._match_case_widget.checkState() == QtCore.Qt.Unchecked:
                self._backup_filter_rule_ctrl.match_case = False
        elif direction == "pull":
            self._match_case_widget.setCheckState(options[self._backup_filter_rule_ctrl.match_case])

    def _pull_mode_path(self, direction="pull"):
        """ ..
        """
        options = [bs.ctrl.session.BackupFilterRuleCtrl.mode_path_starts_with,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_path_contains,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_path_ends_with,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_path_match_pattern,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_path_match_regex
                   ]
        if direction == "push":
            self._backup_filter_rule_ctrl.mode_path = options[self._mode_widget.currentIndex()]
        elif direction == "pull":
            self._mode_widget.setCurrentIndex(options.index(self._backup_filter_rule_ctrl.mode_path))

    def _pull_path_pattern(self, direction="pull"):
        """ ..
        """
        if direction == "push":
            self._backup_filter_rule_ctrl.path_pattern = self._pattern_widget.text()
        elif direction == "pull":
            self._pattern_widget.setText(self._backup_filter_rule_ctrl.path_pattern)

    def _push_match_case(self):
        self._pull_match_case("push")

    def _push_mode_path(self):
        self._pull_mode_path("push")

    def _push_path_pattern(self):
        self._pull_path_pattern("push")

    def pull_data(self):
        """ ..

        Pulls the current data off the controller onto the view, resetting it.
        """
        self._pull_truth()
        self._pull_mode_path()
        self._pull_path_pattern()
        self._pull_match_case()

        super(FilterEditRulePathView, self).pull_data()

    def push_data(self):
        """ ..

        :rtype: `dictionary`

        Collects and serializes the rule(-widget)'s data and returns it in a \
        dictionary. This can be used to save it back to the database.
        """
        if self.is_modified:
            self._push_truth()
            self._push_mode_path()
            self._push_path_pattern()
            self._push_match_case()
            # reset modification states
            for item in self._registered_widgets:
                self._registered_widgets[item] = False
            self.update_signal.emit()

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
        self.update_signal.emit()

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
        self.update_signal.emit()

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
        self.update_signal.emit()


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
        self.pull_data()

    def _pull_mode_size(self, direction="pull"):
        """ ..
        """
        options = [bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_size_smaller_equal,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_size_equal,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_size_larger_equal,
                   bs.ctrl.session.BackupFilterRuleCtrl.mode_size_larger
                   ]
        if direction == "push":
            self._backup_filter_rule_ctrl.mode_size = options[self._mode_size_widget.currentIndex()]
        elif direction == "pull":
            self._mode_size_widget.setCurrentIndex(options.index(self._backup_filter_rule_ctrl.mode_size))

    def _pull_size(self, direction="pull"):
        """ ..
        """
        if direction == "push":
            if self._size_int_widget.isVisible():
                size = int(self._size_int_widget.text()) * pow(1024, self._unit_widget.currentIndex())
            else:
                size = float(self._size_float_widget.text()) * pow(1024, self._unit_widget.currentIndex())
            self._backup_filter_rule_ctrl.size = size
        elif direction == "pull":
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

    def _push_mode_size(self):
        self._pull_mode_size("push")

    def _push_size(self):
        self._pull_size("push")

    def pull_data(self):
        """ ..

        Pulls the current data off the controller onto the view, resetting it.
        """
        self._pull_file_folder()
        self._pull_truth()
        self._pull_mode_size()
        self._pull_size()
        self._pull_include_subfolders()

        super(FilterEditRuleSizeView, self).pull_data()

    def push_data(self):
        """ ..

        :rtype: `dictionary`

        Collects and serializes the rule(-widget)'s data and returns it in a \
        dictionary. This can be used to save it back to the database.
        """
        if self.is_modified:
            self._push_file_folder()
            self._push_truth()
            self._push_mode_size()
            self._push_size()
            self._push_include_subfolders()
            # reset modification states
            for item in self._registered_widgets:
                self._registered_widgets[item] = False
            self.update_signal.emit()

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
        self.update_signal.emit()

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
        self.update_signal.emit()

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
        # iterate through items
        for item in self.items:
            # lock/unlock if necessary
            if not item.backup_filter.session.is_logged_in or not item.backup_filter.session.is_unlocked:
                item.set_disabled()
            else:
                item.set_enabled()

    def load_current_item(self):
        """ ..

        :rtype: `void`

        Loads the currently selected item.
        """
        current_item = None
        if len(self.selectedItems()) > 0:
            current_item = self.selectedItems()[0]
        if current_item:
            if current_item.is_enabled:
                filter_view = self._window_filter_manager.load_filter(current_item._backup_filter)


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
