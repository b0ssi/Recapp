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
    _scroll_area = None

    def __init__(self, session_gui):
        super(ViewSets, self).__init__()

        self._sesson_gui = session_gui

        self._init_ui()

    @property
    def sets_list(self):
        return self._sets_list

    @property
    def sets_details(self):
        return self._sets_details

    @property
    def scroll_area(self):
        return self._scroll_area

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
        self._scroll_area = QtGui.QScrollArea(self)
        self._scroll_area.setContentsMargins(0, 0, 0, 0)
        self._sets_details = ViewSetsDetails(self._sesson_gui, self)
        self._scroll_area.setWidget(self._sets_details)

        self._layout.addWidget(self._scroll_area, 0, 1, 1, 3)
        self.refresh()
        self.resizeEvent(QtCore.QEvent)

    def resizeEvent(self, e):
        """ * """
        main_window_width = self._sesson_gui.main_window.width()
        main_window_height = self._sesson_gui.main_window.height()
        # ADJUST LAYOUT
        # view_sets_sets_list
        target_width = None
        weight = 0.2
        if main_window_width < 100 / weight:
            target_width = 100
        elif main_window_width > 270 / weight:
            target_width = 270
        else:
            target_width = int(main_window_width * weight)
        self._layout.setColumnMinimumWidth(0, target_width)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 99)
        # view_sets_details
        self._sets_details.refresh_geo()

    def refresh(self):
        """ * """
        # list
        self._sets_list.refresh()


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
        self.setFocus()

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

    def keyReleaseEvent(self, e):
        if e.key() == QtCore.Qt.Key_Up or\
            e.key() == QtCore.Qt.Key_Down:
            current_item = self.currentItem()
            self._view_sets.sets_details.refresh(current_item)
        super(ViewSetsSetsList, self).keyReleaseEvent(e)

    def mousePressEvent(self, e):
        """ * """
        item_clicked = self.itemAt(e.x(), e.y())
        self.setCurrentItem(item_clicked)
        if item_clicked:
            # right-click
            if e.button() & QtCore.Qt.RightButton:
                # show context menu
                item_clicked.context_menu.popup(e.globalPos())
                self._view_sets.sets_details.refresh(item_clicked)
            # left-click
            else:
                self._view_sets.sets_details.refresh(item_clicked)
        else:
            self._view_sets.sets_details.refresh(None)
        super(ViewSetsSetsList, self).mousePressEvent(e)

    def refresh(self):
        """ * """
        self.clear()
        for backup_set in self._session_gui.session.backup_sets.sets:
            self.addItem(ViewSetsSetsListItem(self._session_gui,
                                              backup_set,
                                              self,
                                              self._view_sets.sets_details))
        self.setFocus()


