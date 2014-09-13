#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

The window GUI that hosts the *Filter-Manager* and all its widgets.
"""

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
        # connect sessions activity signal to refresh of ui
        self._sessions_ctrl.session_activity_signal.connect(self.refresh)
        # geometry
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
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

    def __init__(self, parent, backup_filter):
        """ ..
        """
        super(FilterEditView, self).__init__(parent)

        self._backup_filter = backup_filter

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        # title
        title = QtGui.QLabel(self)
        title.setStyleSheet("font-size: 14px; font-weight: 500")
        title.setMaximumHeight(30)
        title.setText(self._backup_filter.backup_filter_name)
        self._layout.addWidget(title, 0, 0, 1, 1)
        # empty placeholder widget for now
        self._layout.addWidget(QtGui.QWidget(self), 1, 0, 1, 1)

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

    def mouseReleaseEvent(self, e):
        """ ..

        Override. Triggers load of clicked item.
        """
        super(FilterListView, self).mouseReleaseEvent(e)

        clicked_item = self.itemAt(e.x(), e.y())
        if clicked_item and clicked_item.is_enabled:
            self._window_filter_manager.load_filter(clicked_item._backup_filter)


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
