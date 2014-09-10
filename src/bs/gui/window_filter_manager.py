#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

The window GUI that hosts the *Filter-Manager* and all its widgets.
"""

from PySide import QtGui


class WindowFilterManager(QtGui.QMainWindow):
    """ ..

    :param bs.ctrl.session.SessionsCtrl sessions_ctrl: The \
    :class:`bs.ctrl.session.SessionsCtrl` of the running application instance

    This is the filter manager that lists all filters for a user and offers the
    ability to edit them.
    """
    _sessions_ctrl = None

    def __init__(self, sessions_ctrl):
        super(WindowFilterManager, self).__init__()

        self._sessions_ctrl = sessions_ctrl

        self._init_ui()

    def _init_ui(self):
        """ ..
        """
        self.setWindowTitle("Filter Manager")

    def request_exit(self):
        """ ..

        :rtype: `void`

        Requests exit from all hosted widgets where required and closes itself.
        """
        self.close()
        return True