class ViewSetsSetsListItem(QtGui.QListWidgetItem):
    """ * """
    _session_gui = None
    _backup_set = None
    _list_widget = None
    _view_sets_details = None

    _context_menu = None

    def __init__(self, session_gui, backup_set, list_widget, view_sets_details):
        super(ViewSetsSetsListItem, self).__init__()

        self._session_gui = session_gui
        self._backup_set = backup_set
        self._list_widget = list_widget
        self._view_sets_details = view_sets_details

        self._init_ui()

    def _init_ui(self):
        """ * """
        self.setText(self._backup_set.set_name)
        self.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        # context menu
        self._context_menu = ViewSetsSetsListItemCMenu(self._session_gui,
                                                       self._view_sets_details,
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
    _view_sets_details = None
    _list_widget = None
    _list_widget_item = None  # This is the QListWidgetItem that the menu was opened upon

    _action_del = None

    def __init__(self, session_gui, view_sets_details, list_widget, list_widget_item):
        """ * """
        super(ViewSetsSetsListItemCMenu, self).__init__()

        self._session_gui = session_gui
        self._view_sets_details = view_sets_details
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
            self._session_gui.session.backup_sets.delete_backup_set(set_id)
        # refresh list
        self._list_widget.refresh()
        # refresh details
        self._view_sets_details.refresh()


class ViewSetsDetails(QtGui.QWidget):
    """ * """
    _session_gui = None
    _view_sets = None

    _backup_set = None
    _list_widget_item = None
    _sources_widget = None
    _filters_widget = None
    _arrows_1 = None

    def __init__(self, sesson_gui, view_sets):
        super(ViewSetsDetails, self).__init__()

        self._session_gui = sesson_gui
        self._view_sets = view_sets

        self._init_ui()

    @property
    def backup_set(self):
        self._backup_set = self._view_sets.sets_list.currentItem().backup_set
        return self._backup_set

    @property
    def sources_widget(self):
        return self._sources_widget

    @property
    def list_widget_item(self):
        return self._list_widget_item

    def _init_ui(self):
        """ * """

    def refresh(self, list_widget_item=None):
        """ * """
        # get active QListWidgetItem
        self._list_widget_item = list_widget_item
        # rebuild widgets
        try:
            self._sources_widget.deleteLater()
            self._arrows_1.deleteLater()
            self._filters_widget.deleteLater()
        except:
            pass
        if self._list_widget_item:
            self._sources_widget = ViewSetsDetailsSources(self,
                                                          self._session_gui,
                                                          self._view_sets,
                                                          self._list_widget_item,
                                                          self.backup_set)
            self._filters_widget = ViewSetsDetailsFilters(self,
                                                          self._list_widget_item)
            self._arrows_1 = ViewSetsDetailsArrow(self,
                                                  self._sources_widget,
                                                  self._filters_widget,
                                                  self._backup_set)
            self._sources_widget.show()
            self._filters_widget.show()
            self._arrows_1.show()
            # update composition
            self.refresh_geo()

    def refresh_geo(self):
        """ *
        Refresh this widget's geo. This is necessary for the embedding scroll
        widget to know how big it actually wants to be. Would be 0x0px
        otherwise.
        """
        if self._sources_widget:
            # CENTER VERTICALLY
            # self._sources_widget
            self._sources_widget.setGeometry(5,
                                             self._view_sets.height() / 2 - self._sources_widget.height() / 2,
                                             self._sources_widget.width(),
                                             self._sources_widget.height())
#            self._arrows_1.setGeometry(self._sources_widget.x() + self._sources_widget.width() + 5,
#                                       self._view_sets.height() / 2 - self._arrows_1.height() / 2,
#                                       self._arrows_1.width(),
#                                       self._arrows_1.height())
            # self._filters_widget
            self._filters_widget.setGeometry(self._view_sets.scroll_area.width() - self._filters_widget.width() - 7,
                                             self._view_sets.height() / 2 - self._filters_widget.height() / 2,
                                             self._filters_widget.width(),
                                             self._filters_widget.height())
            # self._arrows_1
            source_widget = self._sources_widget._view_sets_details_source_widgets[0]  #._view_sets_details_source_widgets[0]
            top_left = self._sources_widget.mapTo(self, source_widget.pos())
            top_left.setX(top_left.x() + source_widget.width() + 10)
            top_left.setY(top_left.y() + source_widget.height() / 2)
            bottom_right = self.mapToParent(self._filters_widget.pos())
            bottom_right.setX(bottom_right.x() - 5)
            bottom_right.setY(top_left.y() + ((bottom_right.y() + (self._filters_widget.height() / 2)) - top_left.y()) * 2)
            rect = QtCore.QRect(top_left, bottom_right)
            self._arrows_1.setGeometry(rect)
#            self._arrows_1.refresh_geo()
            # get max width and height
            min_width = 0
            min_height = 0
            for item in [self._sources_widget,
                         self._arrows_1,
                         self._filters_widget]:
                x_max = item.x() + item.width()
                y_max = item.y() + item.height()
                if x_max > min_width:
                    min_width = x_max
                if y_max > min_height:
                    min_height = y_max
            self.setGeometry(self.x(),
                             self.y(),
                             min_width,
                             min_height)


class ViewSetsDetailsSources(QtGui.QFrame):
    """ * """
    _view_sets_details = None
    _session_gui = None
    _view_sets = None
    _list_widget_item = None
    _backup_set = None

    _layout = None
    _title = None
    _view_sets_details_source_widgets = None

    def __init__(self, view_sets_details, session_gui, view_sets, list_widget_item, backup_set):
        super(ViewSetsDetailsSources, self).__init__(view_sets_details)

        self._view_sets_details = view_sets_details
        self._session_gui = session_gui
        self._view_sets = view_sets
        self._list_widget_item = list_widget_item
        self._backup_set = backup_set

        self._view_sets_details_source_widgets = []

        self._init_ui()

    @property
    def list_widget_item(self):
        return self._list_widget_item

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
        for backup_source in self._list_widget_item.backup_set.sources:
            widget = ViewSetsDetailsSource(self,
                                           backup_source,
                                           self._backup_set,
                                           self._view_sets
                                           )
            self._view_sets_details_source_widgets.append(widget)
            self._layout.setRowMinimumHeight(i + 1, widget.height())
            self._layout.setRowStretch(i + 1, 1)
            self._layout.addWidget(widget, i + 1, 0, 1, 1)
            i += 1
        # resize
        last_widget = QtGui.QFrame()
        last_widget.setMinimumHeight(15)
        self._layout.addWidget(last_widget, i + 1, 0, 1, 1)
        self._layout.setRowStretch(i + 1, 100)
        new_height = self._layout.contentsMargins().top() + self._layout.contentsMargins().bottom()
        new_height += self._layout.spacing() * (i + 1)
        new_height += self._layout.rowMinimumHeight(0) * 2
        new_height += (widget.height() + 2) * i
        self.setMinimumHeight(new_height)

    def remove_backup_source(self, backup_source):
        """ *
        Removes the backup_source from the backup-set.
        """
        msg_detailed = "Are you sure you want to <b>remove</b> the following <i>backup-source</i> from this <i>backup-set</i>?"
        msg_detailed += "<ul><li> &nbsp; %s</li>" % (self._backup_set.set_name, )
        msg_detailed += "<ul>"
        for item in self._backup_set.sources:
            if backup_source == item:
                msg_detailed += "<li> &nbsp; <span style='text-decoration: line-through; font-weight: bold'>%s</span></li>"\
                                % (item.source_name, )
            else:
                msg_detailed += "<li> &nbsp; %s</li>" % (item.source_name, )
        msg_detailed += "</ul>"
        msg_detailed += "</ul>"
        msg_detailed += "<br />"
        msg_detailed += "This <i>source</i> itself will not be deleted."
        confirm_msg_box = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                            "Confirm Removal",
                                            msg_detailed)
        dialog_btn_cancel = confirm_msg_box.addButton(QtGui.QMessageBox.Cancel)
        dialog_btn_ok = confirm_msg_box.addButton(QtGui.QMessageBox.Ok)
        confirm_msg_box.exec_()
        # if OK was pressed, remove source
        if confirm_msg_box.clickedButton() is dialog_btn_ok:
            self._backup_set.remove_backup_source(backup_source)
            # refresh list
            self._view_sets.sets_details.refresh(self._list_widget_item)


