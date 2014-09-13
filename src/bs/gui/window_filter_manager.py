#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

The window GUI that hosts the *Filter-Manager* and all its widgets.
"""

import re

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
        self.setMinimumWidth(800)
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
        # geometry
        self.setMinimumWidth(550)
        # title
        self._layout.addWidget(QtGui.QLabel("Name", self), 0, 0, 1, 1)
        line_edit = QtGui.QLineEdit(self._backup_filter.backup_filter_name, self)
        self._layout.addWidget(line_edit, 0, 1, 1, 3)
        # logical mode selector
        mode_cbox = QtGui.QComboBox(self)
        mode_cbox.addItems(["All filters (AND)", "Any filter (OR)", "Only one filter (XOR)"])
        self._layout.addWidget(mode_cbox, 1, 1, 1, 1)
        self._layout.addWidget(QtGui.QLabel("must meet specified criteria.", self), 1, 2, 1, 1)
        # ======================================================================
        # add menu
        # ======================================================================
        add_btn = QtGui.QPushButton(self)
        add_btn.setText("Add filter aspect")
        add_btn_menu = QtGui.QMenu(add_btn)
        # actions
        add_btn_menu_action_path = QtGui.QAction("Path", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_path)
        add_btn_menu_action_size = QtGui.QAction("Size", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_size)
        add_btn_menu_action_date = QtGui.QAction("Date", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_date)
        add_btn_menu_action_age = QtGui.QAction("Age", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_age)
        add_btn_menu_action_attributes = QtGui.QAction("Attributes", add_btn_menu)
        add_btn_menu.addAction(add_btn_menu_action_attributes)

        add_btn.setMenu(add_btn_menu)
        self._layout.addWidget(add_btn, 1, 3, 1, 1)
        # filter rule container, embedded in a scroll-area
        scroll_area = QtGui.QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        self._filter_rules_container = QtGui.QWidget(scroll_area)
        self._filter_rules_container._layout = QtGui.QVBoxLayout(self._filter_rules_container)
        self._filter_rules_container._layout.setContentsMargins(0, 0, 0, 0)
        self._filter_rules_container._layout.setSpacing(0)

        scroll_area.setWidget(self._filter_rules_container)
        self._layout.addWidget(scroll_area, 2, 0, 1, 4)
        # add filter rules
        for backup_filter_rule in self._backup_filter.backup_filter_rules:
            widget = None
            if isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRuleAgeCtrl):
                widget = FilterEditRuleAgeView(self._filter_rules_container, backup_filter_rule)
            elif isinstance(backup_filter_rule, bs.ctrl.session.BackupFilterRuleAttributesCtrl):
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
        # info text
        info_text = QtGui.QLabel(self)
        info_text.setText("Select a filter to edit its details.")
        self._layout.addWidget(info_text, 0, 0, 1, 1)


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
        self.setMinimumHeight(50)
        self.setMaximumHeight(50)

        # del button
        icon = QtGui.QIcon("img/icons_forget.png")
        widget = QtGui.QPushButton(icon, None)
        self._layout.addWidget(widget, 0, self._layout.count(), 1, 1)


class FilterEditRuleAgeView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleAgeCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the age-rule.
    """
    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleAgeView, self).__init__(parent,
                                                      backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """


class FilterEditRuleAttributesView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleAttributesCtrl backup_filter_ctrl: \
    The backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the attributes-rule.
    """
    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleAttributesView, self).__init__(parent,
                                                             backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """


class FilterEditRuleDateView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleDateCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the date-rule.
    """
    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleDateView, self).__init__(parent,
                                                       backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """


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
        self._layout.addWidget(QtGui.QLabel("Path pattern", self),
                               0, self._layout.count(), 1, 1)
        # does/does not
        widget = QtGui.QComboBox(self)
        widget.addItems(["does", "does not"])
        self._layout.addWidget(widget, 0, self._layout.count(), 1, 1)
        # mode
        c_box = QtGui.QComboBox(self)
        c_box.addItems(["start with", "contain", "end with", "match regex"])
        self._layout.addWidget(c_box, 0, self._layout.count(), 1, 1)
        # pattern
        self._layout.addWidget(QtGui.QLineEdit(self._backup_filter_rule_ctrl.path_pattern, self),
                               0, self._layout.count(), 1, 1)
        # match case
        self._layout.addWidget(QtGui.QLabel("and", self),
                               0, self._layout.count(), 1, 1)
        check_box = QtGui.QCheckBox("match case", self)
        if self._backup_filter_rule_ctrl.match_case:
            check_box.setCheckState(QtCore.Qt.Checked)
        self._layout.addWidget(check_box, 0, self._layout.count(), 1, 1)


class FilterEditRuleSizeView(FilterEditRuleInterface):
    """ ..

    :param QtGui.QWidget parent: The widget to act as a parent.

    :param bs.ctrl.session.BackupFilterRuleSizeCtrl backup_filter_ctrl: The \
    backup-filter-rule managed by this GUI.

    **Inherits from:** \
    :class:`bs.gui.backup_filter_manager.FilterEditRuleInterface`

    This is the edit-view for the size-rule.
    """
    def __init__(self, parent, backup_filter_rule_ctrl):
        """ ..
        """
        super(FilterEditRuleSizeView, self).__init__(parent,
                                                       backup_filter_rule_ctrl)

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        self._layout.addWidget(QtGui.QLabel("File size"), 0, self._layout.count(), 1, 1)
        # is/is not
        widget = QtGui.QComboBox(self)
        widget.addItems(["is", "is not"])
        self._layout.addWidget(widget, 0, self._layout.count(), 1, 1)
        # less, less/equal, equal, equal/larger, larger
        widget = QtGui.QComboBox(self)
        widget.addItems(["less than", "less or equal to", "equal to", "equal or larger than", "larger than"])
        self._layout.addWidget(widget, 0, self._layout.count(), 1, 1)
        # quantity

        class Validator(QtGui.QValidator):
            def validate(self, arg_1, arg_2):
                if not re.match("^\d*$", arg_1):
                    return QtGui.QValidator.Invalid
                else:
                    return QtGui.QValidator.Acceptable
        validator = Validator(self)
        widget = QtGui.QLineEdit(self)
        widget.setValidator(validator)
        self._layout.addWidget(widget, 0, self._layout.count(), 1, 1)
        # unit
        widget = QtGui.QComboBox(self)
        widget.addItems(["byte(s)", "KiB", "MiB", "GiB", "TiB", "PiB"])
        self._layout.addWidget(widget, 0, self._layout.count(), 1, 1)


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
