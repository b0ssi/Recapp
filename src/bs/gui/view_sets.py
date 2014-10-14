#!/usr/bin/python3
# -*- coding: utf-8 -*-


""" ..

"""

from PySide import QtCore, QtGui
import logging
import os

import bs.config
import bs.ctrl.backup
import bs.ctrl.session
import bs.gui.lib


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
        self._menu_sets = BSMenu(self._session_gui.session, self, self._backup_sets)
        self._bs_sets_canvas = BSSetsCanvas(self, self._menu_sets, self._app)

    @property
    def bs_sets_canvas(self):
        """ ..

        """
        return self._bs_sets_canvas

    @property
    def backup_set_current(self):
        """ ..

        """
        return self._backup_set_current

    @backup_set_current.setter
    def backup_set_current(self, backup_set_current):
        """ ..

        """
        if not isinstance(backup_set_current, bs.ctrl.session.BackupSetCtrl):
            logging.warning("%s: The first argument needs to be of type BackupSetCtrl."
                            % (self.__class__.__name__, ))
            return False
        self._backup_set_current = backup_set_current

    @property
    def gui_data_modified_signal(self):
        """ ..

        """
        return self._gui_data_modified_signal

    @gui_data_modified_signal.setter
    def gui_data_modified_signal(self, arg):
        """ ..

        """
        self._gui_data_modified_signal = arg

    @property
    def gui_data_save_signal(self):
        """ ..

        """
        return self._gui_data_save_signal

    @gui_data_save_signal.setter
    def gui_data_save_signal(self, arg):
        """ ..

        """
        self._gui_data_save_signal = arg

    @property
    def resizeSignal(self):
        """ ..

        """
        return self._resizeSignal

    @resizeSignal.setter
    def resizeSignal(self, arg):
        """ ..

        """
        self._resizeSignal = arg

    @property
    def session_gui(self):
        """ ..

        """
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
            for node_widget in (self._bs_sets_canvas.bs_source_widgets +
                                self._bs_sets_canvas.bs_filter_widgets +
                                self._bs_sets_canvas.bs_target_widgets):
                node_widget.save_gui_data()
            # save node data to db
            self._backup_set_current.save_to_db()
            logging.debug("%s: Set %s successfully saved to db."
                          % (self.__class__.__name__,
                             self.backup_set_current, ))

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all \
        children.
        """
        # !!! REQUEST THREAD EXITS !!!
        try:
            if self._backup_set_current:
                self._backup_set_current.save_to_db()
        except:
            logging.warning("%s: Sets view could not be closed."
                            % (self.__class__.__name__, ))
            return False
        # request exit for all children
        for child in self.children():
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        return True

    def resizeEvent(self, e):
        """ ..

        :param QtCore.QEvent e:

        Override.
        """
        self.resizeSignal.emit(e)


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
        """ ..

        """
        super(BSFilter, self).__init__(bs, bs_sets_canvas, app, True)

        self._bs_sets_canvas = bs_sets_canvas
        self._bs = bs
        self._backup_entity = backup_entity
        self._backup_set = backup_set
        self._app = app

        self._init_ui()

        self._backup_entity.update_signal.connect(self._refresh)

    def __del__(self):
        self._backup_entity.update_signal.disconnect(self._refresh)

    @property
    def backup_entity(self):
        """ ..

        """
        return self._backup_entity

    def _init_ui(self):
        """ ..

        """
        self.setMaximumWidth(200)
        self.setMinimumWidth(200)
        # css
        self.css = ((self,
                     ".",
                     "background: #%s; border: 1px solid #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[2], bs.config.PALETTE[2], ),
                        (bs.config.PALETTE[2], bs.config.PALETTE[2], ),
                        (bs.config.PALETTE[2], bs.config.PALETTE[2], ),
                        )
                       },
                      "has_focus":
                      {"enabled":
                       ((bs.config.PALETTE[2], bs.config.PALETTE[9], ),
                        (bs.config.PALETTE[2], bs.config.PALETTE[9], ),
                        (bs.config.PALETTE[2], bs.config.PALETTE[9], ),
                        )
                       }
                      }
                     ),
                    )
        # title
        self.title_size = 13
        self._refresh()
        self.show()

    def _refresh(self):
        """ ..

        Refreshes the ui, (re-)populating it with its rules.
        """
        # title
        if self._backup_entity.backup_filter_rules_mode == self._backup_entity.backup_filter_rules_mode_and:
            modus_subtitle = "Mode: AND"
        elif self._backup_entity.backup_filter_rules_mode == self._backup_entity.backup_filter_rules_mode_or:
            modus_subtitle = "Mode: OR"
        elif self._backup_entity.backup_filter_rules_mode == self._backup_entity.backup_filter_rules_mode_xor:
            modus_subtitle = "Mode: XOR"
        title_text = "%s<br />"\
                     "<span style='font-size: 10px'>%s</span>"\
                     % (self._backup_entity.backup_filter_name,
                        modus_subtitle)
        self._title.setWordWrap(True)
        self._title.mouseMoveEvent = self.mouseMoveEvent  # css seems to override in child: title otherwise
        self.title_text = title_text
        # backup-filter items

        while True:
            child = self._custom_contents_container._layout.takeAt(0)
            if not child:
                break
            child.widget().deleteLater()
        for backup_filter_rule in self._backup_entity.backup_filter_rules:
            widget = BSFilterItem(self._custom_contents_container, backup_filter_rule)
            self._custom_contents_container._layout.addWidget(widget,
                                                              self._custom_contents_container._layout.count(),
                                                              0, 1, 1)
            widget.show()
            # ------------------------------------------------------------------
            # GETTING THE QLabel TO ADJUST IN SIZE **CORRECTLY**
            # The width of the (label-)widget **as it displays** has to be
            # taken and the ``heightForWidth`` be calculated from it and set as
            # minimum/maximum height.
            # ------------------------------------------------------------------
#             w = widget._title.width()
#             h = widget._title.heightForWidth(w)
#             margins_v = widget.layout().contentsMargins().top() + widget.layout().contentsMargins().bottom()
#             widget.setMinimumHeight(h + margins_v)
#             widget.setMaximumHeight(h + margins_v)
            # ------------------------------------------------------------------
        # Here we "pull" the main node widget long enough for everything to fit
        # in, calculating the ``heightForWidth`` for the whole lot.
        w = self.width()
        h = self.heightForWidth(w)

        # if recommended height is > 0 (curiously only, if rule widgets are in layout...)
        if h > 0:
            self.resize(w, h)
        # only adjustSize as this resizes to sizeHint, which would crop widgets
        # in some cases in contrast to resizing to ``widthForHeight``.
        if self._custom_contents_container.layout().count() == 0:
            self.adjustSize()
        # updates layout after resize
        self._custom_contents_container.layout().update()
        self.layout().update()

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
        """ ..

        """
        self.title_text = self._backup_filter_rule
        self._title.mouseMoveEvent = self.mouseMoveEvent
        # CSS
        self.css = ((self,
                     ".",
                     "background: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        )
                       }
                      }
                     ),
                    (self.title,
                     ".",
                     "color: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[3], ),
                        )
                       }
                      }
                     ),
                    )
        self._layout.setContentsMargins(self._layout.contentsMargins().left(),
                                        5,
                                        self._layout.contentsMargins().right(),
                                        5)

    def mouseMoveEvent(self, e):
        """ ..
 
        """
        self.parent().mouseMoveEvent(e)


class BSMenu(bs.gui.lib.BSFrame):
    """ ..

    :type: :class:`bs.gui.lib.BSFrame`

    :param bs.ctrl.session.Session backup_session:

    :param bs.gui.view_sets.BS bs:

    :param bs.ctrl.session.BackupSetsCtrl backup_sets:

    """
#     _x_c = None
#     _y_c = None
    _btn_save = None

    def __init__(self, backup_session, bs, backup_sets):
        super(BSMenu, self).__init__(bs)

        self._backup_session = backup_session
        self._bs = bs
        self._backup_sets = backup_sets

        self.parent().resizeSignal.connect(self.resizeEvent)

        self._init_ui()

    def _init_ui(self):
        # layout
        self._layout = QtGui.QGridLayout(self)
        self._layout.setSpacing(1)
        # these MUST be floats!
        self._x_c = float(0.0)
        self._y_c = float(0.0)
        # Drop shadow
        gfx = QtGui.QGraphicsDropShadowEffect(self)
        gfx.setOffset(0)
        gfx.setColor(QtGui.QColor(20, 20, 20))
        gfx.setBlurRadius(4)
        self.setGraphicsEffect(gfx)
        # populate
        self.refresh()

    def refresh(self):
        """ ..

        Populates the menu with BSNodeItems.
        To be called when initially populating the menu or updating after a
        backup-set has been added or deleted.
        """
        # delete old widgets
        while True:
            item = self._layout.takeAt(0)
            if not item:
                break
            item.widget().deleteLater()
        # re-populate with widgets
        # title
        title = QtGui.QLabel("Backup Sets")
        title.setStyleSheet("font-size: 18px")
        self._layout.addWidget(title, 0, 0, 1, 1)
        title.show()
        # set buttons
        for backup_set in self._backup_sets.sets:
            widget = BSMenuItem(self, backup_set, self._bs, self._backup_sets)
            self._layout.addWidget(widget, self._layout.count(), 0, 1, 1)
            widget.show()
        # add button
        btn_add = BSMenuItemAdd(self._backup_session, self)
        self._layout.addWidget(btn_add, self._layout.count(), 0, 1, 1)
        btn_add.show()
        # spacer widget
        # (setRowMinimumHeight didn't scale down to the minimum set when
        # removing buttons again, resulting in an increasingly stretched menu)
        widget = QtGui.QWidget(self)
        widget.setFixedHeight(10)
        self._layout.addWidget(widget, self._layout.count(), 0, 1, 1)
        widget.show()
        # save button
        btn_save = BSMenuItemSave(self, self._bs)
        self._layout.addWidget(btn_save, self._layout.count(), 0, 1, 1)
        btn_save.show()
        # refresh height
        self.resize(self.sizeHint())
        # geometry
#         self._x_c = self.x() + self.width() / 2
#         self._y_c = self.y() + self.height() / 2

    @property
    def backup_sets(self):
        """ ..

        :rtype: :class:`bs.ctrl.session.BackupSetsCtrl`

        The :class:`bs.ctrl.session.BackupSetsCtrl` in use by the corresponding
        session.
        """
        return self._backup_sets

#     def mouseMoveEvent(self, e):
#         """ ..
#
#         """
#         self._x_c = self.x() + self.width() / 2
#         self._y_c = self.y() + self.height() / 2
#
#         super(BSMenu, self).mouseMoveEvent(e)

    def resizeEvent(self, e):
        """ ..

        """
        y = (self.parent().height() - self.height()) / 2
        self.move(10, y)