class ViewSetsDetailsSource(QtGui.QFrame):
    """ * """
    _backup_set = None
    _backup_source = None
    _view_sets_details_sources = None
    _view_sets = None
    _list_widget = None

    _layout = None
    _context_menu = None

    def __init__(self, view_sets_details_sources, backup_source, backup_set, view_sets):
        super(ViewSetsDetailsSource, self).__init__(view_sets_details_sources)

        self._backup_set = backup_set
        self._backup_source = backup_source
        self._view_sets_details_sources = view_sets_details_sources
        self._view_sets = view_sets

        self._list_widget = view_sets.sets_list
        self._init_ui()

    @property
    def context_menu(self):
        return self._context_menu

    def _init_ui(self):
        """ * """
        self._layout = QtGui.QGridLayout(self)

        # title
        backup_source_name = self._backup_source.source_name
        title_widget = QtGui.QLabel(backup_source_name, self)
        title_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._layout.addWidget(title_widget, 0, 0, 1, 1)

        # del button

        # path
        backup_source_path = self._backup_source.source_path
        path_widget = QtGui.QLabel(backup_source_path, self)
        path_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        path_widget.setStyleSheet(".QLabel {border: 0px; color: #808080}")
        self._layout.addWidget(path_widget, 1, 0, 1, 1)

        self.setStyleSheet(".ViewSetsDetailsSource {background: #f0f0f0; border: 1px solid #FFFFFF; border-radius: 2px} .ViewSetsDetailsSource:hover {background: #FFFFFF}")
        # context menu
        self._context_menu = ViewSetsDetailsSourceCMenu(self)
        self._context_menu.triggered.connect(self.remove)
        # set geo
        self.setMinimumHeight(52)

    def remove(self):
        """ *
        Removes this backup-source from the associated backup-set.
        """
        self._view_sets_details_sources.remove_backup_source(self._backup_source)

    def mousePressEvent(self, e):
        """ * """
        if e.button() & QtCore.Qt.RightButton:
            # show context menu
            self.context_menu.popup(e.globalPos())


class ViewSetsDetailsSourceCMenu(QtGui.QMenu):
    """ * """
    _view_sets_details_source = None

    _action_rem = None

    def __init__(self, view_sets_details_source):
        super(ViewSetsDetailsSourceCMenu, self).__init__("sdf")

        self._view_sets_details_source = view_sets_details_source

        self._init_ui()

    def _init_ui(self):
        """ * """
        self._action_rem = QtGui.QAction("Remove", self)
        self.addAction(self._action_rem)


