# -*- coding: utf-8 -*-

###############################################################################
##    bs.ui.main_window                                                      ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  May 13, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################

""" * """

from PySide import QtCore, QtGui
from bs.gui.window_about import WindowAbout
import bs.config
import bs.gui.view_login
import bs.gui.view_sets
import bs.gui.window_about
import logging
import time


class WindowMain(QtGui.QMainWindow):
    """ * """
    _default_width = 640
    _default_height = 480
    _menu_bar = None
    _sessions = None
    _session_gui = None
    # references to all other windows. They are most likely initialized in
    # other classes but all referenced here for easy access
    _window_about = None
    _layout = None

    def __init__(self, sessions, session_gui):
        super(WindowMain, self).__init__()

        self._sessions = sessions
        self._session_gui = session_gui
        self._init_ui()

    @property
    def window_about(self):
        return self._window_about

    @window_about.setter
    def window_about(self, arg):
        if isinstance(arg, bs.gui.window_about.WindowAbout):
            self._window_about = arg
        else:
            logging.warning("%s: The first argument needs to be of type `WindowAbout`"
                            % (self.__class__.__name__, ))

    def keyPressEvent(self, e):
        """ * """
        if isinstance(e, QtGui.QKeyEvent):
            # Ctrl + O
            if e.key() == QtCore.Qt.Key_O and (e.modifiers() & QtCore.Qt.ControlModifier):
                print("Nothing to open!")

    def _init_ui(self):
        """ * """
        # set pos
        screen_prim_res = self._sessions.app.desktop().availableGeometry(screen=0)
        self.setGeometry(screen_prim_res.width() / 2 - self._default_width / 2,
                         screen_prim_res.height() / 2 - self._default_height / 2,
                         self._default_width,
                         self._default_height
                         )
        # menu bar
        self._menu_bar = WindowMainMenu(self._sessions, self._session_gui, self)
        self.setMenuWidget(self._menu_bar)
        # status bar
        self.statusBar().showMessage("Welcome to %s!"
                                     % (bs.config.PROJECT_NAME, ))
        self.statusBar().setDisabled(True)
        self.setWindowTitle("%s" % (bs.config.PROJECT_NAME, ))
        # central widget layout
        widget = QtGui.QWidget()
        self._layout = QtGui.QGridLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(widget)
        widget.setLayout(self._layout)
        # set initial view
        self.set_view('login')
        self.show()

#    def paintEvent(self, pe):
#        tile = QtGui.QPixmap("x.png")
#        painter = QtGui.QPainter(self)
#        painter.drawTiledPixmap(self.rect(), tile)
#        super(WindowMain, self).paintEvent(pe)

    def set_view(self, view):
        """ *
        Sets the main view to `String view`.
        String view        'login'
        """
        # clear layout
        for i in range(self._layout.count()):
            self._layout.itemAt(i).widget().deleteLater()
        if view == "login":
            # ui: set
            widget = bs.gui.view_login.ViewLogin(self._sessions,
                                                 self._session_gui)
            self._layout.addWidget(widget, 0, 0, 1, 1)
            widget.view_login_form.input_username.setFocus()
        elif view == "x":
            widget = bs.gui.view_sets.ViewSets(self._session_gui)
            self._layout.addWidget(widget, 0, 0, 1, 1)
            widget.sets_list.setFocus()

        # update menu
        self._menu_bar.update()

    def lock(self):
        """ *
        Locks the current session, returning the user back to the login-view.
        Keeps any active processes running.
        """
        # log-out user
        self._session_gui.session.lock()
        # detach session from GUI
        self._session_gui.session = None
        # return to login-view
        self._session_gui.main_window.set_view("login")

    def log_out(self):
        """ *
        Logs out of the session, returning the user back to the login-view.
        Cancels any operations if there are any running or prevents the user
        from logging out if so.
        """
        # check for any active processes
        # ...
        # log-out user
        self._session_gui.session.log_out()
        # detach session from GUI
        self._session_gui.session = None
        # return to login-view
        self._session_gui.main_window.set_view("login")

    def exit(self):
        """ *
        Exits the application.
        """
        self._sessions.app.exit()

    def closeEvent(self, e):
        """ * """
        # log-out session
        if self._session_gui.session:
            self._session_gui.session.log_out()
        # remove reference from _guis list
        self._sessions.remove_session_gui(self._session_gui)