#         if e.oldSize().width() > 0:
#             x = self._x_c - self.width() / 2
# #             y = self._y_c - self.height() / 2
#             scale_factor_x = (e.size().width() / e.oldSize().width())
#             scale_factor_y = (e.size().height() / e.oldSize().height())
#             delta_y = e.size().height() - e.oldSize().height()
#             # x
#             if self.x() >= 0:
#                 x_new = x * scale_factor_x
#             else:
#                 x_new = x
#             # y
#             if self._y_c < 0:
#                 y_new = self._y_c - self.height() / 2
#             elif self._y_c > e.size().height():
#                 y_new = self._y_c - self.height() / 2 + delta_y
#             else:
#                 y_new = self._y_c * scale_factor_y - self.height() / 2
#             self.setGeometry(x_new,
#                              y_new,
#                              self.width(),
#                              self.height())
#             self._x_c = x_new + self.width() / 2
#             self._y_c = y_new + self.height() / 2

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
        btn_del = BSMenuItemBtnDel(self._bs_menu,
                                   self,
                                   "DEL",
                                   self._backup_set,
                                   self._backup_sets,
                                   self._bs)
        self._layout.addWidget(btn_del, 0, 1, 1, 1)
        # CSS
        self.css = ((self,
                     "",
                     "background: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[0], ),
                        (bs.config.PALETTE[0], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[0], ),
                        (bs.config.PALETTE[0], ),
                        (bs.config.PALETTE[0], ),
                        ),
                       }
                      }
                     ),
                    (self.title,
                     "",
                     "color: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        ),
                       }
                      }
                     ),
                    )

    def mousePressEvent(self, e):
        """ ..

        """
        super(BSMenuItem, self).mousePressEvent(e)

        self._bs._bs_sets_canvas.load_set(self._backup_set)


