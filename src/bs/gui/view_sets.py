# -*- coding: utf-8 -*-

###############################################################################
##    bs.gui.view_sets                                                       ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  May 16, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################

""" * """

from PySide import QtCore, QtGui
import bs.config
import bs.messages.general
import re
import time


class ViewSets(QtGui.QWidget):
    """ * """
    _sesson_gui = None

    _layout = None
    _sets_list = None
    _sets_details = None

    def __init__(self, session_gui):
        super(ViewSets, self).__init__()

        self._sesson_gui = session_gui

        self._init_ui()

    @property
    def sets_details(self):
        return self._sets_details

    def _init_ui(self):
        """ * """
        # layout
        self._layout = QtGui.QGridLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        # sets list
        self._sets_list = ViewSetsSetsList(self._sesson_gui, self)
        self._layout.addWidget(self._sets_list, 0, 0, 1, 1)
        # details panel
        self._sets_details = ViewSetsDetails(self._sesson_gui)
        self._layout.addWidget(self._sets_details, 0, 1, 1, 3)
        self.refresh()

    def resizeEvent(self, e):
        """ * """
        main_window_width = self._sesson_gui.main_window.width()
        main_window_height = self._sesson_gui.main_window.height()
        # ADJUST LAYOUT
        target_width = None
        weight = 0.2
        if main_window_width < 100 / weight: target_width = 100
        elif main_window_width > 270 / weight: target_width = 270
        else: target_width = int(main_window_width * weight)
        self._layout.setColumnMinimumWidth(0, target_width)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 99)
        # sources
        if self._sets_details.sources_widget:
            self._sets_details.sources_widget.refresh_pos()

    def refresh(self):
        """ * """
        # list
        self._sets_list.refresh()
        # details
        if self._sets_list.item(0):
            self._sets_details.refresh(self._sets_list.item(0))


class ViewSetsSetsList(QtGui.QListWidget):
    """ * """
    _session_gui = None
    _view_sets = None

    _context_menu = None

    def __init__(self, session_gui, view_sets):
        super(ViewSetsSetsList, self).__init__()

        self._session_gui = session_gui
        self._view_sets = view_sets

        self._init_ui()

    def _init_ui(self):
        """ * """
        self.itemChanged.connect(self.rename_item)
        self.setSortingEnabled(True)

    def rename_item(self, item):
        """ *
        Fires when item in list view has been changed (e.g. renamed).
        """
        # VALIDATE DATA
        if not re.match(bs.config.REGEX_PATTERN_NAME, item.text()):
            dialog = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                       "Invalid Name",
                                       bs.messages.general.PATTERN_NAME_INVALID()[0])
            dialog.setDetailedText(bs.messages.general.PATTERN_NAME_INVALID()[1])
            dialog.exec_()
            self.refresh()
            return False
        # RENAME OBJECT
        item.backup_set.set_name = item.text()
        return True

    def mousePressEvent(self, e):
        """ * """
        item_clicked = self.itemAt(e.x(), e.y())
        # right-click
        if e.button() & QtCore.Qt.RightButton:
            # show context menu
            if item_clicked:
                self.setCurrentItem(item_clicked)
                item_clicked.context_menu.popup(e.globalPos())
        else:
            if not item_clicked:
                if self.currentItem():
                    self.currentItem().setSelected(False)
            else:
                self._view_sets.sets_details.refresh(item_clicked)
                super(ViewSetsSetsList, self).mousePressEvent(e)

    def refresh(self):
        """ * """
        self.clear()
        for backup_set in self._session_gui.session.backup_sets.sets:
            self.addItem(ViewSetsSetsListItem(self._session_gui,
                                              backup_set,
                                              self))


