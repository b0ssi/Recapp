# -*- coding: utf-8 -*-
###############################################################################
##    bs.ctrl.backup                                                         ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Nov 06, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################
"""
The window GUI that hosts the *Backup-Monitor*.
"""

from PySide import QtCore, QtGui

import bs.config
import bs.gui.window_main
import bs.gui.view_backup_monitor


class WindowBackupMonitor(QtGui.QMainWindow):
    """ ..

    :param bs.ctrl.session.SessionsCtrl sessions_ctrl: The central \
    :class:`~bs.ctrl.session.SessionsCtrl` managing all \
    :class:`~bs.ctrl.session.SessionCtrl`.

    The central Backup-Monitor window that displays stati of and management options for all dispatched backup-jobs.
    """
    _layout = None
    _sessions_ctrl = None

    def __init__(self, sessions_ctrl):
        super(WindowBackupMonitor, self).__init__()

        self._sessions_ctrl = sessions_ctrl

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("%s: Backup Monitor" % (bs.config.PROJECT_NAME, ))
        self.setCentralWidget(QtGui.QWidget())
        # set position next to first main_window
        x = self._sessions_ctrl.guis[0].main_window.geometry().x() + self._sessions_ctrl.guis[0].main_window.frameGeometry().width()
        y = self._sessions_ctrl.guis[0].main_window.geometry().y()
        self.setGeometry(x, y, 699, 512)
        # layout
        self._layout = QtGui.QGridLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        # set view
        view = bs.gui.view_backup_monitor.BMMainView()
        self.centralWidget().setLayout(self._layout)
        self._layout.addWidget(view, 0, 0, 1, 1)

        self.show()
