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

""" ..

"""

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
    """ ..

    """
    _window_main = None
    _session_gui = None
    _backup_sets = None
    _app = None

    _gui_data_modified_signal = None
    _gui_data_save_signal = None
    _resizeSignal = None
    _menu_sets = None
    _bs_sets_canvas = None
    _backup_set_current = None

    def __init__(self, window_main, session_gui, app):
        super(BS, self).__init__(window_main)

        self._window_main = window_main
        self._session_gui = session_gui
        self._backup_sets = session_gui.session.backup_sets
        self._app = app
        self._resizeSignal = QtCore.Signal(QtGui.QResizeEvent)

        self._gui_data_modified_signal = bs.utils.Signal()
        self._gui_data_modified_signal.connect(self._app.idle_1s_timer.start)
        self._gui_data_save_signal = bs.utils.Signal()
        self._gui_data_save_signal.connect(self._save_to_db)
        self._app.idle_1s_timer.timeout.connect(self.gui_data_save_signal.emit)
        self._init_ui()

    def _init_ui(self):
        """ ..

        """
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
    def gui_data_modified_signal(self):
        return self._gui_data_modified_signal

    @gui_data_modified_signal.setter
    def gui_data_modified_signal(self, arg):
        self._gui_data_modified_signal = arg

    @property
    def gui_data_save_signal(self):
        return self._gui_data_save_signal

    @gui_data_save_signal.setter
    def gui_data_save_signal(self, arg):
        self._gui_data_save_signal = arg

    @property
    def resizeSignal(self):
        return self._resizeSignal

    @resizeSignal.setter
    def resizeSignal(self, arg):
        self._resizeSignal = arg

    @property
    def session_gui(self):
        return self._session_gui

    def set_modified(self, force_save=False):
        """ ..

        :param bool force_save: Force the \
        :class:`~bs.ctrl.session.BackupSetCtrl` to be saved into DB if \
        ``True``.

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
        """ ..

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
#        """ ..

#        Saves the state of all currently existing nodes' data (usually only for
#        active set or none if no set active) to backup_set.gui_data.
#        Does not save to db. self.save_gui_data_to_db() does that explicitly.
#        """
#        for node_widget in self._bs_source_widgets + self._bs_filter_widgets + self._bs_target_widgets:
#            node_widget.save_gui_data()
#
#    def save_gui_data_to_db(self):
#        """ ..

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

    def request_exit(self):
        """ ..

        Hook-method called by window manager before changing view.
        Close any view-specific processes here. Events, save set, etc.
        """
        # !!! REQUEST THREAD EXITS !!!
        try:
            if self._backup_set_current:
                self._backup_set_current.save_to_db()
            return True
        except:
            logging.warning("%s: Sets view could not be closed."
                            % (self.__class__.__name__, ))
            return False

    def resizeEvent(self, e):
        """ ..

        :param QtCore.QEvent e:

        Override.
        """
        self.resizeSignal.emit(e)


class BSSetsCanvas(bs.gui.lib.BSCanvas):
    """ ..

    :param bs.gui.view_sets.BS bs:
    :param bs.gui.view_sets.BSMenu menu_sets:
    :param bs.gui.window_main.Application app:

    The canvas gui for the set-management interface.
    """
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
        """ ..

        Re-stacks children in correct order so they don't overlap \
        inappropriately.
        """
        for widget in self.bs_arrow_btn_del_widgets:
            widget.lower()
        for widget in self.bs_arrow_widgets:
            widget.lower()

    def empty_canvas(self):
        """ ..

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
        """ ..

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
        """ ..

        :param bs.ctrl.session.BackupSetCtrl backup_set:

        Loads a :class:`~bs.ctrl.session.BackupSetCtrl` onto the canvas.
        """
        self.close_set()
        # set new current set
        self._bs.backup_set_current = backup_set
        # LOAD NODES
        # Load backup-sources
        for backup_source in backup_set.backup_sources:
            self.add_node(backup_source, backup_set)
        # load backup-filters
        for backup_filter in backup_set.backup_filters:
            self.add_node(backup_filter, backup_set)
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
        """ ..

        :param mixed-type backup_entity: This can be one of the following:

        - :class:`~bs.ctrl.session.BackupSourceCtrl`
        - :class:`~bs.ctrl.session.BackupFilterCtrl`
        - :class:`~bs.ctrl.session.BackupTargetCtrl`
        :param bs.ctrl.session.BackupSetCtrl backup_set:
        :param QtCore.QPoint global_pos:

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
        """ ..

        :param QtCore.QEvent e:

        Override.
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
        """ ..

        :param QtCore.QEvent e:

        Override.
        """
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
    """ ..

    """
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
    """ ..

    """
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
    """ ..

    """
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
    """ ..

    """
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
        """ ..

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
        """ ..

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
        """ ..

        """
        self._x_c = self.x() + self.width() / 2
        self._y_c = self.y() + self.height() / 2

        super(BSMenu, self).mouseMoveEvent(e)

    def resizeEvent(self, e):
        """ ..

        """
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
    """ ..

    """

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
        """ ..

        """
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
        """ ..

        """
        super(BSMenuItem, self).mousePressEvent(e)

        self._bs._bs_sets_canvas.load_set(self._backup_set)