class ViewSetsSetsListItem(QtGui.QListWidgetItem):
    """ * """
    _session_gui = None
    _backup_set = None
    _list_widget = None

    _context_menu = None

    def __init__(self, session_gui, backup_set, list_widget):
        super(ViewSetsSetsListItem, self).__init__()

        self._session_gui = session_gui
        self._backup_set = backup_set
        self._list_widget = list_widget

        self._init_ui()

    def _init_ui(self):
        """ * """
        self.setText(self._backup_set.set_name)
        self.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        # context menu
        self._context_menu = ViewSetsSetsListItemCMenu(self._session_gui,
                                                       self._list_widget,
                                                       self)

    @property
    def backup_set(self):
        """ * """
        return self._backup_set

    @property
    def context_menu(self):
        return self._context_menu


class ViewSetsSetsListItemCMenu(QtGui.QMenu):
    """ * """
    _session_gui = None
    _list_widget = None
    _list_widget_item = None  # This is the QListWidgetItem that the menu was opened upon

    _action_del = None

    def __init__(self, session_gui, list_widget, list_widget_item):
        """ * """
        super(ViewSetsSetsListItemCMenu, self).__init__()

        self._session_gui = session_gui
        self._list_widget = list_widget
        self._list_widget_item = list_widget_item

        self._init_ui()

    def _init_ui(self):
        self._action_del = QtGui.QAction("Delete", self)
        self._action_del.triggered.connect(self.action_del)
        self.addAction(self._action_del)

    def action_del(self):
        """ *
        Executed when action `action_del` is triggered.
        """
        confirm_msg_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                   "Confirm Deletion",
                                   "Are you sure you want to delete the "\
                                   "following backup-set?\n\n"\
                                   "%s" % (self._list_widget_item.backup_set.set_name, ))
        dialog_btn_cancel = confirm_msg_box.addButton(QtGui.QMessageBox.Cancel)
        dialog_btn_ok = confirm_msg_box.addButton(QtGui.QMessageBox.Ok)
        confirm_msg_box.exec_()
        # if OK was pressed, delete set
        if confirm_msg_box.clickedButton() is dialog_btn_ok:
            set_id = self._list_widget_item.backup_set.set_id
            self._session_gui.session.backup_sets.remove(set_id)
        # refresh list
        self._list_widget.refresh()


class ViewSetsDetails(QtGui.QWidget):
    """ * """
    _session_gui = None

    _sources_widget = None
    _list_widget_item = None

    def __init__(self, sesson_gui):
        super(ViewSetsDetails, self).__init__()

        self._session_gui = sesson_gui

        self._init_ui()

    @property
    def sources_widget(self):
        return self._sources_widget

    @property
    def list_widget_item(self):
        return self._list_widget_item

    def _init_ui(self):
        """ * """
        pass

    def refresh(self, list_widget_item=None):
        """ * """
        # get active QListWidgetItem
        self._list_widget_item = list_widget_item
        # rebuild widgets
        if self._sources_widget:
            self._sources_widget.deleteLater()
        self._sources_widget = ViewSetsDetailsSources(self,
                                                      self._session_gui,
                                                      self._list_widget_item)


class ViewSetsDetailsSources(QtGui.QFrame):
    """ * """
    _session_gui = None
    _view_sets_details = None
    _list_widget_item = None

    _layout = None
    _title = None

    def __init__(self, owner, session_gui, list_widget_item):
        super(ViewSetsDetailsSources, self).__init__(owner)

        self._session_gui = session_gui
        self._view_sets_details = owner
        self._list_widget_item = list_widget_item

        self._init_ui()
        self.refresh_pos()
        self.show()

    def _init_ui(self):
        """ * """
        self.setStyleSheet(".ViewSetsDetailsSources {background: #c7c7ff; border-radius: 2px}")
        self._layout = QtGui.QGridLayout(self)
        self._layout.setContentsMargins(5, 5, 5, 5)
        self._layout.setSpacing(5)
        self._layout.setRowMinimumHeight(0, 13)
        self._layout.setRowStretch(0, 1)
        # title
        self._title = QtGui.QLabel("Sources")
        self._title.setStyleSheet("margin-left: 1px; font-weight: bold")
        self._layout.addWidget(self._title, 0, 0, 1, 1)
        # ADD SOURCE WIDGETS
        i = 0
        new_height = 0
        for source in self._list_widget_item.backup_set.sources:
            widget = ViewSetsDetailsSource(self, source, self._list_widget_item.backup_set)
            self._layout.setRowMinimumHeight(i + 1, widget.height())
            self._layout.setRowStretch(i + 1, 1)
            self._layout.addWidget(widget, i + 1, 0, 1, 1)
            i += 1
        # resize
        last_widget = QtGui.QFrame()
        self._layout.addWidget(last_widget, i + 1, 0, 1, 1)
        self._layout.setRowStretch(i + 1, 100)
        new_height += self._layout.contentsMargins().top() + self._layout.contentsMargins().bottom()
        new_height += self._layout.spacing() * (i + 1)
        new_height += self._layout.rowMinimumHeight(0) * 2
        new_height += (widget.height() + 2) * i
        self.setGeometry(5, 5, 200, new_height)

    def refresh_pos(self):
        """ * """
        self.setGeometry(self.x(),
                         self._view_sets_details.height() / 2 - self.height() / 2,
                         self.width(),
                         self.height())