class BSMenuItemAdd(bs.gui.lib.BSNodeItem):
    """ ..

    :param bs.ctrl.session.Session backup_session:

    :param bs.gui.view_sets.BSMenu bs_menu: The menu that hosts this button.

    This class represents the single button to be used in
    :class:`bs.gui.view_sets.BSMenu` that adds a new backup-set.
    """
    def __init__(self, backup_session, bs_menu):
        """ ..
        """
        super(BSMenuItemAdd, self).__init__(bs_menu)

        self._backup_session = backup_session
        self._bs_menu = bs_menu

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        # title
        self.title_text = "Add Set"
        # CSS
        self.css = ((self,
                     "",
                     "background: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[8], ),
                        (bs.config.PALETTE[7], ),
                        (bs.config.PALETTE[7], ),
                        ),
                       }
                      }
                     ),
                    (self.title,
                     "",
                     "color: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        ),
                       }
                      }
                     ),
                    )

    def mouseReleaseEvent(self, e):
        """ ..

        :param PySide.QtGui.QMouseEvent e:
        :rtype: *void*

        Override. Creates and adds a new backup-set when clicked.
        """
        super(BSMenuItemAdd, self).mouseReleaseEvent(e)

        # launch dialog to enter details and create backup-set
        BSMenuItemAddDialog(self._backup_session)
        # refresh menu
        self._bs_menu.refresh()


