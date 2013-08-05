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


class Application(QtGui.QApplication):
    """ * """

    idle_1s_timer = None

    def __init__(self, name):
        super(Application, self).__init__(name)

        # timers
        self.idle_1s_timer = QtCore.QTimer(self)
        self.idle_1s_timer.setSingleShot(True)
        self.idle_1s_timer.setInterval(1000)
        # global mouse pos signal
        self.global_mouse_pos_signal = bs.utils.Signal()
        self.global_mouse_press_signal = bs.utils.Signal()
        self.global_mouse_release_signal = bs.utils.Signal()
        # session-wide setup
        font = QtGui.QFont()
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        # window-icon
        self.setWindowIcon(QtGui.QIcon("img/recapp_emblem_noname.png"))

    def notify(self, *args, **kwargs):
        receiver = args[0]
        e = args[1]
        if isinstance(e, QtCore.QEvent):
            if e.type() == QtCore.QEvent.KeyPress or\
                e.type() == QtCore.QEvent.MouseMove and\
                self.idle_1s_timer.isActive():
                self.idle_1s_timer.start()
            # global_mouse_pos
            if e.type() == QtCore.QEvent.Type.MouseMove:
                self.global_mouse_pos_signal.emit(e)
            # global_mouse_press
            if e.type() == QtCore.QEvent.Type.MouseButtonPress:
                self.global_mouse_press_signal.emit(receiver, e)
            # global_mouse_release
            if e.type() == QtCore.QEvent.Type.MouseButtonRelease:
                self.global_mouse_release_signal.emit(receiver, e)
            return QtGui.QApplication.notify(self, *args, **kwargs)
        return True


class WindowMain(QtGui.QMainWindow):
    """ * """
    _sessions = None
    _session_gui = None
    _app = None

    _default_width = 800
    _default_height = 600
    _menu_bar = None
    # references to all other windows. They are most likely initialized in
    # other classes but all referenced here for easy access
    _window_about = None
    _layout = None
    _view = None

    def __init__(self, sessions, session_gui, app):
        super(WindowMain, self).__init__()

        self._sessions = sessions
        self._session_gui = session_gui
        self._app = app

        self._init_ui()
        self.setMouseTracking(True)

    @property
    def session_gui(self):
        return self._session_gui

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

    @property
    def view(self):
        return self._view

    def _init_ui(self):
        """ * """
        self.setStyleSheet(bs.config.CSS)
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
        self.setWindowTitle("%s [%s]" % (bs.config.PROJECT_NAME,
                                         bs.config.VERSION))
        # central widget layout
        widget = QtGui.QWidget()
        self._layout = QtGui.QGridLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(widget)
        widget.setLayout(self._layout)
        # set initial view
        self.set_view('login')
        self.show()

    def set_view(self, view):
        """ *
        Sets the main view to `String view`.
        String view        'login'
        """
        # clear layout
        for i in range(self._layout.count()):
            widget = self._layout.itemAt(i).widget()
            self._layout.removeWidget(widget)
            widget.deleteLater()
        if view == "login":
            # ui: set
            self._view = bs.gui.view_login.ViewLogin(self._sessions,
                                                     self._session_gui)
            self._layout.addWidget(self._view, 0, 0, 1, 1)
            self._view.view_login_form.input_username.setFocus()
        elif view == "x":
            self._view = bs.gui.view_sets.BS(self, self._session_gui, self._app)
            self._layout.addWidget(self._view, 0, 0, 1, 1)
        self._menu_bar.update()

    def lock(self):
        """ *
        Locks the current session, returning the user back to the login-view.
        Keeps any active processes running.
        """
        # lock session
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
        if self._view.request_exit():
            # log-out user
            self._session_gui.session.log_out()
            # detach session from GUI
            self._session_gui.session = None
            # return to login-view
            self.set_view("login")
            return True
        return False

    def exit(self):
        """ *
        Exits the application.
        """
        if self.check_if_exit_legal():
            while len(self._sessions.guis) > 0:
                gui = self._sessions.guis[0]
                if gui.main_window.view.request_exit():
