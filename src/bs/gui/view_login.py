#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

"""

from PySide import QtGui
import bs.config
import os
import re


class ViewLogin(QtGui.QWidget):
    """ ..

    """
    _layout = None
    _sessions = None
    _session_gui = None
    _view_login_form = None

    def __init__(self, sessions, session_gui):
        super(ViewLogin, self).__init__()

        self._session_gui = session_gui
        self._sessions = sessions
        self.setContentsMargins(0, 0, 0, 0)
        self._init_ui()

    @property
    def view_login_form(self):
        return self._view_login_form

    def _init_ui(self):
        """ ..

        """
        # set-up layout
        self._layout = QtGui.QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setColumnMinimumWidth(1, 200)
        self._layout.setColumnMinimumWidth(2, 10)
        self._layout.setColumnMinimumWidth(3, 200)
        self._layout.setColumnStretch(0, 40)
        self._layout.setColumnStretch(2, 20)
        self._layout.setColumnStretch(4, 40)
        self.setLayout(self._layout)

        # login-form
        self._view_login_form = ViewLoginForm(self, self._sessions)
        self._layout.addWidget(self._view_login_form, 0, 1, 1, 1)

        # emblem
        self._layout.addWidget(ViewLoginEmblem(), 0, 3, 1, 1)

    def unlock(self, username, password):
        """ ..

        """

    def log_in(self, username, password):
        """ ..

        :param str username: The *username* part of the credentials to log-\
        in with.
        :param str password: The *password* part of the credentials to log-\
        in with.

        Gets session for user if login is valid and sets up UI.
        """
        session = self._sessions.add_session(username, password)
        # log-in failed
        if not session:
            self._view_login_form.input_username.setStyleSheet("background: #FF7373")
            self._view_login_form.input_password.setStyleSheet("background: #FF7373")
        # session already active
        elif session == -1:
            window_msg = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                           "Session Already Active",
                                           "This user already runs an active session.")
            window_msg.exec_()
        # log-in success
        else:
            # add reference to new session to session_gui
            self._session_gui.session = session
            # set view
            self._session_gui.main_window.set_view('view_sets')

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Hook-method called by window manager before changing view.
        Close any view-specific processes here. Events, etc.
        """
        return True


class ViewLoginForm(QtGui.QWidget):
    """ ..

    """
    _layout = None
    _label_username = None
    _input_username = None
    _input_username_completer = None
    _label_password = None
    _input_password = None
    _btn_login = None
    _view_login = None  # reference to main login view
    _sessions = None

    def __init__(self, view_login, sessions):
        super(ViewLoginForm, self).__init__()

        self._view_login = view_login
        self._sessions = sessions
        self._init_ui()

    @property
    def input_username(self):
        return self._input_username

    @property
    def input_password(self):
        return self._input_password

    def _init_ui(self):
        """ ..

        """
        self._layout = QtGui.QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setRowMinimumHeight(1, 20)
        self._layout.setRowMinimumHeight(2, 20)
        self._layout.setRowMinimumHeight(3, 20)
        self._layout.setRowStretch(0, 50)
        self._layout.setRowStretch(4, 50)
        # form
        self._label_username = QtGui.QLabel("Username:")
        self._label_username.setDisabled(True)
        self._input_username = QtGui.QLineEdit()
        self._label_password = QtGui.QLabel("Password:")
        self._label_password.setDisabled(True)
        self._input_password = QtGui.QLineEdit()
        self._input_password.setEchoMode(self._input_password.Password)
        self._btn_login = QtGui.QPushButton()
        # form setup that is affected when form set into 'unlock' mode
        self._set_into_unlock(False)
        # add to layout
        self._layout.addWidget(self._label_username, 1, 0, 1, 1)
        self._layout.addWidget(self._input_username, 1, 1, 1, 1)
        self._layout.addWidget(self._label_password, 2, 0, 1, 1)
        self._layout.addWidget(self._input_password, 2, 1, 1, 1)
        self._layout.addWidget(self._btn_login, 3, 1, 1, 1)
        # CONNECT SIGNALS
        self._input_username.textChanged.connect(self._on_text_changed)
        self._input_username.textEdited.connect(self._on_text_edited)
        self._input_username.textChanged.connect(self._on_text_changed)
        self._input_password.textChanged.connect(self._on_text_changed)
        # form: log-in
        signals_to_connect = [self._input_username.returnPressed,
                              self._input_password.returnPressed,
                              self._btn_login.clicked
                              ]
        for signal in signals_to_connect:
            # disconnect signal
            try:
                signal.disconnect()
            except:
                pass
            # reconnect
            signal.connect(lambda: self._view_login.log_in(self._input_username.text(),
                                                           self._input_password.text()
                                                           )
                           )

    def _on_text_changed(self):
        """ ..

        Refreshes form formatting, updates auto completer.
        """
        # INPUT_USERNAME: HIGHLIGHT LOCKED USERNAME
        input_username_text = self._input_username.text()
        # Checks if session with `username` exists and if it's locked.
        if re.match(bs.config.REGEX_PATTERN_USERNAME, input_username_text):
            for session in self._sessions.sessions:
                if (session.user.username == input_username_text and
                        not session.is_unlocked and
                        session.is_logged_in):
                    self._set_into_unlock(True)
                    return True
        self._set_into_unlock(False)
        return False

    def _on_text_edited(self):
        """ ..

        Updates form only on text edits (prevents completion list from getting
        updated on cycling through list)
        """
        # INPUT_USERNAME: AUTO COMPLETER
        usernames = [(x.user.username) for x in self._sessions.sessions if not x.is_unlocked and x.is_logged_in]
        self._input_username_completer = QtGui.QCompleter(usernames,
                                                          parent=self)
        self._input_username_completer.setCompletionMode(self._input_username_completer.InlineCompletion)
        self._input_username.setCompleter(self._input_username_completer)

    def _set_into_unlock(self, arg):
        """ ..

        """
        # set into unlock mode
        if arg:
            text = "Un&lock"
            self._input_username.setStyleSheet("background: #FFFF73")
            self._input_password.setStyleSheet("background: #FFFFFF")
            self._btn_login.setText(text)
        # set into standard login mode
        elif not arg:
            text = "&Login"
            self._btn_login.setText(text)
            self._input_username.setStyleSheet("background: #FFFFFF")
            self._input_password.setStyleSheet("background: #FFFFFF")


class ViewLoginEmblem(QtGui.QLabel):
    """ ..

    """

    _layout = None

    def __init__(self):
        super(ViewLoginEmblem, self).__init__()

        self._init_ui()

    def _init_ui(self):
        pm = QtGui.QPixmap(os.path.realpath("img/recapp_emblem.png"))
        self.setPixmap(pm)