class BSMenuItemAddDialog(QtGui.QDialog):
    """ ..

    :param bs.ctrl.session.Session backup_session: The\
    :class:`bs.ctrl.session.Session` of the current session.

    This is the dialog window where particulars about the backup-set to be
    added are specified.
    """
    _input_name = None
    _input_name_title = None
    _inpub_db_path = None
    _input_db_path_title = None
    _input_pw = None
    _input_pw_title = None

    def __init__(self, backup_session):
        """ ..
        """
        super(BSMenuItemAddDialog, self).__init__()

        self._backup_session = backup_session
        self._backup_sets = backup_session.backup_sets

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        layout = QtGui.QGridLayout(self)
        # title
        self.setWindowTitle("Add new Backup-Set")
        # set name
        self._input_name_title = QtGui.QLabel("Please specify a name for the "
                                              "new Backup-Set:")
        layout.addWidget(self._input_name_title, 0, 0, 1, 3)
        self._input_name = QtGui.QLineEdit()
        layout.addWidget(self._input_name, 1, 0, 1, 3)
        # set db path
        self._input_db_path_title = QtGui.QLabel("Please specify a path where "
                                                 "the Backup-Set's database "
                                                 "will be stored:")
        layout.addWidget(self._input_db_path_title, 2, 0, 1, 3)
        self._input_db_path = QtGui.QLineEdit()
        layout.addWidget(self._input_db_path, 3, 0, 1, 3)
        # set filter
        self._input_target_title = QtGui.QLabel("Please select the targets "
                                                "you wish to add to the new "
                                                "set.")
        layout.addWidget(self._input_target_title, 4, 0, 1, 3)
        self._input_target = QtGui.QListWidget(self)
        self._input_target.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        for backup_target in self._backup_session.backup_targets.targets:
            item = QtGui.QListWidgetItem(backup_target.target_name)
            item.backup_target = backup_target
            self._input_target.addItem(item)
        layout.addWidget(self._input_target, 5, 0, 1, 3)
        # set pw
        self._input_pw_title = QtGui.QLabel("Please specify a password:")
        layout.addWidget(self._input_pw_title, 6, 0, 1, 3)
        self._input_pw = QtGui.QLineEdit()
        self._input_pw.setEchoMode(QtGui.QLineEdit.Password)
        layout.addWidget(self._input_pw, 7, 0, 1, 3)
        # add button
        btn_add = QtGui.QPushButton("&Add")
        btn_add.clicked.connect(self._submit)
        layout.addWidget(btn_add, 8, 1, 1, 1)
        # cancel button
        btn_cancel = QtGui.QPushButton("&Cancel")
        btn_cancel.clicked.connect(self.close)
        layout.addWidget(btn_cancel, 8, 2, 1, 1)
        self.exec_()

    def _submit(self):
        """ ..
        :rtype: `void`

        Verifies entered data by attempting to add the backup-set.
        """
        try:
            backup_targets = [x.backup_target for x in self._input_target.selectedItems()]
            self._backup_sets.create_backup_set(self._input_name.text(),
                                                self._input_pw.text(),
                                                self._input_db_path.text(),
                                                [],
                                                [],
                                                backup_targets
                                                )
            # close
            self.close()
        except Exception as e:
            err = ""
            # set_name
            if not e.args[0][0]:
                self._input_name_title.setStyleSheet("color: red")
                err += "- %s\n" % e.args[0][1]
            else:
                self._input_name_title.setStyleSheet("")
            # key_raw
            if not e.args[1][0]:
                self._input_pw_title.setStyleSheet("color: red")
                err += "- %s\n" % e.args[1][1]
            else:
                self._input_pw_title.setStyleSheet("")
            # db_path
            if not e.args[2][0]:
                self._input_db_path_title.setStyleSheet("color: red")
                err += "- %s\n" % e.args[2][1]
            else:
                self._input_db_path_title.setStyleSheet("")
            # target_objs
            if not e.args[3][0]:
                self._input_target_title.setStyleSheet("color: red")
                err += "- %s\n" % e.args[3][1]
            else:
                self._input_target_title.setStyleSheet("")
            # prompt error dialog
            if err != "":
                msg_box = QtGui.QMessageBox()
                msg_box.setWindowTitle("Validation error")
                msg_box.setText("%s's a bit picky, sorry." % bs.config.PROJECT_NAME)
                msg_box.setInformativeText(err)
                msg_box.show()

    def closeEvent(self, e):
        """ ..

        Override.
        """
        self.deleteLater()


class BSMenuItemBtnDel(bs.gui.lib.BSNodeItemButton):
    """ ..

    """
    _title = None
    _bs_menu = None
    _bs_menu_item = None
    _backup_set = None
    _backup_sets = None
    _bs = None

    def __init__(self, bs_menu, bs_menu_item, title, backup_set, backup_sets,
                 bs):
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
                                          "<p>Are you sure you wish to "
                                          "delete Backup-Set <b>%s</b>?</p>"
                                          "<p>The Backup-Sources, -Filters "
                                          "and -Targets contained in the "
                                          "Backup-Set will not be deleted.</p>"
                                          % (self._backup_set.set_name, ))
        msg_box.addButton(msg_box.Cancel)
        msg_box_ok = msg_box.addButton(msg_box.Ok)
        msg_box.exec_()
        if msg_box.clickedButton() == msg_box_ok:
            self._backup_sets.delete_backup_set(self._backup_set)
            # empty the canvas if set to be deleted is currently loaded set
            if self._backup_set == self._bs.backup_set_current:
                self._bs.bs_sets_canvas.close_set()
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
        """ ..

        """
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
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[8], ),
                        (bs.config.PALETTE[7], ),
                        (bs.config.PALETTE[7], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        ),
                       }
                      }
                     ),
                    (self.title,
                     "",
                     "color: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[6], ),
                        (bs.config.PALETTE[6], ),
                        (bs.config.PALETTE[6], ),
                        ),
                       }
                      }
                     ),
                    )

    def setEnabled(self, *args, **kwargs):
        """ ..

        """
        super(BSMenuItemSave, self).setEnabled(*args, **kwargs)

        self.title_text = "SAVE"

    def setDisabled(self, *args, **kwargs):
        """ ..

        """
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
        """ ..

        """
        super(BSSetsCMenuAction, self).__init__(name, parent)

        self._bs_sets_canvas = bs_sets_canvas
        self._backup_entity = backup_entity
        self._backup_set_current = backup_set_current
        self._c_menu_main_global_pos = c_menu_main_global_pos

        self._init_ui()

    def _init_ui(self):
        """ ..

        """
        self.triggered.connect(self.fire)

    def fire(self):
        """ ..

        """
        self._bs_sets_canvas.add_node(self._backup_entity,
                                      self._backup_set_current,
                                      self._c_menu_main_global_pos)


