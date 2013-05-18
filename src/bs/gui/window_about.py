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

""" * """

import bs.config
from PySide import QtGui


class WindowAbout(QtGui.QDialog):
    """ * """
    _default_width = 300
    _default_height = 200
    _session_gui = None

    def __init__(self, session_gui):
        super(WindowAbout, self).__init__()

        self._session_gui = session_gui
        self.init_ui()

    def init_ui(self):
        """ * """
        # set size
        self.setGeometry(self._session_gui.main_window.x() + self._session_gui.main_window.width() / 2 - self._default_width / 2,
                         self._session_gui.main_window.y() + self._session_gui.main_window.height() / 2 - self._default_height / 2,
                         self._default_width,
                         self._default_height)
        self.setWindowTitle("About %s" % (bs.config.PROJECT_NAME, ))
#        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
#        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setModal(True)
        self.show()