class WindowMainMenu(QtGui.QMenuBar):
    """ * """
    _main_window = None
    _menu_file = None
    _menu_user = None
    _sessions = None
    _session_gui = None

    def __init__(self, sessions, session_gui, main_window):
        super(WindowMainMenu, self).__init__()

        self._main_window = main_window
        self._sessions = sessions
        self._session_gui = session_gui

        self._menu_file = WindowMainMenuFile(self, self._sessions, self._main_window)
        self._menu_user = WindowMainMenuUser(self, self._session_gui)
        self._init_ui()

    @property
    def menu_file(self):
        return self._menu_file

    @property
    def menu_user(self):
        return self._menu_user

    def _init_ui(self):
        """ * """
        menu_help = QtGui.QMenu("&?", self)
        menu_help_about = QtGui.QAction("&About %s"
                                        % (bs.config.PROJECT_NAME, ),
                                        menu_help)
        menu_help_about.setShortcut("F1")
        menu_help_about.triggered.connect(self._show_window_about)
        menu_help.addAction(menu_help_about)

        menu_dev = QtGui.QMenu("&Dev", self)
        menu_dev_action0 = QtGui.QAction("Action&0", menu_dev)
        menu_dev_action0.setShortcut("F9")
        menu_dev_action0.triggered.connect(lambda: print(self._sessions.guis))
        menu_dev.addAction(menu_dev_action0)
        menu_dev_action1 = QtGui.QAction("Action&1", menu_dev)
        menu_dev_action1.setShortcut("F10")
        menu_dev_action1.triggered.connect(lambda: print(self._sessions.sessions))
        menu_dev.addAction(menu_dev_action1)

        self.addMenu(self._menu_file)
        self.addMenu(menu_help)
        self.addMenu(menu_dev)
        self.addMenu(" | ").setDisabled(True)
        self.addMenu(self._menu_user)

    def _show_window_about(self):
        """ * """
        self._session_gui.main_window.window_about = bs.gui.window_about.WindowAbout(self._session_gui)

    def update(self):
        """ *
        Updates the menu_bar with  all its sub-menus.
        """
        # If logged in and session unlocked
        if self._session_gui.session and \
            self._session_gui.session.is_logged_in and \
            self._session_gui.session.is_unlocked:
            # MENU_FILE
            self.menu_file.action_lock.setDisabled(False)
            self.menu_file.action_logout.setDisabled(False)
            # MENU_USER
            self._menu_user.setDisabled(False)
            self._menu_user.setTitle(self._session_gui.session.user.username)
            # update menu
            self._menu_user.clear()
            menu_user_point1 = QtGui.QAction("&Whaaazupppp", self._menu_user)
            self._menu_user.addAction(menu_user_point1)
        # If session logged out or locked
        else:
            # MENU_FILE
            self._menu_file.action_lock.setDisabled(True)
            self._menu_file.action_logout.setDisabled(True)
            # MENU_USER
            self._menu_user.setTitle("-")
            self._menu_user.clear()
            self._menu_user.setDisabled(True)


class WindowMainMenuFile(QtGui.QMenu):
    """ * """
    _sessions = None
    _main_window = None
    _title = None
    _action_new_window = None
    _action_lock = None
    _action_logout = None
    _action_close = None
    _action_exit = None

    def __init__(self, owner, sessions, main_window):
        super(WindowMainMenuFile, self).__init__("", owner)

        self._sessions = sessions
        self._main_window = main_window
        self._title = "&File"
        self._init_ui()

    @property
    def action_lock(self):
        return self._action_lock

    @property
    def action_logout(self):
        return self._action_logout

    @property
    def action_close(self):
        return self.action_close

    @property
    def action_exit(self):
        return self.action_exit

    def _init_ui(self):
        """ * """
        self.setTitle(self._title)

        self._action_new_window = QtGui.QAction("&New Window", self)
        self._action_new_window.triggered.connect(self._sessions.add_session_gui)
        self._action_new_window.setShortcut("Ctrl+N")
        self.addAction(self._action_new_window)
        self.addSeparator()
        self._action_lock = QtGui.QAction("&Lock", self)
        self._action_lock.triggered.connect(self._main_window.lock)
        self._action_lock.setShortcut("Ctrl+L")
        self.addAction(self._action_lock)
        self._action_logout = QtGui.QAction("Log-&Out", self)
        self._action_logout.triggered.connect(self._main_window.log_out)
        self._action_logout.setShortcut("Ctrl+U")
        self.addAction(self._action_logout)
        self._action_close = QtGui.QAction("&Close", self)
        self._action_close.triggered.connect(self._main_window.close)
        self._action_close.setShortcut("Ctrl+W")
        self.addAction(self._action_close)
        self._action_exit = QtGui.QAction("E&xit", self)
        self._action_exit.triggered.connect(self._main_window.exit)
        self._action_exit.setShortcut("Ctrl+Q")
        self.addAction(self._action_exit)


class WindowMainMenuUser(QtGui.QMenu):
    """ * """
    _menu_bar = None
    _session = None

    def __init__(self, owner, session_gui):
        super(WindowMainMenuUser, self).__init__("-", owner)

        self._session = session_gui
        self._menu_bar = owner