class BSSetsCMenuSub(QtGui.QMenu):
    """ ..

    """
    # this is the list of entities (backup_sources/backup_filters) for the
    # entire session self._bs.backup_set_current.backup_sources
    _backup_entities_session = None
    # this is the list of entities (backup_sources/backup_filters) for the
    # entire session self._bs.backup_set_current.backup_sources
    _backup_entities_set = None
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
        sources_unused = [x for x in self._backup_entities_session if
                          x not in self._backup_entities_set]
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
    # This is where the temporary arrow's carrier is held when interactively
    # connecting nodes. Initialized on node's connectins socket
    _bs_arrow_carrier = None
    _mouse_press_global_pos = None

    def __init__(self, bs, menu_sets, app):
        """ ..

        """
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
        """ ..

        """
        return self._bs_source_widgets

    @property
    def bs_filter_widgets(self):
        """ ..

        """
        return self._bs_filter_widgets

    @property
    def bs_target_widgets(self):
        """ ..

        """
        return self._bs_target_widgets

    @property
    def bs_arrow_widgets(self):
        """ ..

        """
        return self._bs_arrow_widgets

    @property
    def bs_arrow_btn_del_widgets(self):
        """ ..

        """
        return [x for x in self.children()
                if isinstance(x, bs.gui.lib.BSArrowBtnDel)]

    def _init_ui(self):
        """ ..

        """
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

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
            # add entity on ctrl level
            backup_set.add_backup_source(backup_entity)
            # add widget
            widget = BSSource(self, self._bs, backup_entity, backup_set,
                              self._app)
            self._bs_source_widgets.append(widget)
        elif isinstance(backup_entity, bs.ctrl.session.BackupFilterCtrl):
            # add entity on ctrl level
            backup_set.add_backup_filter(backup_entity)
            # add widget
            widget = BSFilter(self, self._bs, backup_entity, backup_set,
                              self._app)
            self._bs_filter_widgets.append(widget)
        elif (isinstance(backup_entity, list) and
                isinstance(backup_entity[0],
                           bs.ctrl.session.BackupTargetCtrl)):
            widget = BSTarget(self, self._bs, backup_entity, backup_set,
                              self._app)
            self._bs_target_widgets.append(widget)
        # set position
        if global_pos:
            widget.setGeometry(self.mapFromGlobal(global_pos).x(),
                               self.mapFromGlobal(global_pos).y(),
                               widget.width(),
                               widget.height())
        self._bs.set_modified()

    def close_set(self):
        """ ..

        :rtype: *bool*

        Closes the current backup-set GUI on the canvas.
        """
        # save current set
        self._bs.set_modified(force_save=True)
        # EMPTY CANVAS
        # clean canvas, delete old widgets
        if not self.empty_canvas():
            logging.warning("%s: Canvas could not be emptied."
                            % (self.__class__.__name__, ))
            return False
        # arrow_carrier
        self._bs_arrow_carrier = bs.gui.lib.BSArrowCarrier(self,
                                                           self._app,
                                                           self._bs)
        return True

    def empty_canvas(self):
        """ ..

        :rtype: *bool*

        Empties the canvas, removing/deleting all loaded widgets and arrows.
        Be aware that this deletes the arrow-carrier-widget as well.
        :meth:`close_set` should be used in most cases.
        """
        # request exit for all children
        for child in self.children():
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        # delete child-widgets
        for bs_source_widget in self._bs_source_widgets:
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

    def load_set(self, backup_set):
        """ ..

        :param bs.ctrl.session.BackupSetCtrl backup_set:
        :rtype: *boolean*

        Loads a :class:`~bs.ctrl.session.BackupSetCtrl` onto the canvas.
        """
        # Check for database existence
        try:
            backup_set.set_db_path
        except IOError as e:
            out = "The set database could not be found at location %s (%s)." \
                  % (os.path.realpath(e.filename), e.strerror, )
            msg_window = QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error",
                                           out)
            msg_window.exec_()
            return False
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
                bs.gui.lib.BSArrow(self._bs, bs_source_widget,
                                   self._bs_target_widgets[0])
            for bs_filter_widget in self._bs_filter_widgets:
                backup_entity = bs_filter_widget.backup_entity
                if backup_entity in backup_entity_ass:
                    # we have source and filter widget now. Connect!
                    bs.gui.lib.BSArrow(self._bs, bs_source_widget,
                                       bs_filter_widget)
        # filters - filters/targets
        for bs_filter_widget_a in self._bs_filter_widgets:
            backup_filter_a = bs_filter_widget_a.backup_entity
            backup_filter_a_ass = backup_filter_a.backup_entity_ass[self._bs.backup_set_current]
            if backup_set.backup_targets in backup_filter_a_ass:
                bs.gui.lib.BSArrow(self._bs, bs_filter_widget_a,
                                   self._bs_target_widgets[0])
            for bs_filter_widget_b in self._bs_filter_widgets:
                backup_filter_b = bs_filter_widget_b.backup_entity
                if (backup_filter_b in backup_filter_a_ass and
                        backup_filter_b != backup_filter_a):
                    # we have both associated filters now. Connect!
                    bs.gui.lib.BSArrow(self._bs, bs_filter_widget_a,
                                       bs_filter_widget_b)
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
        return True

    def restack(self):
        """ ..

        Re-stacks children in correct order so they don't overlap
        inappropriately.
        """
        for widget in self.bs_arrow_btn_del_widgets:
            widget.lower()
        for widget in self.bs_arrow_widgets:
            widget.lower()

    def request_exit(self):
        """ ..

        :rtype: *boolean*

        Executes exit calls to related objects and forwards request to all
        children.
        """
        # request exit for all children
        for child in self.children():
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        return True

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

        super(BSSetsCanvas, self).keyPressEvent(e)

    def mousePressEvent(self, e):
        """ ..

        """
        self._mouse_press_global_pos = e.globalPos()

        super(BSSetsCanvas, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ ..

        :param QtCore.QEvent e:

        Override.
        """
        if (e.globalPos() == self._mouse_press_global_pos and
                e.button() & QtCore.Qt.MouseButton.RightButton and
                self._bs.backup_set_current):
            # Main context menu
            menu_main = BSSetsCMenu(self, self._bs.backup_set_current, e.globalPos())
            menu_main.popup(e.globalPos())
        else:
            super(BSSetsCanvas, self).mouseReleaseEvent(e)


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
        """ ..

        """
        super(BSSource, self).__init__(bs, bs_sets_canvas, app, True)

        self._bs_sets_canvas = bs_sets_canvas
        self._bs = bs
        self._backup_entity = backup_source
        self._backup_set = backup_set
        self._app = app

        self._init_ui()

    @property
    def backup_entity(self):
        """ ..

        """
        return self._backup_entity

    def _init_ui(self):
        """ ..

        """
        # CSS
        self.css = ((self,
                     ".",
                     "background: #%s; border: 1px solid #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[8], bs.config.PALETTE[8], ),
                        (bs.config.PALETTE[8], bs.config.PALETTE[8], ),
                        (bs.config.PALETTE[8], bs.config.PALETTE[8], ),
                        )
                       },
                      "has_focus":
                      {"enabled":
                       ((bs.config.PALETTE[8], bs.config.PALETTE[9], ),
                        (bs.config.PALETTE[8], bs.config.PALETTE[9], ),
                        (bs.config.PALETTE[8], bs.config.PALETTE[9], ),
                        )
                       }
                      }
                     ),
                    )
        # title
        self.title_text = self._backup_entity.source_name
        self.title_size = 13
        # populate with item
        self._bs_source_item = BSSourceItem(self,
                                            self._backup_entity,
                                            self._backup_set)
        self._custom_contents_container._layout.addWidget(self._bs_source_item,
                                                          self._layout.count(),
                                                          0, 1, 1)
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
        # remove backup-ctrl
        self._backup_set.backup_ctrls.pop(self.backup_entity)
        # remove from canvas
        self._bs_sets_canvas.bs_source_widgets.pop(self._bs_sets_canvas.bs_source_widgets.index(self))
        self.deleteLater()

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all \
        children.
        """
        # request exit for all children
        for child in self.children():
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        return True

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

    :param bs.gui.view_sets.BSSource bs_source:
    :param bs.ctrl.session.BackupSourceCtrl backup_source:
    :param bs.ctrl.session.BackupSetCtrl backup_set:

    The sub-widget on the :class:`~bs.gui.view_sets.BSSource` that display
    extra information about the :class:`~bs.gui.view_sets.BSSource` widget.
    """
    _bs_source = None
    _backup_ctrl = None
    _backup_entity = None
    _backup_set = None

    _update_thread = None
    _update_worker = None

    _finished_signal = QtCore.Signal(bs.ctrl.backup.BackupUpdateEvent)
    _updated_signal = QtCore.Signal(bs.ctrl.backup.BackupUpdateEvent)

    def __init__(self, bs_source, backup_source, backup_set):
        """ ..

        """
        super(BSSourceItem, self).__init__(bs_source)

        self._bs_source = bs_source
        self._backup_entity = backup_source
        self._backup_set = backup_set
        self._backup_ctrl = self._backup_set.backup_ctrls[self._backup_entity]

#         self._backup_ctrl.finished_signal.connect(self._finished_signal.emit)
#         self._backup_ctrl.updated_signal.connect(self._updated_signal.emit)
#         self._updated_signal.connect(self.update_ui,
#                                      QtCore.Qt.QueuedConnection)
#         self._finished_signal.connect(self.update_ui,
#                                       QtCore.Qt.QueuedConnection)
#         self._finished_signal.connect(self.setEnabled,
#                                       QtCore.Qt.QueuedConnection)

        self._init_ui()

    def _init_ui(self):
        """ ..

        """
        self.title_text = "Calculate Pending Data"
        # CSS
        self.css = ((self,
                     ".",
                     "background: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[0], ),
                        (bs.config.PALETTE[1], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        ),
                       }
                      }
                     ),
                    (self.title,
                     "",
                     "color: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[3], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[3], ),
                        ),
                       }
                      }
                     ),
                    )

    def deleteLater(self):
        """ ..

        Override.
        """
#         self._backup_ctrl.finished_signal.disconnect(self._finished_signal.emit)
#         self._backup_ctrl.updated_signal.disconnect(self._updated_signal.emit)
#         self._updated_signal.disconnect(self.update_ui)
#         self._finished_signal.disconnect(self.update_ui)
#         self._finished_signal.disconnect(self.setEnabled)

        super(BSSourceItem, self).deleteLater()

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all
        children.
        """
        # request exit for all children
        for child in self.children():
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        return True

    def setEnabled(self, f=True):
        """ ..

        Override, to enable parameterless referencing by signals.
        """
        if not isinstance(f, bool):
            f = True
        super(BSSourceItem, self).setEnabled(f)

    def update(self):
        """ ..

        :rtype: *bool*

        Updates the data displayed in the GUI, executing a pre-process on the
        backup controller to accumulate # of files and -bytes that are due
        to be backed up.
        """
        backup_ctrl = self._backup_set.backup_ctrls[self._backup_entity]

        worker = backup_ctrl.simulate()[0]
        self.setDisabled(True)
        worker.start()
        return True

    def update_ui(self, e):
        """ ..

        :param bs.ctrl.backup.BackupUpdateEvent e:
        """
        if e.byte_count_total and e.file_count_total:
            self.title_text = "%s | %s files"\
                              % (bs.utils.format_data_size(e.byte_count_total),
                                 e.file_count_total, )

    def mouseReleaseEvent(self, e):
        """ ..

        :rtype: *void*
        :param QtCore.QEvent e:

        Override. Opens a password prompt if the backup-set is encrypted.
        """
        # if backup_set is encrypted, prompt for key
        if self._backup_set.salt_dk:
            err_msg = "The Backup-Set seems to be encrypted. Please enter password:"
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
            self.update()


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
        """ ..

        """
        return self._backup_entity

    def _init_ui(self):
        """ ..

        """
        # targetItems
        for backup_target in self._backup_entity:
            widget = BSTargetItem(self, backup_target)
            self._custom_contents_container._layout.addWidget(widget,
                                                              self._custom_contents_container._layout.count(),
                                                              0, 1, 1)
        # init backup button
        widget = BSTargetItemDispatch(self, self._bs, self._backup_set)
        self._custom_contents_container._layout.addWidget(widget,
                                                          self._custom_contents_container._layout.count(),
                                                          0, 1, 1)
        # css
        self.css = ((self,
                     ".",
                     "background: #%s; border: 1px solid #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[4], bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], bs.config.PALETTE[4], ),
                        )
                       },
                      "has_focus":
                      {"enabled":
                       ((bs.config.PALETTE[4], bs.config.PALETTE[9], ),
                        (bs.config.PALETTE[4], bs.config.PALETTE[9], ),
                        (bs.config.PALETTE[4], bs.config.PALETTE[9], ),
                        )
                       }
                      }
                     ),
                    )
        # title
        self.title_text = "Targets"
        self.title_size = 13
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
        """ ..

        """
        self.setMaximumWidth(200)
        self.setMinimumWidth(200)

        target_name = self._backup_target.target_name
        target_path = self._backup_target.target_path
        if target_path == "":
            target_path = "Target Offline"
        self.title_text = "%s (%s)" % (target_name,
                                       target_path, )
        # CSS
        self.css = ((self,
                     ".",
                     "background: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[1], ),
                        ),
                       }
                      }
                     ),
                    (self.title,
                     "",
                     "color: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[3], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[3], ),
                        ),
                       }
                      }
                     ),
                    )
        # progress-bar
        self._layout.addWidget(bs.gui.lib.BSNodeItemVProgressBar(self), 0, 1, 1, 1)

    def mouseMoveEvent(self, e):
        """ ..

        Override to capture mouse-drag on this child-widget as well.
        """
        self.parent().mouseMoveEvent(e)