class ViewSetsDetailsSource(QtGui.QFrame):
    """ * """
    _parent = None
    _backup_source = None

    _layout = None
    _context_menu = None

    def __init__(self, owner, backup_source, backup_set):
        super(ViewSetsDetailsSource, self).__init__(owner)

        self._parent = owner
        self._backup_source = backup_source
        self._backup_set = backup_set

        self._init_ui()

    @property
    def context_menu(self):
        return self._context_menu

    def _init_ui(self):
        """ * """
        self._layout = QtGui.QGridLayout(self)

        # title
        backup_name = self._backup_source.source_name
        title_widget = QtGui.QLabel(backup_name, self)
        title_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._layout.addWidget(title_widget, 0, 0, 1, 1)

        # del button

        # path
        backup_path = self._backup_source.source_path
        path_widget = QtGui.QLabel(backup_path, self)
        path_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        path_widget.setStyleSheet(".QLabel {border: 0px; color: #808080}")
        self._layout.addWidget(path_widget, 1, 0, 1, 1)

        self.setGeometry(0, 0, self._parent.width(), 50)
        self.setStyleSheet(".ViewSetsDetailsSource {background: #f0f0f0; border: 1px solid #FFFFFF; border-radius: 2px} .ViewSetsDetailsSource:hover {background: #FFFFFF}")

        # context menu
        self._context_menu = ViewSetsDetailsSourceCMenu()
        self._context_menu.triggered.connect(self.remove)

    def mousePressEvent(self, e):
        """ * """
        if e.button() & QtCore.Qt.RightButton:
            # show context menu
            self.context_menu.popup(e.globalPos())

    def remove(self):
        """ *
        Removes the backup_source from the backup-set.
        """
        confirm_msg_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                            "Confirm Removal",
                                            "Are you sure you want to remove the following backup-source from this backup-set (%s)?\n\n%s\n\nThis source itself will not be deleted."
                                            % (self._backup_set.set_name,
                                               self._backup_source.source_name, ))
        dialog_btn_cancel = confirm_msg_box.addButton(QtGui.QMessageBox.Cancel)
        dialog_btn_ok = confirm_msg_box.addButton(QtGui.QMessageBox.Ok)
        confirm_msg_box.exec_()
        # if OK was pressed, remove source
        if confirm_msg_box.clickedButton() is dialog_btn_ok:
            source_id = self._backup_source.source_id
            self._session_gui.session.backup_sets.remove(source_id)
#        # refresh list
#        self._list_widget.refresh()


class ViewSetsDetailsSourceCMenu(QtGui.QMenu):
    """ * """

    _action_rem = None

    def __init__(self):
        super(ViewSetsDetailsSourceCMenu, self).__init__("sdf")

        self._init_ui()

    def _init_ui(self):
        """ * """
        self._action_rem = QtGui.QAction("Remove", self)
        self.addAction(self._action_rem)
