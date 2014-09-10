#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

The window GUI that hosts the *Backup-Monitor*.
"""

from PySide import QtGui

import bs.config
import bs.gui.view_backup_monitor


class WindowBackupMonitor(QtGui.QMainWindow):
    """ ..

    :param bs.ctrl.session.SessionsCtrl sessions_ctrl: The central \
    :class:`~bs.ctrl.session.SessionsCtrl` managing all \
    :class:`~bs.ctrl.session.SessionCtrl`.

    The central Backup-Monitor window that displays stati of and management
    options for all dispatched backup-jobs.
    """
    _layout = None
    _sessions_ctrl = None

    def __init__(self, sessions_ctrl):
        """ ..

        """
        super(WindowBackupMonitor, self).__init__()

        self._sessions_ctrl = sessions_ctrl

        self._init_ui()

    def _init_ui(self):
        """ ..

        """
        self.setWindowTitle("%s: Backup Monitor" % (bs.config.PROJECT_NAME, ))
        self.setCentralWidget(QtGui.QWidget())
        # set position next to first main_window
        x = self._sessions_ctrl.guis[0].main_window.geometry().x() + \
            self._sessions_ctrl.guis[0].main_window.frameGeometry().width()
        y = self._sessions_ctrl.guis[0].main_window.geometry().y()
        self.setGeometry(x, y, 699, 512)
        self.setMinimumSize(699, 512)
        # layout
        self._layout = QtGui.QGridLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        # set view
        view = bs.gui.view_backup_monitor.BMMainView()
        self.centralWidget().setLayout(self._layout)
        self._layout.addWidget(view, 0, 0, 1, 1)

    @property
    def view(self):
        """ ..

        :type: :class:`~bs.gui.view_backup_monitor.BMMainView`
        :permissions: read

        Returns the main view widget of the backup-monitor directly.
        """
        return self._layout.itemAt(0).widget()

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all \
        children.
        """
        # request exit for all children
        for child in self.children() + self.centralWidget().children():
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        # close itself
        self.close()
        return True


class WindowDispatchCheck(QtGui.QDialog):
    """ ..

    :param bs.ctrl.session.BackupSetCtrl backup_set:
    :param bs.gui.window_backup_monitor.WindowBackupMonitor backup_set:

    This is a dispatch check GUI that runs several checks before dispatching \
    the backup-set to the queue for backup and prompts for dispatch parameters.
    """
    _backup_set = None
    _bm_window = None
    _combo_box_queue = None
    _layout = None

    def __init__(self, backup_set, bm_window):
        """ ..

        """
        super(WindowDispatchCheck, self).__init__()

        self._backup_set = backup_set
        self._bm_window = bm_window
        self._init_ui()

    def _init_ui(self):
        """ ..

        """
        self.setWindowTitle("Backup-Job Dispatch")
        self._layout = QtGui.QGridLayout(self)
        # if backup-set already exists in any of the monitor's queues,
        # deactivate and notify
        if self._bm_window.view.has_backup_set_in_queues(self._backup_set):
            msg = "This backup-set is already enqueued."
            self._layout.addWidget(QtGui.QLabel(msg), 0, 0, 1, 2)
            btn_ok = QtGui.QPushButton("OK")
            btn_ok.clicked.connect(self.close)
            self._layout.addWidget(btn_ok, 1, 1, 1, 1)
        else:
            msg = "Please choose a queue to submit the backup-job to."
            self._layout.addWidget(QtGui.QLabel(msg), 0, 0, 1, 2)
            # queue
            self._layout.addWidget(QtGui.QLabel("Queue:"), 1, 0, 1, 1)
            self._combo_box_queue = QtGui.QComboBox(self)
            self._combo_box_queue.insertItems(0,
                                              ["1", "2", "3", "4", "5", "6",
                                               "7", "8"])
            self._layout.addWidget(self._combo_box_queue, 1, 1, 1, 1)
            # OK/Cancel buttons
            btn_submit = QtGui.QPushButton("&Submit")
            btn_submit.clicked.connect(self._submit)
            self._layout.addWidget(btn_submit, 2, 0, 1, 1)
            btn_cancel = QtGui.QPushButton("&Cancel")
            btn_cancel.clicked.connect(self.close)
            self._layout.addWidget(btn_cancel, 2, 1, 1, 1)

        self.exec_()

    def _submit(self):
        """ ..

        """
        queue_number = int(self._combo_box_queue.currentText())
        self._bm_window.show()
        self._bm_window.view.queues[queue_number - 1].add_backup_job(self._backup_set)
        self.close()

    def closeEvent(self, e):
        """ ..

        Override.
        """
        self.deleteLater()

    def hideEvent(self, e):
        """ ..

        Override.
        """
        self.deleteLater()