class BSTargetItemDispatch(bs.gui.lib.BSNodeItem):
    """ ..

    :param QtGui.QWidget parent:
    :param bs.gui.view_sets.BS bs:
    :param bs.ctrl.session.BackupSetCtrl backup_set:

    This is the backup-job-dispatch button on the target widget that submits
    the *backup-set* to the *backup-monitor* for execution.
    """

    _bs = None
    _backup_set = None

    _password_prompt = None

    def __init__(self, parent, bs, backup_set):
        super(BSTargetItemDispatch, self).__init__(parent)

        self._bs = bs
        self._backup_set = backup_set

        self._init_ui()

    def _check_authentication(self):
        """ ..

        Checks if backup-set is authenticated and opens a password prompt if
        not. Dispatches the job to the queue on success.
        """
        def _dispatch_backup_job():
            """ ..

            :rtype: *void*

            Prompts for the password if *backup-set* is encrypted and
            dispatches it as a new *backup-job* to the *backup-monitor*'s queue
            for execution.
            """
            bm_window = self._bs.session_gui.sessions.window_backup_monitor
            bs.gui.window_backup_monitor.WindowDispatchCheck(self._backup_set,
                                                             bm_window)

        if (self._backup_set.salt_dk and not self._backup_set.is_authenticated):
            self._password_prompt = PasswordPromptView(self._backup_set.authenticate,
                                                       self._check_authentication)
        else:
            _dispatch_backup_job()

    def _init_ui(self):
        """ ..

        """
        self.title_text = "Start Backup..."
        self.css = ((self,
                     "",
                     "background: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[1], ),
                        (bs.config.PALETTE[0], ),
                        (bs.config.PALETTE[0], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[0], ),
                        (bs.config.PALETTE[0], ),
                        (bs.config.PALETTE[0], ),
                        ),
                       }
                      }
                     ),
                    (self.title,
                     "",
                     "color: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[3], ),
                        (bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        ),
                       "disabled":
                       ((bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        ),
                       }
                      }
                     ),
                    )

    def mousePressEvent(self, e):
        """ ..

        :param QtCore.QEvent e:
        :rtype: *void*

        Override. Calls :meth:`dispatch_backup_job`.
        """
        self._check_authentication()