class ViewSetsDetailsFilters(QtGui.QFrame):
    """ * """
    _view_sets_details = None
    _list_widget_item = None

    _layout = None
    _title = None

    def __init__(self, view_sets_details, list_widget_item):
        super(ViewSetsDetailsFilters, self).__init__(view_sets_details)

        self._view_sets_details = view_sets_details
        self._list_widget_item = list_widget_item

        self._init_ui()

    def _init_ui(self):
        """ * """
        self.setStyleSheet(".ViewSetsDetailsFilters {background: #c7c7ff; border-radius: 2px}")
        self._layout = QtGui.QGridLayout(self)
        self._layout.setContentsMargins(5, 5, 5, 5)
        self._layout.setSpacing(5)
        self._layout.setRowMinimumHeight(0, 13)
        self._layout.setRowStretch(0, 1)
        # title
        self._title = QtGui.QLabel("Filters")
        self._title.setStyleSheet("margin-left: 1px; font-weight: bold")
        self._layout.addWidget(self._title, 0, 0, 1, 1)
        # ADD FILTER WIDGETS
        i = 0
        for backup_filter in self._list_widget_item.backup_set.filters:
            widget = ViewSetsDetailsFilter(self,
                                           backup_filter)
            self._layout.setRowMinimumHeight(i + 1, widget.height())
            self._layout.setRowStretch(i + 1, 1)
            self._layout.addWidget(widget, i + 1, 0, 1, 1)
            i += 1

        # resize
        last_widget = QtGui.QFrame()
        last_widget.setMinimumHeight(15)
        self._layout.addWidget(last_widget, i + 1, 0, 1, 1)
        self._layout.setRowStretch(i + 1, 100)
        new_height = self._layout.contentsMargins().top() + self._layout.contentsMargins().bottom()
        new_height += self._layout.spacing() * (i + 1)
        new_height += self._layout.rowMinimumHeight(0) * 2
        new_height += (widget.height() + 2) * i
        self.setMinimumHeight(new_height)


class ViewSetsDetailsFilter(QtGui.QFrame):
    """ * """
    _view_sets_details_filters = None
    _backup_filter = None

    _layout = None

    def __init__(self, view_sets_details_filters, backup_filter):
        super(ViewSetsDetailsFilter, self).__init__(view_sets_details_filters)

        self._view_sets_details_filters = view_sets_details_filters
        self._backup_filter = backup_filter

        self._init_ui()

    def _init_ui(self):
        """ * """
        self._layout = QtGui.QGridLayout(self)

        # title
        backup_filter_name = self._backup_filter.filter_pattern
        title_widget = QtGui.QLabel(backup_filter_name, self)
        title_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._layout.addWidget(title_widget, 0, 0, 1, 1)

        self.setStyleSheet(".ViewSetsDetailsFilter {background: #f0f0f0; border: 1px solid #FFFFFF; border-radius: 2px} .ViewSetsDetailsFilter:hover {background: #FFFFFF}")
        self.setMinimumHeight(52)


class ViewSetsDetailsArrow(QtGui.QWidget):
    """ * """
    _view_sets_details = None
    _sources_widget = None
    _filters_widget = None
    _backup_set = None

    def __init__(self, view_sets_details, sources_widget, filters_widget, backup_set):
        """ * """

        super(ViewSetsDetailsArrow, self).__init__(view_sets_details)

        self._view_sets_details = view_sets_details
        self._sources_widget = sources_widget
        self._filters_widget = filters_widget
        self._backup_set = backup_set

        self._init_ui()

    def _init_ui(self):
        """ * """

    def paintEvent(self, e=None):
        """ * """
        stroke_width = 3
        path = QtGui.QPainterPath()
        n = len(self._backup_set.sources)
        for i in range(n):
            p_1_x = stroke_width
            try:
                p_1_y = (self.height() - stroke_width * 2) / (n - 1) * i + stroke_width
            except:
                p_1_y = self.height() / 2
            p_2_x = self.width() / 2
            p_2_y = p_1_y
            p_3_x = p_2_x
            p_3_y = self.height() / 2
            p_4_x = self.width() - stroke_width
            p_4_y = p_3_y
            path.moveTo(p_1_x, p_1_y)
            path.cubicTo(p_2_x, p_2_y,
                         p_3_x, p_3_y,
                         p_4_x, p_4_y)
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(199, 199, 255),
                                      stroke_width,
                                      QtCore.Qt.SolidLine,
                                      QtCore.Qt.RoundCap,
                                      QtCore.Qt.MiterJoin)
        painter.setPen(pen)
#        painter.setBrush(QtGui.QColor(122, 163, 39))
        painter.drawPath(path)
#        painter = QtGui.QPainter(self)
#        painter.setPen(QtCore.Qt.blue)
#        painter.setFont(QtGui.QFont("Tahoma", 30))
#        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "Sources")
        super(ViewSetsDetailsArrow, self).paintEvent(e)

    def refresh_geo(self):
        """ *
        Updates the geo according to its context and calls self.paintEvent
        to repaint the graphics.
        """
        source_widget = self._sources_widget._view_sets_details_source_widgets[0]
        self.setGeometry(self.x(),
                         self.y(),
                         self._filters_widget.x() - 5 - self.x(),
                         self._sources_widget.height()
                         )
        self.setMinimumWidth(self.width())
        self.setMinimumHeight(self.height())
