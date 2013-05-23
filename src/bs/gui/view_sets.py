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
import bs.gui.lib
import bs.messages.general
import re
import time


class BS(QtGui.QFrame):
    """ * """
    _session_gui = None
    _backup_sets = None

    resizeSignal = QtCore.Signal(QtGui.QResizeEvent)
    _menu_sets = None
    _bs_sets_canvas = None

    def __init__(self, session_gui):
        super(BS, self).__init__()

        self._session_gui = session_gui
        self._backup_sets = session_gui.session.backup_sets

        self._init_ui()

    def _init_ui(self):
        """ * """
        self._menu_sets = BSMenu(self, self._backup_sets)
        self._bs_sets_canvas = BSSetsCanvas(self)

    def resizeEvent(self, e):
        """ * """
        self.resizeSignal.emit(e)


class BSSetsCanvas(bs.gui.lib.BSCanvas):
    """ * """

    _bs_sources_widgets = None

    def __init__(self, parent):
        super(BSSetsCanvas, self).__init__(parent)

        self._bs_sources_widgets = []

        self._init_ui()
        self.lower()

    def _init_ui(self):
#        self.setStyleSheet("background: red")

        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
#        # add sources
#        self._bs_sources = BSSource(self)
#        self._bs_sources.show()
#        # add filters
#        self._bs_filters = BSFilters(self)
#        self._bs_filters.show()
#        # add targets
#        self._bs_targets = BSTargets(self)
#        self._bs_targets.show()
#        # connect widgets
#        self._arrow_1 = BSArrow(self._bs_sources, self._bs_filters)
#        self._arrow_2 = BSArrow(self._bs_filters, self._bs_targets)
#        # lay out widgets
#        menu_width = self.parent()._menu_sets.width()
#        self._bs_sources.setGeometry((self.width() - menu_width) * 0.25 + menu_width - self._bs_sources.width() / 2,
#                                     self.height() / 2 - self._bs_sources.height() / 2,
#                                     self._bs_sources.width(),
#                                     self._bs_sources.height())
#        self._bs_filters.setGeometry((self.width() - menu_width) * 0.5 + menu_width - self._bs_filters.width() / 2,
#                                     self.height() / 2 - self._bs_filters.height() / 2,
#                                     self._bs_filters.width(),
#                                     self._bs_filters.height())
#        self._bs_targets.setGeometry((self.width() - menu_width) * 0.75 + menu_width - self._bs_targets.width() / 2,
#                                     self.height() / 2 - self._bs_targets.height() / 2,
#                                     self._bs_targets.width(),
#                                     self._bs_targets.height())
#        self._bs_sources.draw_arrows()
#        self._bs_filters.draw_arrows()
#        self._bs_targets.draw_arrows()

    def load_set(self, backup_set):
        """ *
        Loads a backup-set onto the canvas.
        """
        # clean canvas, delete old widgets
        for bs_sources_widget in self._bs_sources_widgets:
            bs_sources_widget.deleteLater()
        self._bs_sources_widgets = []
        # Load backup-sources
        for backup_source in backup_set.sources:
            widget = BSSource(self, backup_source)
            self._bs_sources_widgets.append(widget)
        # load filters
        # loat target set
        # connect nodes
        # LAY-OUT NODES
        # sources
        n = len(self._bs_sources_widgets)
        for bs_sources_widget in self._bs_sources_widgets:
            i = self._bs_sources_widgets.index(bs_sources_widget)
            x_c = self.width() * .25
            y_c = self.height() / (n + 1) * (i + 1)
            x = x_c - bs_sources_widget.width() / 2
            y = y_c - bs_sources_widget.height() / 2
            bs_sources_widget.setGeometry(x, y,
                                          bs_sources_widget.width(),
                                          bs_sources_widget.height())
        self.update()