class PasswordPromptView(QtGui.QDialog):
    """ ..

    :param method auth_method: The function/method to be called by the\
    implemented thread to verify the password and authenticate.

    :param method callback: The callback to be invoked on success.

    This password-prompt window implements a threaded authentication
    mechanic, visual progress feedback and a ``callback`` to be invoked on
    success.
    """
    _auth_method = None
    _callback = None

    _stacked_layout = None
    _widget_pw_input = None
    _widget_pw_verify = None

    def __init__(self, auth_method, callback):
        """ ..

        """
        super(PasswordPromptView, self).__init__()

        self._auth_method = auth_method
        self._callback = callback

        self._init_ui()

    def _init_ui(self):
        """ ..

        """
        self.setWindowTitle("Backup-Set Authentication")
        self._stacked_layout = QtGui.QStackedLayout(self)
        # BUILD VIEWS
        # pw input
        self._widget_pw_input = QtGui.QWidget()
        self._stacked_layout.addWidget(self._widget_pw_input)
        layout = QtGui.QGridLayout(self._widget_pw_input)
        msg = "The Backup-Set appears to be encrypted. Please enter the password:"
        layout.addWidget(QtGui.QLabel(msg), 0, 0, 1, 2)
        line_edit = QtGui.QLineEdit()
        line_edit.setEchoMode(line_edit.Password)
        layout.addWidget(line_edit, 1, 0, 1, 2)
        btn_ok = QtGui.QPushButton("OK")
        layout.addWidget(btn_ok, 2, 0, 1, 1)
        btn_ok.clicked.connect(lambda: self._stacked_layout.setCurrentWidget(self._widget_pw_verify))
        btn_ok.clicked.connect(lambda: self._verify_pw(line_edit.text()))

        btn_cancel = QtGui.QPushButton("Cancel")
        layout.addWidget(btn_cancel, 2, 1, 1, 1)
        btn_cancel.clicked.connect(self.close)
        # pw verify
        self._widget_pw_verify = QtGui.QWidget()
        self._stacked_layout.addWidget(self._widget_pw_verify)
        layout = QtGui.QGridLayout(self._widget_pw_verify)
        msg = "Verifying password, please wait..."
        layout.addWidget(QtGui.QLabel(msg), 0, 0, 1, 1)

        # activate input view
        self._stacked_layout.setCurrentWidget(self._widget_pw_input)

        self.exec_()

    def _verify_pw(self, key_raw):
        """ ..

        """
        verification_worker = self._auth_method(key_raw)
        verification_worker.finished.connect(self.close,
                                             QtCore.Qt.QueuedConnection)
        verification_worker.finished.connect(self._callback,
                                             QtCore.Qt.QueuedConnection)
        verification_worker.start()

    def closeEvent(self, e):
        """ ..

        Override.
        """
        self.deleteLater()
