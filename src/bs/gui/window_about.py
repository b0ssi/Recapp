# -*- coding: utf-8 -*-

###############################################################################
##    bs.gui.window_about                                                    ##
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

""" This package contains the *about* window class(es)."""

import bs.config
import platform
from PySide import QtGui


class WindowAbout(QtGui.QDialog):
    """ ..

    :param bs.ctrl.session.SessionGuiCtrl session_gui:

    This is the *about* window.
    """
    _default_width = 300
    _default_height = 200
    _session_gui = None

    _layout = None

    def __init__(self, session_gui):
        super(WindowAbout, self).__init__()

        self._session_gui = session_gui
        self._init_ui()

    def _init_ui(self):
        """ * """
        self._layout = QtGui.QGridLayout(self)
        self._layout.setContentsMargins(30, 30, 30, 10)
        self._layout.setColumnStretch(0, 30)
        self._layout.setColumnStretch(1, 70)
        # set size
        self.setGeometry(self._session_gui.main_window.x() + self._session_gui.main_window.width() / 2 - self._default_width / 2,
                         self._session_gui.main_window.y() + self._session_gui.main_window.height() / 2 - self._default_height / 2,
                         self._default_width,
                         self._default_height)
        self.setWindowTitle("About %s" % (bs.config.PROJECT_NAME, ))
        self.setModal(True)
        self.show()
        ## FILL WITH CONTENTS ##
        # title
        widget = QtGui.QLabel("%s" % (bs.config.PROJECT_NAME, ))
        widget.setStyleSheet("font-weight: bold; font-size: 18px")
        self._layout.addWidget(widget, 0, 0, 1, 2)
        # version
        widget = QtGui.QLabel("%s" % ("Version: ", ))
        self._layout.addWidget(widget, 1, 0, 1, 1)
        widget = QtGui.QLabel("%s" % (bs.config.VERSION, ))
        self._layout.addWidget(widget, 1, 1, 1, 1)
        # platform-architecture
        widget = QtGui.QLabel("%s" % ("Application Platform Architecture: ", ))
        if platform.architecture()[0] == "32bit":
            platform_architecture = "x86"
        elif platform.architecture()[0] == "64bit":
            platform_architecture = "x86-64"
        else:
            platform_architecture = platform.architecture()[0]
        self._layout.addWidget(widget, 2, 0, 1, 1)
        widget = QtGui.QLabel("%s" % (platform_architecture, ))
        self._layout.addWidget(widget, 2, 1, 1, 1)
