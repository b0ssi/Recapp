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
import bs.ctrl.session
import bs.gui.lib
import bs.messages.general
import json
import logging
import re
import threading
import time


class BS(QtGui.QFrame):
    """ * """
    _window_main = None
    _session_gui = None
    _backup_sets = None
    _app = None

    gui_data_modified_signal = None
    resizeSignal = QtCore.Signal(QtGui.QResizeEvent)
    _menu_sets = None
    _bs_sets_canvas = None
    _backup_set_current = None

    def __init__(self, window_main, session_gui, app):
        super(BS, self).__init__(window_main)

        self._window_main = window_main
        self._session_gui = session_gui
        self._backup_sets = session_gui.session.backup_sets
        self._app = app

        self.gui_data_modified_signal = bs.utils.Signal()
        self.gui_data_modified_signal.connect(self._app.idle_1s_timer.start)
        self.gui_data_save_signal = bs.utils.Signal()
        self.gui_data_save_signal.connect(self._save_to_db)
        self._app.idle_1s_timer.timeout.connect(self.gui_data_save_signal.emit)
        self._init_ui()

    def _init_ui(self):
        """ * """
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        self._menu_sets = BSMenu(self, self._backup_sets)
        self._bs_sets_canvas = BSSetsCanvas(self, self._menu_sets, self._app)

    @property
    def bs_sets_canvas(self):
        return self._bs_sets_canvas

    @property
    def backup_set_current(self):
        return self._backup_set_current

    @backup_set_current.setter
    def backup_set_current(self, backup_set_current):
        if not isinstance(backup_set_current, bs.ctrl.session.BackupSetCtrl):
            logging.warning("%s: The first argument needs to be of type BackupSetCtrl."
                            % (self.__class__.__name__, ))
            return False
        self._backup_set_current = backup_set_current

    @property
    def session_gui(self):
        return self._session_gui

    def set_modified(self, force_save=False):
        """ *
        Triggers the modified signal (which again sets connected handlers such
        as a save button to enabled, etc.) which then starts the timer which
        has a connection to self._save_to_db().
        force_save evades the timer, stops it and calls self._save_to_db()
        directly.
        """
        if force_save:
            self._app.idle_1s_timer.stop()
            self._save_to_db()
            self.gui_data_save_signal.emit()
        else:
            self.gui_data_modified_signal.emit()

    def _save_to_db(self):
        """ *
        Designed to get triggered by either a save button or an (idle) timer
        timeout. Only calls the actual _save_to_db function on the current
        BackupSetCtrl().
        """
        if self._backup_set_current:
            # update node data in memory
            for node_widget in self._bs_sets_canvas.bs_source_widgets + self._bs_sets_canvas.bs_filter_widgets + self._bs_sets_canvas.bs_target_widgets:
                node_widget.save_gui_data()
            # save node data to db
            self._backup_set_current.save_to_db()
            logging.debug("%s: Set %s successfully saved to db."
                          % (self.__class__.__name__,
                             self.backup_set_current, ))

#    def save_gui_data(self):
#        """ *
#        Saves the state of all currently existing nodes' data (usually only for
#        active set or none if no set active) to backup_set.gui_data.
#        Does not save to db. self.save_gui_data_to_db() does that explicitly.
#        """
#        for node_widget in self._bs_source_widgets + self._bs_filter_widgets + self._bs_target_widgets:
#            node_widget.save_gui_data()
#
#    def save_gui_data_to_db(self):
#        """ *
#        Saves current backup_set's gui_data to db.
#        """
#        if self._bs.backup_set_current:
#            self._bs.backup_set_current.save_to_db()
#            logging.debug("%s: Set %s successfully saved to db."
#                          % (self.__class__.__name__,
#                             self._bs.backup_set_current, ))
#        else:
#            logging.debug("%s: No set saved: No set loaded."
#                          % (self.__class__.__name__, ))

    def resizeEvent(self, e):
        """ * """
        self.resizeSignal.emit(e)