class BSMenuItemBtnDel(bs.gui.lib.BSNodeItemButton):
    """ ..

    """
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
        """ ..

        """
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
    """ ..

    """
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
        """ ..

        :param QtCore.QEvent e:

        Override. Triggers backup_set.save_to_db() and disables this button \
        again.
        """
        super(BSMenuItemSave, self).mousePressEvent(e)

        self._bs.set_modified(force_save=True)


class BSSource(bs.gui.lib.BSNode):
    """ ..

    """
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
        """ ..

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
        """ ..

        """
        super(BSSource, self).remove_node()

        # unregister set-association
        self._backup_entity.backup_entity_ass.pop(self._backup_set)
        # remove from set-ctrl
        self._backup_set.backup_sources.pop(self._backup_set.backup_sources.index(self._backup_entity))
        # remove from canvas
        self._bs_sets_canvas.bs_source_widgets.pop(self._bs_sets_canvas.bs_source_widgets.index(self))
        self.deleteLater()

    def request_exit(self):
        """ ..

        """
        if self._bs_source_item.request_exit():
            return True
        else:
            logging.warning("%s: Could not exit." % (self.__class__.__name__, ))
            return False

    def mousePressEvent(self, e):
        """ ..

        """
        super(BSSource, self).mousePressEvent(e)

        self._mouse_press_event_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        """ ..

        """
        super(BSSource, self).mouseReleaseEvent(e)
        # emit modified-signal, only if mouse has actually moved
        if self._mouse_press_event_pos != e.globalPos():
            self._bs.set_modified()


class BSSourceItem(bs.gui.lib.BSNodeItem):
    """ ..

    """
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
        """ ..

        """
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
        """ ..

        """
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
        """ ..

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
    """ ..

    """
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
        """ ..

        """
        super(BSFilter, self).mousePressEvent(e)

        self._mouse_press_event_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        """ ..

        """
        super(BSFilter, self).mouseReleaseEvent(e)

        # emit modified-signal, only if mouse has actually moved
        if self._mouse_press_event_pos != e.globalPos():
            self._bs.set_modified()

    def save_gui_data(self):
        """ ..

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
        """ ..

        """
        super(BSFilter, self).remove_node()

        # unregister set-association
        self._backup_entity.backup_entity_ass.pop(self._backup_set)
        # remove from set-ctrl
        self._backup_set.backup_filters.pop(self._backup_set.backup_filters.index(self._backup_entity))
        # remove from canvas
        self._bs_sets_canvas.bs_filter_widgets.pop(self._bs_sets_canvas.bs_filter_widgets.index(self))
        self.deleteLater()


class BSFilterItem(bs.gui.lib.BSNodeItem):
    """ ..

    """
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
    """ ..

    """
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
        # targetItems
        for backup_target in self._backup_entity:
            widget = BSTargetItem(self, backup_target)
            self._custom_contents_container._layout.addWidget(widget,
                                   self._custom_contents_container._layout.count(),
                                   0, 1, 1)
        # init backup button
        widget = bs.gui.lib.BSNodeItem(self)
        widget.title_text = "Start Backup..."
        widget.css = ((widget,
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
                     (widget.title,
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
        widget.mousePressEvent = lambda e: self.dispatch_backup_job()
        self._custom_contents_container._layout.addWidget(widget,
                                                          self._custom_contents_container._layout.count(),
                                                          0, 1, 1)
        # css
        self.setStyleSheet("BSTarget {border: 1px solid #%s}" % (bs.config.PALETTE[2], ))
        # title
        self.title_text = "Targets"
        self.title_size = 13
        self.show()

    def dispatch_backup_job(self):
        """ ..

        Dispatches the associated backup-set as a new backup-job to the \
        monitor/queue.
        """
        bm_window = self._bs.session_gui.sessions.window_backup_monitor
        bm_window.show()
        bm_window.view.queues[0].add_backup_job(self._backup_set)

    def mousePressEvent(self, e):
        """ ..

        """
        super(BSTarget, self).mousePressEvent(e)

        self._mouse_press_event_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        """ ..

        """
        super(BSTarget, self).mouseReleaseEvent(e)

        # emit modified-signal, only if mouse has actually moved
        if self._mouse_press_event_pos != e.globalPos():
            self._bs.set_modified()

    def save_gui_data(self):
        """ ..

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
        """ ..

        Override to mute.
        """


class BSTargetItem(bs.gui.lib.BSNodeItem):
    """ ..

    """
    _bs_target = None
    _backup_target = None

    def __init__(self, bs_target, backup_target):
        super(BSTargetItem, self).__init__(bs_target)

        self._bs_target = bs_target
        self._backup_target = backup_target

        self._init_ui()

    def _init_ui(self):
        target_name = self._backup_target.target_name
        target_path = self._backup_target.target_path
        if target_path == "":
            target_path = "Target Offline"
        self.title_text = "%s (%s)" % (target_name,
                                       target_path, )
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