#                     self._sessions.remove_session_gui(gui)
                    gui.main_window.close()

    def check_if_exit_legal(self):
        """ *
        Checks, if application can be exited. That means that there is no
        logged in session with the optional exception of the current window's
        session that will be automatically requested to exit.
        """
        # check if other users are currently logged on
        for session in self._sessions.sessions:
            if session != self._session_gui.session:
                if session.is_logged_in:
                    window_msg = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                                   "Cannot Exit",
                                                   "Other sessions are "\
                                                   "active. %s can only exit "\
                                                   "once all other sessions "\
                                                   "are logged out."
                                                   % (bs.config.PROJECT_NAME, ))
                    window_msg.exec_()
                    return False
        return True

    def closeEvent(self, e):
        """ * """
        if len(self._sessions.guis) <= 1:
            if not self.check_if_exit_legal():
                e.ignore()
                return False
        if isinstance(self._view, bs.gui.view_sets.BS):
            if not self.log_out():
                e.ignore()
                return False
        self._sessions.remove_session_gui(self._session_gui)

    def keyPressEvent(self, e):
        """ * """
        if isinstance(e, QtGui.QKeyEvent):
            # Ctrl + O
            if e.key() == QtCore.Qt.Key_O and (e.modifiers() & QtCore.Qt.ControlModifier):
                print("Nothing to open!")


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
        self._menu_user = WindowMainMenuUser(self, self._main_window, self._session_gui)
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
        self._menu_file.update()
        self._menu_user.update()


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
        # lock
        self._action_lock = QtGui.QAction("&Lock", self)
        self._action_lock.triggered.connect(self._main_window.lock)
        self.addAction(self._action_lock)
        # logout
        self._action_logout = QtGui.QAction("Log-&Out", self)
        self._action_logout.triggered.connect(self._main_window.log_out)
        self.addAction(self._action_logout)
        self.addSeparator()
        # close
        self._action_close = QtGui.QAction("&Close", self)
        self._action_close.triggered.connect(self._main_window.close)
        self.addAction(self._action_close)
        # exit
        self._action_exit = QtGui.QAction("E&xit", self)
        self._action_exit.triggered.connect(self._main_window.exit)
        self._action_exit.setShortcut("Ctrl+Q")
        self.addAction(self._action_exit)

    def showEvent(self, *args, **kwargs):
        self.update()

        return QtGui.QMenu.showEvent(self, *args, **kwargs)

    def update(self):
        """ * """
        # reset all dynamic actions to default
        self._action_lock.setDisabled(False)
        self._action_lock.setShortcut("Ctrl+L")
        self._action_logout.setDisabled(False)
        self._action_logout.setShortcut("Ctrl+U")
        self._action_close.setDisabled(False)
        self._action_close.setShortcut("Ctrl+W")
        if len(self._sessions.guis) <= 1:
            self._action_close.setDisabled(True)
            self._action_close.setShortcut("")
        # case-sensitive handling
        if isinstance(self._main_window.view, bs.gui.view_login.ViewLogin):
            self._action_lock.setDisabled(True)
            self._action_lock.setShortcut("")
            self._action_logout.setDisabled(True)
            self._action_logout.setShortcut("")
        elif isinstance(self._main_window.view, bs.gui.view_sets.BS):
            pass


class WindowMainMenuUser(QtGui.QMenu):
    """ * """
    _window_main_menu = None
    _window_main = None

    _session_gui = None

    def __init__(self, window_main_menu, window_main, session_gui):
        super(WindowMainMenuUser, self).__init__("", window_main_menu)

        self._window_main_menu = window_main_menu
        self._window_main = window_main
        self._session_gui = session_gui

    def update(self):
        if self._window_main.session_gui.session:
            self.setDisabled(False)
            self.setTitle(self._window_main.session_gui.session.user.username)
        else:
            self.setDisabled(True)

    def setEnabled(self, *args, **kwargs):
        if not args[0]:
            self.setTitle("")

        return QtGui.QMenu.setEnabled(self, *args, **kwargs)

    def setDisabled(self, *args, **kwargs):
        if args[0]:
            self.setTitle("")

        return QtGui.QMenu.setDisabled(self, *args, **kwargs)