class BSSetsCanvas(bs.gui.lib.BSCanvas):
    """ * """
    _bs = None
    _menu_sets = None
    _app = None

    _bs_source_widgets = None
    _bs_filter_widgets = None
    _bs_target_widgets = None
    _bs_arrow_widgets = None
    _bs_arrow_carrier = None  # This is where the temporary arrow's carrier is held when interactively connecting nodes. Initialized on node's connectins socket
    _mouse_press_global_pos = None

    def __init__(self, bs, menu_sets, app):
        super(BSSetsCanvas, self).__init__(bs)

        self._bs = bs
        self._menu_sets = menu_sets
        self._app = app

        self._bs_source_widgets = []
        self._bs_filter_widgets = []
        self._bs_target_widgets = []
        self._bs_arrow_widgets = []

        self._init_ui()
        self.lower()

    @property
    def bs_source_widgets(self):
        return self._bs_source_widgets

    @property
    def bs_filter_widgets(self):
        return self._bs_filter_widgets

    @property
    def bs_target_widgets(self):
        return self._bs_target_widgets

    @property
    def bs_arrow_widgets(self):
        return self._bs_arrow_widgets

    @property
    def bs_arrow_btn_del_widgets(self):
        return [x for x in self.children() if isinstance(x, bs.gui.lib.BSArrowBtnDel)]

    def _init_ui(self):
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

    def restack(self):
        """ *
        Restacks children in correct order so they don't overlap
        inappropriately.
        """
        for widget in self.bs_arrow_btn_del_widgets:
            widget.lower()
        for widget in self.bs_arrow_widgets:
            widget.lower()

    def empty_canvas(self):
        """ *
        Empties the canvas, removing/deleting all widgets and arrows.
        """
        for bs_source_widget in self._bs_source_widgets:
            if not bs_source_widget.request_exit():
                logging.warning("%s: Node did not respond positively to exit request." % (self.__class__.__name__, ))
                return False
            bs_source_widget.deleteLater()
        self._bs_source_widgets = []
        for bs_filters_widgets in self._bs_filter_widgets:
            bs_filters_widgets.deleteLater()
        self._bs_filter_widgets = []
        for bs_target_widget in self._bs_target_widgets:
            bs_target_widget.deleteLater()
        self._bs_target_widgets = []
        while len(self._bs_arrow_widgets) > 0:
            self._bs_arrow_widgets[0].delete()
        self._bs_arrow_widgets = []
        # arrow_tmp_carrier_widget
        if self._bs_arrow_carrier:
            # unregister old carrier's signals
            self._bs_arrow_carrier.unregister_signals()
            # delete
            self._bs_arrow_carrier.deleteLater()
        return True

    def close_set(self):
        """ *
        Closes the current backup_set
        """
        # save current set
        self._bs.set_modified(force_save=True)
        # EMPTY CANVAS
        # clean canvas, delete old widgets
        if not self.empty_canvas():
            logging.warning("%s: Canvas could not be emptied." % (self.__class__.__name__, ))
            return False
        # arrow_carrier
        self._bs_arrow_carrier = bs.gui.lib.BSArrowCarrier(self,
                                                           self._app,
                                                           self._bs)

    def load_set(self, backup_set):
        """ *
        Loads a backup-set onto the canvas.
        """
        self.close_set()
        # set new current set
        self._bs.backup_set_current = backup_set
        # LOAD NODES
        # Load backup-sources
        for backup_source in backup_set.backup_sources:
            self.add_node(backup_source, backup_set)
        # load backup-filters
        for backup_entity in backup_set.backup_filters:
            self.add_node(backup_entity, backup_set)
        # load target set
        if backup_set.backup_targets:
            self.add_node(backup_set.backup_targets, backup_set)
        # CONNECT NODES
        # sources - filters/targets
        for bs_source_widget in self._bs_source_widgets:
            backup_entity_ass = bs_source_widget.backup_entity.backup_entity_ass[self._bs.backup_set_current]
            if backup_set.backup_targets in backup_entity_ass:
                widget = bs.gui.lib.BSArrow(self._bs, bs_source_widget, self._bs_target_widgets[0])
            for bs_filter_widget in self._bs_filter_widgets:
                backup_entity = bs_filter_widget.backup_entity
                if backup_entity in backup_entity_ass:
                    # we have source and filter widget now. Connect!
                    widget = bs.gui.lib.BSArrow(self._bs, bs_source_widget, bs_filter_widget)
        # filters - filters/targets
        for bs_filter_widget_a in self._bs_filter_widgets:
            backup_filter_a = bs_filter_widget_a.backup_entity
            backup_filter_a_ass = backup_filter_a.backup_entity_ass[self._bs.backup_set_current]
            if backup_set.backup_targets in backup_filter_a_ass:
                widget = bs.gui.lib.BSArrow(self._bs, bs_filter_widget_a, self._bs_target_widgets[0])
            for bs_filter_widget_b in self._bs_filter_widgets:
                backup_filter_b = bs_filter_widget_b.backup_entity
                if backup_filter_b in backup_filter_a_ass and\
                    backup_filter_b != backup_filter_a:
                    # we have both associated filters now. Connect!
                    widget = bs.gui.lib.BSArrow(self._bs, bs_filter_widget_a, bs_filter_widget_b)
        # LAY-OUT NODES
        # sources
        for bs_source_widget in self._bs_source_widgets:
            # get pos data
            gui_data = backup_set.gui_data
            try:
                pos = gui_data["nodes"]["bs_source_widgets"][str(bs_source_widget.backup_entity.backup_source_id)]["pos"]
            except:
                pos = [self.width() / 2, self.height() / 2]
            x_c = pos[0]
            y_c = pos[1]
            x = x_c - bs_source_widget.width() / 2
            y = y_c - bs_source_widget.height() / 2
            bs_source_widget.setGeometry(x, y,
                                         bs_source_widget.width(),
                                         bs_source_widget.height())
        # filters
        for bs_filter_widget in self._bs_filter_widgets:
            # get pos data
            gui_data = backup_set.gui_data
            try:
                pos = gui_data["nodes"]["bs_filter_widgets"][str(bs_filter_widget.backup_entity.backup_filter_id)]["pos"]
            except:
                pos = [self.width() / 2, self.height() / 2]
            x_c = pos[0]
            y_c = pos[1]
            x = x_c - bs_filter_widget.width() / 2
            y = y_c - bs_filter_widget.height() / 2
            bs_filter_widget.setGeometry(x, y,
                                         bs_filter_widget.width(),
                                         bs_filter_widget.height())
        # targets
        for bs_target_widget in self._bs_target_widgets:
            # get pos data
            gui_data = backup_set.gui_data
            try:
                pos = gui_data["nodes"]["bs_target_widgets"]["container"]["pos"]
            except:
                pos = [self.width() / 2, self.height() / 2]
            x_c = pos[0]
            y_c = pos[1]
            x = x_c - bs_target_widget.width() / 2
            y = y_c - bs_target_widget.height() / 2
            bs_target_widget.setGeometry(x, y,
                                         bs_target_widget.width(),
                                         bs_target_widget.height())
        # REDRAW ARROWS
        for bs_filter_widget in self._bs_filter_widgets:
            bs_filter_widget.draw_arrows()
        for bs_target_widget in self._bs_target_widgets:
            bs_target_widget.draw_arrows()
        self.update()

    def add_node(self, backup_entity, backup_set, global_pos=None):
        """ *
        Adds a new node.
        """
        if isinstance(backup_entity, bs.ctrl.session.BackupSourceCtrl):
            widget = BSSource(self, self._bs, backup_entity, backup_set, self._app)
            self._bs_source_widgets.append(widget)
            # add entity on ctrl level
            backup_set.add_backup_source(backup_entity)
        elif isinstance(backup_entity, bs.ctrl.session.BackupFilterCtrl):
            widget = BSFilter(self, self._bs, backup_entity, backup_set, self._app)
            self._bs_filter_widgets.append(widget)
            # add entity on ctrl level
            backup_set.add_backup_filter(backup_entity)
        elif isinstance(backup_entity, list) and\
            isinstance(backup_entity[0], bs.ctrl.session.BackupTargetCtrl):
            widget = BSTarget(self, self._bs, backup_entity, backup_set, self._app)
            self._bs_target_widgets.append(widget)
        # set position
        if global_pos:
            widget.setGeometry(self.mapFromGlobal(global_pos).x(),
                               self.mapFromGlobal(global_pos).y(),
                               widget.width(),
                               widget.height())
        self._bs.set_modified()

    def mousePressEvent(self, e):
        self._mouse_press_global_pos = e.globalPos()

        super(BSSetsCanvas, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ *
        """
        if e.globalPos() == self._mouse_press_global_pos and\
            e.button() & QtCore.Qt.MouseButton.RightButton and\
            self._bs.backup_set_current:
            # Main context menu
            menu_main = BSSetsCMenu(self, self._bs.backup_set_current, e.globalPos())
            menu_main.popup(e.globalPos())
        else:
            super(BSSetsCanvas, self).mouseReleaseEvent(e)

    def keyPressEvent(self, e):
        """ * """
        if e.text() == "h":
            bs_nodes = self._bs_filter_widgets + self._bs_source_widgets + self._bs_target_widgets
            bb_l = 0
            bb_t = 0
            bb_r = 0
            bb_b = 0
            for bs_node in bs_nodes:
                if bs_node is bs_nodes[0]:
                    bb_l = bs_node.x()
                    bb_r = bs_node.x() + bs_node.width()
                    bb_t = bs_node.y()
                    bb_b = bs_node.y() + bs_node.height()
                # generate bounding box for current node positions
                if bs_node.x() < bb_l:
                    bb_l = bs_node.x()
                if (bs_node.x() + bs_node.width()) > bb_r:
                    bb_r = (bs_node.x() + bs_node.width())
                if bs_node.y() < bb_t:
                    bb_t = bs_node.y()
                if (bs_node.y() + bs_node.height()) > bb_b:
                    bb_b = (bs_node.y() + bs_node.height())
            bb_current = QtCore.QRect(bb_l,
                                      bb_t,
                                      bb_r - bb_l,
                                      bb_b - bb_t)
            for bs_node in bs_nodes:
                # bring node down into view
                bs_node.setGeometry(int(bs_node.x() - (bb_current.center().x() - self.width() / 2)),
                                    int(bs_node.y() - (bb_current.center().y() - self.height() / 2)),
                                    bs_node.width(),
                                    bs_node.height())
                bs_node.draw_arrows()
            self._bs.set_modified()


class BSSetsCMenu(QtGui.QMenu):
    """ * """
    _bs_sets_canvas = None
    _backup_set_current = None
    _c_menu_main_global_pos = None

    _menu_sources = None
    _menu_filters = None

    def __init__(self,
                 bs_sets_canvas,
                 backup_set_current,
                 c_menu_main_global_pos):
        super(BSSetsCMenu, self).__init__(bs_sets_canvas)

        self._bs_sets_canvas = bs_sets_canvas
        self._backup_set_current = backup_set_current
        self._c_menu_main_global_pos = c_menu_main_global_pos

        self._init_ui()

    def _init_ui(self):
        self._menu_sources = BSSetsCMenuSub("Sources",
                                            self,
                                            self._bs_sets_canvas._bs.session_gui.session.backup_sources.backup_sources,
                                            self._bs_sets_canvas._bs.backup_set_current.backup_sources,
                                            self._bs_sets_canvas,
                                            self._backup_set_current,
                                            self._c_menu_main_global_pos)
        self._menu_filters = BSSetsCMenuSub("Filters",
                                            self,
                                            self._bs_sets_canvas._bs.session_gui.session.backup_filters.backup_filters,
                                            self._bs_sets_canvas._bs.backup_set_current.backup_filters,
                                            self._bs_sets_canvas,
                                            self._backup_set_current,
                                            self._c_menu_main_global_pos)
        self.addMenu(self._menu_sources)
        self.addMenu(self._menu_filters)


class BSSetsCMenuSub(QtGui.QMenu):
    """ * """
    _backup_entities_session = None  # these is the list of entities (backup_sources/backup_filters) for the entire sessionself._bs.backup_set_current.backup_sources
    _backup_entities_set = None  # these is the list of entities (backup_sources/backup_filters) for the entire sessionself._bs.backup_set_current.backup_sources
    _bs_sets_canvas = None
    _backup_set_current = None
    _c_menu_main_global_pos = None

    def __init__(self,
                 name,
                 parent,
                 backup_entities_session,
                 backup_entities_set,
                 bs_sets_canvas,
                 backup_set_current,
                 c_menu_main_global_pos):
        super(BSSetsCMenuSub, self).__init__(name, parent)

        self._backup_entities_session = backup_entities_session
        self._backup_entities_set = backup_entities_set
        self._bs_sets_canvas = bs_sets_canvas
        self._backup_set_current = backup_set_current
        self._c_menu_main_global_pos = c_menu_main_global_pos

        self._init_ui()

    def _init_ui(self):
        sources_unused = [x for x in self._backup_entities_session if x not in self._backup_entities_set]
        for backup_entity in sources_unused:
            if isinstance(backup_entity, bs.ctrl.session.BackupSourceCtrl):
                name = backup_entity.source_name
            elif isinstance(backup_entity, bs.ctrl.session.BackupFilterCtrl):
                name = backup_entity.backup_filter_name
            action = BSSetsCMenuAction(name,
                                       self,
                                       self._bs_sets_canvas,
                                       backup_entity,
                                       self._backup_set_current,
                                       self._c_menu_main_global_pos)
            self.addAction(action)
        if len(sources_unused) == 0:
            self.setDisabled(True)


class BSSetsCMenuAction(QtGui.QAction):
    """ * """
    _bs_sets_canvas = None
    _backup_entity = None
    _backup_set_current = None
    _c_menu_main_global_pos = None

    def __init__(self,
                 name,
                 parent,
                 bs_sets_canvas,
                 backup_entity,
                 backup_set_current,
                 c_menu_main_global_pos):
        super(BSSetsCMenuAction, self).__init__(name, parent)

        self._bs_sets_canvas = bs_sets_canvas
        self._backup_entity = backup_entity
        self._backup_set_current = backup_set_current
        self._c_menu_main_global_pos = c_menu_main_global_pos

        self._init_ui()

    def _init_ui(self):
        self.triggered.connect(self.fire)

    def fire(self):
        self._bs_sets_canvas.add_node(self._backup_entity,
                                      self._backup_set_current,
                                      self._c_menu_main_global_pos)


class BSMenu(bs.gui.lib.BSDraggable):
    """ * """
    _bs = None
    _backup_sets = None

    _x_c = None
    _y_c = None
    _btn_save = None

    def __init__(self, bs, backup_sets):
        super(BSMenu, self).__init__(bs)

        self._bs = bs
        self._backup_sets = backup_sets

        self.parent().resizeSignal.connect(self.resizeEvent)

        self._init_ui()

    def _init_ui(self):
        # layout
        self._layout = QtGui.QGridLayout(self)
        # these MUST be floats!
        self._x_c = float(0.0)
        self._y_c = float(0.0)
        # title
        self.title_text = "Sets"
        self.title_size = 18
        # refresh with set buttons
        self.refresh()
        self.setGeometry(20,
                         self.parent().height() / 2 - self.height() / 2,
                         self.width(),
                         self.height())
        self._x_c = self.x() + self.width() / 2
        self._y_c = self.y() + self.height() / 2
        # Drop shadow
        gfx = QtGui.QGraphicsDropShadowEffect(self)
        gfx.setOffset(0)
        gfx.setColor(QtGui.QColor(20, 20, 20))
        gfx.setBlurRadius(4)
        self.setGraphicsEffect(gfx)

    def refresh(self):
        """ *
        Populates the menu with BSNodeItem
        """
        # delete old widgets
        for layout_pos in range(self._layout.count() - 1):
            widget_item = self._layout.takeAt(1)
            widget_item.widget().deleteLater()
            del(widget_item)
        # re-populate with widgets
        for backup_set in self._backup_sets.sets:
            widget = BSMenuItem(self, backup_set, self._bs, self._backup_sets)
            self._layout.addWidget(widget, self._layout.count(), 0, 1, 1)
        # spacer widget
        widget = QtGui.QWidget(self)
        widget.setMinimumHeight(10)
        self._layout.addWidget(widget, self._layout.count(), 0, 1, 1)
        # save button
        btn_save = BSMenuItemSave(self, self._bs)
        self._layout.addWidget(btn_save, self._layout.count(), 0, 1, 1)
        # refresh height
        self._refresh_height()

    def _refresh_height(self):
        """ *
        Recalculates widget's size based on minimumHeight of all widgets in
        its layout + spacing + margins and sets it.
        """
        # recalculate size
        min_height = 0
        # widget height
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            min_height += widget.minimumHeight()
        # spacing
        min_height += self._layout.spacing() * (self.layout().count() - 1)
        # margins
        min_height += self._layout.contentsMargins().top()
        min_height += self._layout.contentsMargins().bottom()
        # set pos
        self.show()
        x = self.x()
        y = self.y()
        self.setMaximumHeight(min_height)
        # have to reset pos() as resizeEvent would move the widget otherwise.
        self.setGeometry(x,
                         y,
                         self.width(),
                         self.height()
                         )

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
    _backup_sets = None

    def __init__(self, bs_menu, backup_set, bs, backup_sets):
        super(BSMenuItem, self).__init__(bs_menu)

        self._bs_menu = bs_menu
        self._backup_set = backup_set
        self._bs = bs
        self._backup_sets = backup_sets

        self._init_ui()

    def _init_ui(self):
        """ * """
        # layout
#        self._layout.setColumnStretch(0, 100)
#        self._layout.setColumnStretch(1, 1)
#        self._layout.setColumnMinimumWidth(1, 28)
        # title
        self.title_text = self._backup_set.set_name
        # buttons
        self._btn_del = BSMenuItemBtnDel(self._bs_menu, self, "DEL", self._backup_set, self._backup_sets, self._bs)
        self._layout.addWidget(self._btn_del, 0, 1, 1, 1)
        # CSS
        self.css = ((self,
                     "",
                     "background: #%s",
                     (
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[0], ),
                      (bs.config.PALETTE[0], ),
                      (bs.config.PALETTE[0], ),
                      (bs.config.PALETTE[0], ),
                      (bs.config.PALETTE[0], ),
                      )
                     ),
                     (self.title,
                      "",
                      "color: #%s",
                      (
                       (bs.config.PALETTE[3], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                      )
                     )
                    )

    def mousePressEvent(self, e):
        """ * """
        super(BSMenuItem, self).mousePressEvent(e)

        self._bs._bs_sets_canvas.load_set(self._backup_set)


class BSMenuItemBtnDel(bs.gui.lib.BSNodeItemButton):
    """ * """
    _title = None
    _bs_menu = None
    _bs_menu_item = None
    _backup_set = None
    _backup_sets = None
    _bs = None

    def __init__(self, bs_menu, bs_menu_item, title, backup_set, backup_sets, bs):
        super(BSMenuItemBtnDel, self).__init__(bs_menu, title)

        self._title = title
        self._bs_menu = bs_menu
        self._bs_menu_item = bs_menu_item
        self._backup_set = backup_set
        self._backup_sets = backup_sets
        self._bs = bs

    def mousePressEvent(self, e):
        """ * """
#        super(BSMenuItemBtnDel, self).mousePressEvent(e)

        msg_box = bs.gui.lib.BSMessageBox(QtGui.QMessageBox.Warning,
                                          "Confirm Deletion",
                                          "<p>Are you sure you wish to delete "\
                                          "Backup-Set <b>%s</b>?</p>"\
                                          "<p>The Backup-Sources, -Filters "\
                                          "and -Targets contained in the "\
                                          "Backup-Set will not be deleted.</p>"
                                          % (self._backup_set.set_name, ))
        msg_box_cancel = msg_box.addButton(msg_box.Cancel)
        msg_box_ok = msg_box.addButton(msg_box.Ok)
        msg_box.exec_()
        if msg_box.clickedButton() == msg_box_ok:
            self._backup_sets.delete_backup_set(self._backup_set)
            # empty the canvas
            self._bs.bs_sets_canvas.empty_canvas()
            # refresh the menu
            self._bs_menu.refresh()


class BSMenuItemSave(bs.gui.lib.BSNodeItem):
    """ * """
    _bs = None
    _bs_menu = None

    def __init__(self, bs_menu, bs):
        super(BSMenuItemSave, self).__init__(bs_menu)

        self._bs = bs
        self._bs_menu = bs_menu

        self._init_ui()

    def _init_ui(self):
        # connect to signals
        self._bs.gui_data_modified_signal.connect(self.setEnabled)
        self._bs.gui_data_save_signal.connect(self.setDisabled)
        self.setDisabled(True)
        # layout
        # title
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title_text = "SAVE"
        # CSS
        self.css = ((self,
                     "",
                     "background: #%s",
                     (
                      (bs.config.PALETTE[8], ),
                      (bs.config.PALETTE[7], ),
                      (bs.config.PALETTE[7], ),
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[1], ),
                      )
                     ),
                     (self.title,
                      "",
                      "color: #%s",
                      (
                       (bs.config.PALETTE[3], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[6], ),
                       (bs.config.PALETTE[6], ),
                       (bs.config.PALETTE[6], ),
                      )
                     )
                    )

    def setEnabled(self, *args, **kwargs):
        super(BSMenuItemSave, self).setEnabled(*args, **kwargs)

        self.title_text = "SAVE"

    def setDisabled(self, *args, **kwargs):
        super(BSMenuItemSave, self).setDisabled(*args, **kwargs)

        self.title_text = "SAVED"

    def mousePressEvent(self, e):
        """ *
        Triggers backup_set.save_to_db() and disables this button again.
        """
        super(BSMenuItemSave, self).mousePressEvent(e)

        self._bs.set_modified(force_save=True)


class BSSource(bs.gui.lib.BSNode):
    """ * """
    _bs = None
    _bs_sets_canvas = None
    _backup_entity = None
    _backup_set = None
    _app = None

    _mouse_press_event_pos = None  # this holds the press_event object's pos()
    _bs_source_item = None

    def __init__(self,
                 bs_sets_canvas,
                 bs,
                 backup_source,
                 backup_set,
                 app):
        super(BSSource, self).__init__(bs, bs_sets_canvas, app, True)

        self._bs_sets_canvas = bs_sets_canvas
        self._bs = bs
        self._backup_entity = backup_source
        self._backup_set = backup_set
        self._app = app

        self._init_ui()

    @property
    def backup_entity(self):
        return self._backup_entity

    def _init_ui(self):
        # css
        self.setStyleSheet("BSSource {border: 1px solid #%s}" % (bs.config.PALETTE[2], ))
        # title
        self.title_text = self._backup_entity.source_name
        self.title_size = 13
        # populate with item
        self._bs_source_item = BSSourceItem(self, self._backup_entity, self._backup_set)
        self._custom_contents_container._layout.addWidget(self._bs_source_item, self._layout.count(), 0, 1, 1)
#         self._layout.addWidget(self._bs_source_item, self._layout.count(), 0, 1, 1)
        self.show()

    def save_gui_data(self):
        """ *
        Saves the state of the node.
        This includes node-position only for now.
        Not to be called by itself; only by an iterator that runs through *all*
        nodes to call this save_gui_data method.
        """
        x = self.geometry().x()
        y = self.geometry().y()
        x_c = x + self.width() / 2
        y_c = y + self.height() / 2
        pos = [x_c, y_c]
        gui_data = self._backup_set.gui_data
        # build dict
        try:
            x = gui_data["nodes"]
        except:
            gui_data["nodes"] = {}
        try:
            x = gui_data["nodes"]["bs_source_widgets"]
        except:
            gui_data["nodes"]["bs_source_widgets"] = {}
        try:
            x = gui_data["nodes"]["bs_source_widgets"][str(self._backup_entity.backup_source_id)]
        except:
            gui_data["nodes"]["bs_source_widgets"][str(self._backup_entity.backup_source_id)] = {}
        # update dict
        gui_data["nodes"]["bs_source_widgets"][str(self._backup_entity.backup_source_id)]["pos"] = pos

    def remove_node(self):
        """ * """
        super(BSSource, self).remove_node()

        # unregister set-association
        self._backup_entity.backup_entity_ass.pop(self._backup_set)
        # remove from set-ctrl
        self._backup_set.backup_sources.pop(self._backup_set.backup_sources.index(self._backup_entity))
        # remove from canvas
        self._bs_sets_canvas.bs_source_widgets.pop(self._bs_sets_canvas.bs_source_widgets.index(self))
        self.deleteLater()

    def request_exit(self):
        """ * """
        if self._bs_source_item.request_exit():
            return True
        else:
            logging.warning("%s: Could not exit." % (self.__class__.__name__, ))
            return False

    def mousePressEvent(self, e):
        """ * """
        super(BSSource, self).mousePressEvent(e)

        self._mouse_press_event_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        """ * """
        super(BSSource, self).mouseReleaseEvent(e)
        # emit modified-signal, only if mouse has actually moved
        if self._mouse_press_event_pos != e.globalPos():
            self._bs.set_modified()


class BSSourceItem(bs.gui.lib.BSNodeItem):
    """ * """
    _bs_source = None
    _backup_entity = None
    _backup_set = None

    _update_thread = None
    _request_exit = None

    def __init__(self, bs_source, backup_source, backup_set):
        super(BSSourceItem, self).__init__(bs_source)

        self._bs_source = bs_source
        self._backup_entity = backup_source
        self._backup_set = backup_set

        self._request_exit = False

        self._init_ui()

    def _init_ui(self):
        """ * """
        self.title_text = "Calculate Pending Data"
        # CSS
        self.css = ((self,
                     "",
                     "background: #%s",
                     (
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[0], ),
                      (bs.config.PALETTE[0], ),
                      (bs.config.PALETTE[0], ),
                      (bs.config.PALETTE[0], ),
                      (bs.config.PALETTE[0], ),
                      )
                     ),
                     (self.title,
                      "",
                      "color: #%s",
                      (
                       (bs.config.PALETTE[3], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                       (bs.config.PALETTE[4], ),
                      )
                     )
                    )

    def mouseReleaseEvent(self, e):
        """ * """
        # if backup_set is encrypted, prompt for key
        if self._backup_set.salt_dk:
            err_msg = "The Backup-Set seems to be encrypted. Please enter the password:"
            while not self._backup_set.is_authenticated:
                key_raw, ok = QtGui.QInputDialog.getText(self,
                                                         "Backup-Set Authentication",
                                                         err_msg,
                                                         echo=QtGui.QLineEdit.Password,
                                                         text="",
                                                         flags=0)
                if ok:
                    self._backup_set.authenticate(key_raw)
                else:
                    break
                if self._backup_set.is_authenticated:
                    break
                err_msg = "Invalid password. Please try again:"
            if self._backup_set.is_authenticated:
                if not self._update_thread or\
                    not self._update_thread.is_alive():
                    self._update_thread = threading.Thread(target=self.update)
                    self._update_thread.start()

    def update(self):
        pre_calc_thread = self._backup_set.backup_ctrls[self._backup_entity].pre_process_data()
        while True:
            bytes_to_be_backed_up = self._backup_set.backup_ctrls[self._backup_entity].bytes_to_be_backed_up
            if self._request_exit:
                self._backup_set.backup_ctrls[self._backup_entity].request_exit()
            files_num_to_be_backed_up = self._backup_set.backup_ctrls[self._backup_entity].files_num_to_be_backed_up
            self.title_text = "%s | %s files" % (bs.utils.format_data_size(bytes_to_be_backed_up),
                                                 files_num_to_be_backed_up, )
            if not pre_calc_thread.is_alive():
                break
            time.sleep(0.1)

    def request_exit(self):
        """ *
        Requests threads to exit. To be used before deleting a node.
        """
        self._request_exit = True
        while True:
            if not self._update_thread or\
                not self._update_thread.is_alive():
                break
            else:
                time.sleep(0.1)
        self._request_exit = False
        return True


class BSFilter(bs.gui.lib.BSNode):
    """ * """
    _bs_sets_canvas = None
    _bs = None
    _backup_entity = None
    _backup_set = None
    _app = None

    _mouse_press_event_pos = None  # this holds the press_event object's pos()

    def __init__(self,
                 bs_sets_canvas,
                 bs,
                 backup_entity,
                 backup_set,
                 app):
        super(BSFilter, self).__init__(bs, bs_sets_canvas, app, True)

        self._bs_sets_canvas = bs_sets_canvas
        self._bs = bs
        self._backup_entity = backup_entity
        self._backup_set = backup_set
        self._app = app

        self._init_ui()

    @property
    def backup_entity(self):
        return self._backup_entity

    def _init_ui(self):
        self.setMaximumWidth(400)
        # css
        self.setStyleSheet("BSFilter {border: 1px solid #%s}" % (bs.config.PALETTE[2], ))
        # title
        self.title_text = self._backup_entity.backup_filter_name
        self.title_size = 13
        # backup-filter items
        for backup_filter_rule in self._backup_entity.backup_filter_rules:
            widget = BSFilterItem(self, backup_filter_rule)
            self._custom_contents_container._layout.addWidget(widget, self._custom_contents_container._layout.count(), 0,
                                                              1, 1)
        self.show()

    def mousePressEvent(self, e):
        """ * """
        super(BSFilter, self).mousePressEvent(e)

        self._mouse_press_event_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        """ * """
        super(BSFilter, self).mouseReleaseEvent(e)

        # emit modified-signal, only if mouse has actually moved
        if self._mouse_press_event_pos != e.globalPos():
            self._bs.set_modified()

    def save_gui_data(self):
        """ *
        Saves the state of the node.
        This includes node-position only for now.
        Not to be called by itself; only by an iterator that runs through *all*
        nodes to call this save_gui_data method.
        """
        x = self.geometry().x()
        y = self.geometry().y()
        x_c = x + self.width() / 2
        y_c = y + self.height() / 2
        pos = [x_c, y_c]
        gui_data = self._backup_set.gui_data
        # build dict
        try:
            x = gui_data["nodes"]
        except:
            gui_data["nodes"] = {}
        try:
            x = gui_data["nodes"]["bs_filter_widgets"]
        except:
            gui_data["nodes"]["bs_filter_widgets"] = {}
        try:
            x = gui_data["nodes"]["bs_filter_widgets"][str(self._backup_entity.backup_filter_id)]
        except:
            gui_data["nodes"]["bs_filter_widgets"][str(self._backup_entity.backup_filter_id)] = {}
        # update dict
        gui_data["nodes"]["bs_filter_widgets"][str(self._backup_entity.backup_filter_id)]["pos"] = pos

    def remove_node(self):
        """ * """
        super(BSFilter, self).remove_node()

        # unregister set-association
        self._backup_entity.backup_entity_ass.pop(self._backup_set)
        # remove from set-ctrl
        self._backup_set.backup_filters.pop(self._backup_set.backup_filters.index(self._backup_entity))
        # remove from canvas
        self._bs_sets_canvas.bs_filter_widgets.pop(self._bs_sets_canvas.bs_filter_widgets.index(self))
        self.deleteLater()


class BSFilterItem(bs.gui.lib.BSNodeItem):
    """ * """
    _bs_filter = None
    _backup_filter_rule = None

    def __init__(self, bs_filter, backup_filter_rule):
        super(BSFilterItem, self).__init__(bs_filter)

        self._bs_filter = bs_filter
        self._backup_filter_rule = backup_filter_rule

        self._init_ui()

    def _init_ui(self):
        self.title_text = self._backup_filter_rule
        # CSS
        self.css = ((self,
                     "",
                     "background: #%s",
                     (
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[1], ),
                      (bs.config.PALETTE[1], ),
                      )
                     ),
                     (self.title,
                      "",
                      "color: #%s",
                      (
                       (bs.config.PALETTE[3], ),
                       (bs.config.PALETTE[3], ),
                       (bs.config.PALETTE[3], ),
                       (bs.config.PALETTE[3], ),
                       (bs.config.PALETTE[3], ),
                       (bs.config.PALETTE[3], ),
                      )
                     )
                    )
        self._title.setDisabled(True)
        self._title.setWordWrap(True)
        self._layout.setContentsMargins(self._layout.contentsMargins().left(),
                                        5,
                                        self._layout.contentsMargins().right(),
                                        5)

    def mouseMoveEvent(self, e):
        self.parent().mouseMoveEvent(e)


class BSTarget(bs.gui.lib.BSNode):
    """ * """
    _bs_sets_canvas = None
    _bs = None
    _backup_entity = None
    _backup_set = None
    _app = None

    _mouse_press_event_pos = None  # this holds the press_event object's pos()

    def __init__(self,
                 bs_sets_canvas,
                 bs,
                 backup_entity,
                 backup_set,
                 app):
        super(BSTarget, self).__init__(bs, bs_sets_canvas, app)

        self._bs_sets_canvas = bs_sets_canvas
        self._bs = bs
        self._backup_entity = backup_entity
        self._backup_set = backup_set
        self._app = app

        self._init_ui()

    @property
    def backup_entity(self):
        return self._backup_entity

    def _init_ui(self):
        # css
        self.setStyleSheet("BSTarget {border: 1px solid #%s}" % (bs.config.PALETTE[2], ))
        # title
        self.title_text = "Targets"
        self.title_size = 13
        self.show()

    def mousePressEvent(self, e):
        """ * """
        super(BSTarget, self).mousePressEvent(e)

        self._mouse_press_event_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        """ * """
        super(BSTarget, self).mouseReleaseEvent(e)

        # emit modified-signal, only if mouse has actually moved
        if self._mouse_press_event_pos != e.globalPos():
            self._bs.set_modified()

    def save_gui_data(self):
        """ *
        Saves the state of the node.
        This includes node-position only for now.
        Not to be called by itself; only by an iterator that runs through *all*
        nodes to call this save_gui_data method.
        """
        x = self.geometry().x()
        y = self.geometry().y()
        x_c = x + self.width() / 2
        y_c = y + self.height() / 2
        pos = [x_c, y_c]
        gui_data = self._backup_set.gui_data
        # build dict
        try:
            x = gui_data["nodes"]
        except:
            gui_data["nodes"] = {}
        try:
            x = gui_data["nodes"]["bs_target_widgets"]
        except:
            gui_data["nodes"]["bs_target_widgets"] = {}
        try:
            x = gui_data["nodes"]["bs_target_widgets"]["container"]
        except:
            gui_data["nodes"]["bs_target_widgets"]["container"] = {}
        # update dict
        gui_data["nodes"]["bs_target_widgets"]["container"]["pos"] = pos

    def keyPressEvent(self, e):
        """ *
        Override
        """

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
#    _backup_entity = None
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
#        self._backup_entity = backup_source
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
#        backup_source_name = self._backup_entity.source_name
#        title_widget = QtGui.QLabel(backup_source_name, self)
#        title_widget.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
#        self._layout.addWidget(title_widget, 0, 0, 1, 1)
#
#        # del button
#
#
#        # path
#        backup_source_path = self._backup_entity.source_path
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
#        self._view_sets_details_sources.remove_backup_source(self._backup_entity)
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
#    _backup_entity = None
#
#    _layout = None
#
#    def __init__(self, view_sets_details_filters, backup_filter):
#        super(ViewSetsDetailsFilter, self).__init__(view_sets_details_filters)
#
#        self._view_sets_details_filters = view_sets_details_filters
#        self._backup_entity = backup_filter
#
#        self._init_ui()
#
#    def _init_ui(self):
#        """ * """
#        self._layout = QtGui.QGridLayout(self)
#
#        # title
#        backup_filter_name = self._backup_entity.filter_pattern
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