class BSMenu(bs.gui.lib.BSNode):
    """ * """
    _bs = None
    _backup_sets = None

    _x_c = None
    _y_c = None

    def __init__(self, bs, backup_sets):
        super(BSMenu, self).__init__(bs)

        self._bs = bs
        self._backup_sets = backup_sets

        self.parent().resizeSignal.connect(self.resizeEvent)

        self._init_ui()

    def _init_ui(self):
        # these MUST be floats!
        self._x_c = float(0.0)
        self._y_c = float(0.0)
        # title
        self.title_text = "Sets"
        self.title_size = 18
        # populate with set buttons
        self.populate()
        # set pos
        self.show()
        self.setGeometry(20,
                         self.parent().height() / 2 - self.height() / 2,
                         self.width(),
                         self.height())
        self._x_c = self.x() + self.width() / 2
        self._y_c = self.y() + self.height() / 2

    def populate(self):
        """ *
        Populates the menu with BSNodeItem
        """
        for backup_set in self._backup_sets.sets:
            widget = BSMenuItem(self, backup_set, self._bs)
            self.add_item(widget)

    def mouseMoveEvent(self, e):
        """ * """
        self._x_c = self.x() + self.width() / 2
        self._y_c = self.y() + self.height() / 2
        super(BSMenu, self).mouseMoveEvent(e)

    def resizeEvent(self, e):
        """ * """
        if e.oldSize().width() > 0:
            x = self._x_c - self.width() / 2
            y = self._y_c - self.height() / 2
            scale_factor_x = (e.size().width() / e.oldSize().width())
            scale_factor_y = (e.size().height() / e.oldSize().height())
            delta_y = e.size().height() - e.oldSize().height()
            # x
            if self.x() >= 0:
                x_new = x * scale_factor_x
            else:
                x_new = x
            # y
            if self._y_c < 0:
                y_new = self._y_c - self.height() / 2
            elif self._y_c > e.size().height():
                y_new = self._y_c - self.height() / 2 + delta_y
            else:
                y_new = self._y_c * scale_factor_y - self.height() / 2
            self.setGeometry(x_new,
                             y_new,
                             self.width(),
                             self.height())
            self._x_c = x_new + self.width() / 2
            self._y_c = y_new + self.height() / 2
        super(BSMenu, self).resizeEvent(e)


class BSMenuItem(bs.gui.lib.BSNodeItem):
    """ * """

    _bs_menu = None
    _backup_set = None
    _bs = None

    def __init__(self, bs_menu, backup_set, bs):
        super(BSMenuItem, self).__init__(bs_menu)

        self._bs_menu = bs_menu
        self._backup_set = backup_set
        self._bs = bs

        self._init_ui()

    def _init_ui(self):
        """ * """
        self.title_text = self._backup_set.set_name

    def mousePressEvent(self, e):
        """ * """
        super(BSMenuItem, self).mousePressEvent(e)

        self._bs._bs_sets_canvas.load_set(self._backup_set)


class BSSource(bs.gui.lib.BSNode):
    """ * """
    _backup_source = None
    _bs_sets_canvas = None

    def __init__(self, bs_sets_canvas, backup_source):
        super(BSSource, self).__init__(bs_sets_canvas)

        self._backup_source = backup_source
        self._bs_sets_canvas = bs_sets_canvas

        self._init_ui()

    def _init_ui(self):
        # title
        self.title_text = self._backup_source.source_name
        self.title_size = 13
        # populate with item
        widget = BSSourceItem(self, self._backup_source)
        self.add_item(widget)
        self.show()


class BSSourceItem(bs.gui.lib.BSNodeItem):
    """ * """
    _bs_source = None
    _backup_source = None

    def __init__(self, bs_source, backup_source):
        super(BSSourceItem, self).__init__(bs_source)

        self._bs_source = bs_source
        self._backup_source = backup_source

        self._init_ui()

    def _init_ui(self):
        """ * """
        self.title_text = self._backup_source.source_name


#class ViewSets(QtGui.QWidget):
#    """ * """
#    _sesson_gui = None
#
#    _layout = None
#    _sets_list = None
#    _sets_details = None
#    _scroll_area = None
#
#    def __init__(self, session_gui):
#        super(ViewSets, self).__init__()
#
#        self._sesson_gui = session_gui
#
#        self._init_ui()
#
#    @property
#    def sets_list(self):
#        return self._sets_list
#
#    @property
#    def sets_details(self):
#        return self._sets_details
#
#    @property
#    def scroll_area(self):
#        return self._scroll_area
#
#    def _init_ui(self):
#        """ * """
#        # layout
#        self._layout = QtGui.QGridLayout()
#        self._layout.setSpacing(0)
#        self._layout.setContentsMargins(0, 0, 0, 0)
#        self.setLayout(self._layout)
#        # sets list
#        self._sets_list = ViewSetsSetsList(self._sesson_gui, self)
#        self._layout.addWidget(self._sets_list, 0, 0, 1, 1)
#        # details panel
#        self._scroll_area = QtGui.QScrollArea(self)
#        self._scroll_area.setContentsMargins(0, 0, 0, 0)
#        self._sets_details = ViewSetsDetails(self._sesson_gui, self)
#        self._scroll_area.setWidget(self._sets_details)
#
#        self._layout.addWidget(self._scroll_area, 0, 1, 1, 3)
#        self.refresh()
#        self.resizeEvent(QtCore.QEvent)
#
#    def resizeEvent(self, e):
#        """ * """
#        main_window_width = self._sesson_gui.main_window.width()
#        main_window_height = self._sesson_gui.main_window.height()
#        # ADJUST LAYOUT
#        # view_sets_sets_list
#        target_width = None
#        weight = 0.2
#        if main_window_width < 100 / weight:
#            target_width = 100
#        elif main_window_width > 270 / weight:
#            target_width = 270
#        else:
#            target_width = int(main_window_width * weight)
#        self._layout.setColumnMinimumWidth(0, target_width)
#        self._layout.setColumnStretch(0, 1)
#        self._layout.setColumnStretch(1, 99)
#        # view_sets_details
#        self._sets_details.refresh_geo()
#
#    def refresh(self):
#        """ * """
#        # list
#        self._sets_list.refresh()
#
#
#class ViewSetsSetsList2(QtGui.QFrame):
#    def __init__(self):
#        super(ViewSetsSetsList2, self).__init__()
#
#        self._init_ui()
#
#    def _init_ui(self):
#        pass
#
#
#class ViewSetsSetsList(QtGui.QListWidget):
#    """ * """
#    _session_gui = None
#    _view_sets = None
#
#    _context_menu = None
#
#    def __init__(self, session_gui, view_sets):
#        super(ViewSetsSetsList, self).__init__()
#
#        self._session_gui = session_gui
#        self._view_sets = view_sets
#
#        self._init_ui()
#        self.setFocus()
#
#    def _init_ui(self):
#        """ * """
#        self.itemChanged.connect(self.rename_item)
#        self.setSortingEnabled(True)
#
#    def rename_item(self, item):
#        """ *
#        Fires when item in list view has been changed (e.g. renamed).
#        """
#        # VALIDATE DATA
#        if not re.match(bs.config.REGEX_PATTERN_NAME, item.text()):
#            dialog = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
#                                       "Invalid Name",
#                                       bs.messages.general.PATTERN_NAME_INVALID()[0])
#            dialog.setDetailedText(bs.messages.general.PATTERN_NAME_INVALID()[1])
#            dialog.exec_()
#            self.refresh()
#            return False
#        # RENAME OBJECT
#        item.backup_set.set_name = item.text()
#        return True
#
#    def keyReleaseEvent(self, e):
#        if e.key() == QtCore.Qt.Key_Up or\
#            e.key() == QtCore.Qt.Key_Down:
#            current_item = self.currentItem()
#            self._view_sets.sets_details.refresh(current_item)
#        super(ViewSetsSetsList, self).keyReleaseEvent(e)
#
#    def mousePressEvent(self, e):
#        """ * """
#        item_clicked = self.itemAt(e.x(), e.y())
#        self.setCurrentItem(item_clicked)
#        if item_clicked:
#            # right-click
#            if e.button() & QtCore.Qt.RightButton:
#                # show context menu
#                item_clicked.context_menu.popup(e.globalPos())
#                self._view_sets.sets_details.refresh(item_clicked)
#            # left-click
#            else:
#                self._view_sets.sets_details.refresh(item_clicked)
#        else:
#            self._view_sets.sets_details.refresh(None)
#        super(ViewSetsSetsList, self).mousePressEvent(e)
#
#    def refresh(self):
#        """ * """
#        self.clear()
#        for backup_set in self._session_gui.session.backup_sets.sets:
#            self.addItem(ViewSetsSetsListItem(self._session_gui,
#                                              backup_set,
#                                              self,
#                                              self._view_sets.sets_details))
#        self.setFocus()
#
#
#class ViewSetsSetsListItem(QtGui.QListWidgetItem):
#    """ * """
#    _session_gui = None
#    _backup_set = None
#    _list_widget = None
#    _view_sets_details = None
#
#    _context_menu = None
#
#    def __init__(self, session_gui, backup_set, list_widget, view_sets_details):
#        super(ViewSetsSetsListItem, self).__init__()
#
#        self._session_gui = session_gui
#        self._backup_set = backup_set
#        self._list_widget = list_widget
#        self._view_sets_details = view_sets_details
#
#        self._init_ui()
#
#    def _init_ui(self):
#        """ * """
#        self.setText(self._backup_set.set_name)
#        self.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
#        # context menu
#        self._context_menu = ViewSetsSetsListItemCMenu(self._session_gui,
#                                                       self._view_sets_details,
#                                                       self._list_widget,
#                                                       self)
#
#    @property
#    def backup_set(self):
#        """ * """
#        return self._backup_set
#
#    @property
#    def context_menu(self):
#        return self._context_menu
#
#
#class ViewSetsSetsListItemCMenu(QtGui.QMenu):
#    """ * """
#    _session_gui = None
#    _view_sets_details = None
#    _list_widget = None
#    _list_widget_item = None  # This is the QListWidgetItem that the menu was opened upon
#
#    _action_del = None
#
#    def __init__(self, session_gui, view_sets_details, list_widget, list_widget_item):
#        """ * """
#        super(ViewSetsSetsListItemCMenu, self).__init__()
#
#        self._session_gui = session_gui
#        self._view_sets_details = view_sets_details
#        self._list_widget = list_widget
#        self._list_widget_item = list_widget_item
#
#        self._init_ui()
#
#    def _init_ui(self):
#        self._action_del = QtGui.QAction("Delete", self)
#        self._action_del.triggered.connect(self.action_del)
#        self.addAction(self._action_del)
#
#    def action_del(self):
#        """ *
#        Executed when action `action_del` is triggered.
#        """
#        confirm_msg_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
#                                   "Confirm Deletion",
#                                   "Are you sure you want to delete the "\
#                                   "following backup-set?\n\n"\
#                                   "%s" % (self._list_widget_item.backup_set.set_name, ))
#        dialog_btn_cancel = confirm_msg_box.addButton(QtGui.QMessageBox.Cancel)
#        dialog_btn_ok = confirm_msg_box.addButton(QtGui.QMessageBox.Ok)
#        confirm_msg_box.exec_()
#        # if OK was pressed, delete set
#        if confirm_msg_box.clickedButton() is dialog_btn_ok:
#            set_id = self._list_widget_item.backup_set.set_id
#            self._session_gui.session.backup_sets.delete_backup_set(set_id)
#        # refresh list
#        self._list_widget.refresh()
#        # refresh details
#        self._view_sets_details.refresh()
#
#
#class ViewSetsDetails(QtGui.QWidget):
#    """ * """
#    _session_gui = None
#    _view_sets = None
#
#    _backup_set = None
#    _list_widget_item = None
#    _sources_widget = None
#    _filters_widget = None
#    _arrows_1 = None
#    _arrows_2 = None
#
#    def __init__(self, sesson_gui, view_sets):
#        super(ViewSetsDetails, self).__init__()
#
#        self._session_gui = sesson_gui
#        self._view_sets = view_sets
#
#        self._init_ui()
#
#    @property
#    def backup_set(self):
#        self._backup_set = self._view_sets.sets_list.currentItem().backup_set
#        return self._backup_set
#
#    @property
#    def sources_widget(self):
#        return self._sources_widget
#
#    @property
#    def list_widget_item(self):
#        return self._list_widget_item
#
#    def _init_ui(self):
#        pass
#
#    def refresh(self, list_widget_item=None):
#        """ * """
#        # get active QListWidgetItem
#        self._list_widget_item = list_widget_item
#        # rebuild widgets
#        try:
#            self._sources_widget.deleteLater()
#            self._filters_widget.deleteLater()
#            self._targets_widget.deleteLater()
#            self._arrows_1.deleteLater()
#            self._arrows_2.deleteLater()
#        except:
#            pass
#        if self._list_widget_item:
#            self._sources_widget = ViewSetsDetailsSources(self,
#                                                          self._session_gui,
#                                                          self._view_sets,
#                                                          self._list_widget_item,
#                                                          self.backup_set,
#                                                          "Sources")
#            self._filters_widget = ViewSetsDetailsFilters(self,
#                                                          self._session_gui,
#                                                          self._view_sets,
#                                                          self._list_widget_item,
#                                                          self._backup_set,
#                                                          "Filters")
#            self._targets_widget = ViewSetsDetailsTargets(self,
#                                                          self._session_gui,
#                                                          self._view_sets,
#                                                          self._list_widget_item,
#                                                          self._backup_set,
#                                                          "Targets")
#            self._arrows_1 = ViewSetsDetailsArrow_1(self,
#                                                    self._backup_set)
#            self._arrows_2 = ViewSetsDetailsArrow_2(self,
#                                                    self._backup_set)
#            # update composition
#            self.refresh_geo()
#        self.update()
#
#    def refresh_geo(self):
#        """ *
#        Refresh this widget's geo. This is necessary for the embedding scroll
#        widget to know how big it actually wants to be. Would be 0x0px
#        otherwise.
#        """
#        try:
#            # CENTER VERTICALLY
#            # self._sources_widget
#            self._sources_widget.setGeometry(5,
#                                             self._view_sets.height() / 2 - self._sources_widget.height() / 2,
#                                             self._sources_widget.width(),
#                                             self._sources_widget.height())
#            # self._filters_widget
#            self._filters_widget.setGeometry(self._view_sets.scroll_area.width() / 2 - self._filters_widget.width() / 2,
#                                             self._view_sets.height() / 2 - self._filters_widget.height() / 2,
#                                             self._filters_widget.width(),
#                                             self._filters_widget.height())
#            # self._targets_widget
#            self._targets_widget.setGeometry(self._view_sets.scroll_area.width() - self._targets_widget.width() - 7,
#                                             self._view_sets.height() / 2 - self._targets_widget.height() / 2,
#                                             self._targets_widget.width(),
#                                             self._targets_widget.height())
#            # self._arrows_1
#            source_widget_first = self._sources_widget._nested_widgets[0]
#            source_widget_last = self._sources_widget._nested_widgets[-1]
#            top_left = self._sources_widget.mapTo(self, source_widget_first.pos())
#            top_left.setX(top_left.x() + source_widget_first.width() + 10)
#            bottom_right = self._sources_widget.mapTo(self, source_widget_last.pos())
#            bottom_right.setX(self._filters_widget.x() - 5)
#            bottom_right.setY(self._sources_widget.mapTo(self, source_widget_last.pos()).y() + source_widget_last.height())
#            rect = QtCore.QRect(top_left, bottom_right)
#            self._arrows_1.setGeometry(rect)
#            # self._arrows_2
#            target_widget_first = self._targets_widget._nested_widgets[0]
#            target_widget_last = self._targets_widget._nested_widgets[-1]
#            top_left = self._targets_widget.mapTo(self, target_widget_first.pos())
#            top_left.setX(self._filters_widget.x() + self._filters_widget.width() + 5)
#            bottom_right = self.mapToParent(self._targets_widget.mapTo(self, target_widget_last.pos()))
#            bottom_right.setX(bottom_right.x() - 10)
#            bottom_right.setY(bottom_right.y() + target_widget_last.height())
#            rect = QtCore.QRect(top_left, bottom_right)
#            self._arrows_2.setGeometry(rect)
#            # get max width and height
#            min_width = 0
#            min_height = 0
#            for item in [self._sources_widget,
#                         self._filters_widget,
#                         self._targets_widget,
#                         self._arrows_1,
#                         self._arrows_2]:
#                x_max = item.x() + item.width()
#                y_max = item.y() + item.height()
#                if x_max > min_width:
#                    min_width = x_max
#                if y_max > min_height:
#                    min_height = y_max
#            self.setGeometry(self.x(),
#                             self.y(),
#                             min_width,
#                             min_height)
#        except:
#            pass
#
#
#class ViewSetsDetailsContainer(QtGui.QFrame):
#    """ * """
#    _view_sets_details = None
#    _session_gui = None
#    _view_sets = None
#    _list_widget_item = None
#    _backup_set = None
#    _title = None
#
#    _layout = None
#    _title_widget = None
#    _nested_widgets = None
#    _x_default = None
#    _width_default = 120
#    _width_relaxed = None  # This records the relaxed width after shown and lain out
#
#    def __init__(self,
#                 view_sets_details,
#                 session_gui,
#                 view_sets,
#                 list_widget_item,
#                 backup_set,
#                 title):
#        super(ViewSetsDetailsContainer, self).__init__(view_sets_details)
#
#        self._view_sets_details = view_sets_details
#        self._session_gui = session_gui
#        self._view_sets = view_sets
#        self._list_widget_item = list_widget_item
#        self._backup_set = backup_set
#        self._title = title
#
#        self._nested_widgets = []
#
#        self._init_ui()
#
#    @property
#    def list_widget_item(self):
#        return self._list_widget_item
#
#    def _init_ui(self):
#        """ * """
#        # drop-shadow
#        gfx = QtGui.QGraphicsDropShadowEffect(self)
#        gfx.setOffset(0)
#        gfx.setBlurRadius(4)
#        self.setGraphicsEffect(gfx)
#        # CSS
#        self.setStyleSheet(".%s {background: #c7c7ff; border-radius: 2px;} .%s:hover {}"
#                           % (self.__class__.__name__,
#                              self.__class__.__name__))
#        self._layout = QtGui.QGridLayout(self)
#        self._layout.setContentsMargins(5, 5, 5, 5)
#        self._layout.setSpacing(5)
#        self._layout.setRowMinimumHeight(0, 13)
#        self._layout.setRowStretch(0, 1)
#        # title
#        self._title_widget = QtGui.QLabel(self._title)
#        self._title_widget.setStyleSheet("margin-left: 1px; font-weight: bold")
#        self._layout.addWidget(self._title_widget, 0, 0, 1, 1)
#        # ADD SOURCE WIDGETS
#        self.populate()
#        self.show()
#        self._width_relaxed = self.width()
#        self.setGeometry(self.x(), self.y(), self._width_default, self.height())
#
#    def enterEvent(self, e):
#        # transpose widget
#        if self.width() < self._width_relaxed:
#            self._x_default = self.x()
#            # determin where it sits on its parent
#            pos_x_f = (self.x() - 5) / (self._view_sets_details.width() - self._width_default - 5)
#            self.raise_()
#            x = int(self._x_default - (self._width_relaxed - self._width_default) * pos_x_f)
#            self.setGeometry(x, self.y(), self._width_relaxed, self.height())
##        collider = Collider(self)
#
#    def leaveEvent(self, e):
#        self.setGeometry(self._x_default, self.y(), self._width_default, self.height())
#
#    def populate(self):
#        """ *
#        This method populates the widget with sub-widgets.
#        It is meant to be overridden in subclasses.
#        """
#
#
#class ViewSetsDetailsSources(ViewSetsDetailsContainer):
#    """ * """
#    def __init__(self, view_sets_details, session_gui, view_sets, list_widget_item, backup_set, title):
#        super(ViewSetsDetailsSources, self).__init__(view_sets_details, session_gui, view_sets, list_widget_item, backup_set, title)
#
#    def populate(self):
#        """ *
#        Overloaded from superclass.
#        """
#        i = 0
#        for backup_source in self._list_widget_item.backup_set.sources:
#            widget = ViewSetsDetailsSource(self,
#                                           backup_source,
#                                           self._backup_set,
#                                           self._view_sets
#                                           )
#            self._nested_widgets.append(widget)
#            self._layout.setRowMinimumHeight(i + 1, widget.height())
#            self._layout.setRowStretch(i + 1, 1)
#            self._layout.addWidget(widget, i + 1, 0, 1, 1)
#            i += 1
#        # resize
#        last_widget = QtGui.QFrame()
#        last_widget.setMinimumHeight(15)
#        self._layout.addWidget(last_widget, i + 1, 0, 1, 1)
#        self._layout.setRowStretch(i + 1, 100)
#        new_height = self._layout.contentsMargins().top() + self._layout.contentsMargins().bottom()
#        new_height += self._layout.spacing() * (i + 1)
#        new_height += self._layout.rowMinimumHeight(0) * 2
#        new_height += (widget.height() + 2) * i
#        self.setMinimumHeight(new_height)
#
#    def remove_backup_source(self, backup_source):
#        """ *
#        Removes the backup_source from the backup-set.
#        """
#        msg_detailed = "Are you sure you want to <b>remove</b> the following <i>backup-source</i> from this <i>backup-set</i>?"
#        msg_detailed += "<ul><li> &nbsp; %s</li>" % (self._backup_set.set_name, )
#        msg_detailed += "<ul>"
#        for item in self._backup_set.sources:
#            if backup_source == item:
#                msg_detailed += "<li> &nbsp; <span style='text-decoration: line-through; font-weight: bold'>%s</span></li>"\
#                                % (item.source_name, )
#            else:
#                msg_detailed += "<li> &nbsp; %s</li>" % (item.source_name, )
#        msg_detailed += "</ul>"
#        msg_detailed += "</ul>"
#        msg_detailed += "<br />"
#        msg_detailed += "This <i>source</i> itself will not be deleted."
#        confirm_msg_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
#                                            "Confirm Removal",
#                                            msg_detailed)
#        dialog_btn_cancel = confirm_msg_box.addButton(QtGui.QMessageBox.Cancel)
#        dialog_btn_ok = confirm_msg_box.addButton(QtGui.QMessageBox.Ok)
#        print(type(dialog_btn_ok))
#        confirm_msg_box.exec_()
#        # if OK was pressed, remove source
#        if confirm_msg_box.clickedButton() is dialog_btn_ok:
#            self._backup_set.remove_backup_source(backup_source)
#            # refresh list
#            self._view_sets.sets_details.refresh(self._list_widget_item)
#
#
#class ViewSetsDetailsSource(QtGui.QFrame):
#    """ * """
#    _backup_set = None
#    _backup_source = None
#    _view_sets_details_sources = None
#    _view_sets = None
#    _list_widget = None
#
#    _layout = None
#    _context_menu = None
#
#    def __init__(self, view_sets_details_sources, backup_source, backup_set, view_sets):
#        super(ViewSetsDetailsSource, self).__init__(view_sets_details_sources)
#
#        self._backup_set = backup_set
#        self._backup_source = backup_source
#        self._view_sets_details_sources = view_sets_details_sources
#        self._view_sets = view_sets
#
#        self._list_widget = view_sets.sets_list
#        self._init_ui()
#
#    @property
#    def context_menu(self):
#        return self._context_menu
#
#    def _init_ui(self):
#        """ * """
#        self._layout = QtGui.QGridLayout(self)
#
#        # title
#        backup_source_name = self._backup_source.source_name
#        title_widget = QtGui.QLabel(backup_source_name, self)
#        title_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
#        self._layout.addWidget(title_widget, 0, 0, 1, 1)
#
#        # del button
#
#
#        # path
#        backup_source_path = self._backup_source.source_path
#        path_widget = QtGui.QLabel(backup_source_path, self)
#        path_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
#        path_widget.setStyleSheet(".QLabel {border: 0px; color: #808080}")
#        self._layout.addWidget(path_widget, 1, 0, 1, 1)
#
#        self.setStyleSheet(".ViewSetsDetailsSource {background: #f0f0f0; border: 1px solid #FFFFFF; border-radius: 2px} .ViewSetsDetailsSource:hover {background: #FFFFFF}")
#        # context menu
#        self._context_menu = ViewSetsDetailsSourceCMenu(self)
#        # set geo
#        self.setMinimumHeight(52)
#
#    def remove(self):
#        """ *
#        Removes this backup-source from the associated backup-set.
#        """
#        self._view_sets_details_sources.remove_backup_source(self._backup_source)
#
#    def mousePressEvent(self, e):
#        """ * """
#        if e.button() & QtCore.Qt.RightButton:
#            # show context menu
#            self.context_menu.popup(e.globalPos())
#        super(ViewSetsDetailsSource, self).mousePressEvent(e)
#
#
#class ViewSetsDetailsSourceCMenu(QtGui.QMenu):
#    """ * """
#    _view_sets_details_source = None
#
#    _action_rem = None
#
#    def __init__(self, view_sets_details_source):
#        super(ViewSetsDetailsSourceCMenu, self).__init__(view_sets_details_source)
#
#        self._view_sets_details_source = view_sets_details_source
#
#        self._init_ui()
#
#    def _init_ui(self):
#        """ * """
#        self._action_rem = QtGui.QAction("Remove", self)
#        self._action_rem.triggered.connect(self._view_sets_details_source.remove)
#        self.addAction(self._action_rem)
#
#
#class ViewSetsDetailsFilters(ViewSetsDetailsContainer):
#    """ * """
#    def __init__(self, view_sets_details,
#                 session_gui,
#                 view_sets,
#                 list_widget_item,
#                 backup_set,
#                 title):
#        super(ViewSetsDetailsFilters, self).__init__(view_sets_details,
#                                                     session_gui,
#                                                     view_sets,
#                                                     list_widget_item,
#                                                     backup_set,
#                                                     title)
#
#    def populate(self):
#        """ *
#        Override from superclass.
#        """
#        # ADD FILTER WIDGETS
#        i = 0
#        for backup_filter in self._list_widget_item.backup_set.filters:
#            widget = ViewSetsDetailsFilter(self,
#                                           backup_filter)
#            self._nested_widgets.append(widget)
#            self._layout.setRowMinimumHeight(i + 1, widget.height())
#            self._layout.setRowStretch(i + 1, 1)
#            self._layout.addWidget(widget, i + 1, 0, 1, 1)
#            i += 1
#
#        # resize
#        last_widget = QtGui.QFrame()
#        last_widget.setMinimumHeight(15)
#        self._layout.addWidget(last_widget, i + 1, 0, 1, 1)
#        self._layout.setRowStretch(i + 1, 100)
#        new_height = self._layout.contentsMargins().top() + self._layout.contentsMargins().bottom()
#        new_height += self._layout.spacing() * (i + 1)
#        new_height += self._layout.rowMinimumHeight(0) * 2
#        new_height += (widget.height() + 2) * i
#        self.setMinimumHeight(new_height)
#
#
#class ViewSetsDetailsFilter(QtGui.QFrame):
#    """ * """
#    _view_sets_details_filters = None
#    _backup_filter = None
#
#    _layout = None
#
#    def __init__(self, view_sets_details_filters, backup_filter):
#        super(ViewSetsDetailsFilter, self).__init__(view_sets_details_filters)
#
#        self._view_sets_details_filters = view_sets_details_filters
#        self._backup_filter = backup_filter
#
#        self._init_ui()
#
#    def _init_ui(self):
#        """ * """
#        self._layout = QtGui.QGridLayout(self)
#
#        # title
#        backup_filter_name = self._backup_filter.filter_pattern
#        title_widget = QtGui.QLabel(backup_filter_name, self)
#        title_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
#        self._layout.addWidget(title_widget, 0, 0, 1, 1)
#
#        self.setStyleSheet(".ViewSetsDetailsFilter {background: #f0f0f0; border: 1px solid #FFFFFF; border-radius: 2px} .ViewSetsDetailsFilter:hover {background: #FFFFFF}")
#        self.setMinimumHeight(52)
#
#
#class ViewSetsDetailsTargets(ViewSetsDetailsContainer):
#    """ *
#    """
#    def __init__(self,
#                 view_sets_details,
#                 session_gui,
#                 view_sets,
#                 list_widget_item,
#                 backup_set,
#                 title):
#        super(ViewSetsDetailsTargets, self).__init__(view_sets_details,
#                                                     session_gui,
#                                                     view_sets,
#                                                     list_widget_item,
#                                                     backup_set,
#                                                     title)
#
#    def populate(self):
#        """ *
#        Override from superclass.
#        """
#        # ADD TARGET WIDGETS
#        i = 0
#        for backup_target in self._list_widget_item.backup_set.targets:
#            widget = ViewSetsDetailsTarget(self,
#                                           backup_target)
#            self._nested_widgets.append(widget)
#            self._layout.setRowMinimumHeight(i + 1, widget.height())
#            self._layout.setRowStretch(i + 1, 1)
#            self._layout.addWidget(widget, i + 1, 0, 1, 1)
#            i += 1
#
#        # resize
#        last_widget = QtGui.QFrame()
#        last_widget.setMinimumHeight(15)
#        self._layout.addWidget(last_widget, i + 1, 0, 1, 1)
#        self._layout.setRowStretch(i + 1, 100)
#        new_height = self._layout.contentsMargins().top() + self._layout.contentsMargins().bottom()
#        new_height += self._layout.spacing() * (i + 1)
#        new_height += self._layout.rowMinimumHeight(0) * 2
#        new_height += (widget.height() + 2) * i
#        self.setMinimumHeight(new_height)
#
#
#class ViewSetsDetailsTarget(QtGui.QFrame):
#    """ * """
#    _view_sets_details_targets = None
#    _backup_target = None
#
#    _layout = None
#
#    def __init__(self, view_sets_details_targets, backup_target):
#        super(ViewSetsDetailsTarget, self).__init__(view_sets_details_targets)
#
#        self._view_sets_details_targets = view_sets_details_targets
#        self._backup_target = backup_target
#
#        self._init_ui()
#
#    def _init_ui(self):
#        """ * """
#        self._layout = QtGui.QGridLayout(self)
#
#        # title
#        backup_target_name = self._backup_target.target_name
#        title_widget = QtGui.QLabel(backup_target_name, self)
#        title_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
#        self._layout.addWidget(title_widget, 0, 0, 1, 1)
#
#        self.setStyleSheet(".ViewSetsDetailsTarget {background: #f0f0f0; border: 1px solid #FFFFFF; border-radius: 2px} .ViewSetsDetailsTarget:hover {background: #FFFFFF}")
#        self.setMinimumHeight(52)
#
#
#class ViewSetsDetailsArrow(QtGui.QWidget):
#    """ * """
#    _view_sets_details = None
#    _backup_set = None
#
#    _stroke_width = None
#    _render_mode = None
#    _n = None
#
#    def __init__(self,
#                 view_sets_details,
#                 backup_set):
#        super(ViewSetsDetailsArrow, self).__init__(view_sets_details)
#
#        self._view_sets_details = view_sets_details
#        self._backup_set = backup_set
#
#        self._stroke_width = 3
#        self._render_mode = "m_s"
#        self._n = 1
#
#        self._init_ui()
#
#    def _init_ui(self):
#        """ * """
#        self.show()
#
#    def paintEvent(self, e=None):
#        """ * """
#        path = QtGui.QPainterPath()
#        for i in range(self._n):
#            x_1 = self._stroke_width
#            x_2 = self.width() / 2
#            x_3 = self.width() - self._stroke_width
#            y_1 = self.height() / 2
#            try:
#                y_2 = (2 * self.height() * i + self.height()) / (2 * self._n)
#            except:
#                y_2 = y_1
#
#            if self._render_mode == "m_s":
#                path.moveTo(x_1, y_2)
#                path.cubicTo(x_2, y_2,
#                             x_2, y_1,
#                             x_3, y_1)
#                path = self._draw_arrow_head(path, x_3, y_1)
#            elif self._render_mode == "s_m":
#                path.moveTo(x_1, y_1)
#                path.cubicTo(x_2, y_1,
#                             x_2, y_2,
#                             x_3, y_2)
#                path = self._draw_arrow_head(path, x_3, y_2)
#
#        painter = QtGui.QPainter(self)
#        painter.setRenderHints(QtGui.QPainter.Antialiasing)
#        pen = QtGui.QPen(QtGui.QColor(199, 199, 255),
#                                      self._stroke_width,
#                                      QtCore.Qt.SolidLine,
#                                      QtCore.Qt.RoundCap,
#                                      QtCore.Qt.MiterJoin)
#        painter.setPen(pen)
#        painter.drawPath(path)
#        super(ViewSetsDetailsArrow, self).paintEvent(e)
#
#    def _draw_arrow_head(self, path, current_x, current_y):
#        wing_length = 5
#        path.moveTo(current_x - 1, current_y - 1)
#        path.lineTo(current_x - wing_length, current_y - wing_length)
#        path.moveTo(current_x - 1, current_y + 1)
#        path.lineTo(current_x - wing_length, current_y + wing_length)
#        return path
#
#
#class ViewSetsDetailsArrow_1(ViewSetsDetailsArrow):
#    """ * """
#
#    def __init__(self,
#                 view_sets_details,
#                 backup_set):
#        super(ViewSetsDetailsArrow_1, self).__init__(view_sets_details,
#                                                     backup_set)
#
#        self._render_mode = "m_s"
#        self._n = len(self._backup_set.sources)
#
#
#class ViewSetsDetailsArrow_2(ViewSetsDetailsArrow):
#    """ * """
#
#    def __init__(self,
#                 view_sets_details,
#                 backup_set):
#        super(ViewSetsDetailsArrow_2, self).__init__(view_sets_details,
#                                                     backup_set)
#
#        self._render_mode = "s_m"
#        self._n = len(self._backup_set.targets)
