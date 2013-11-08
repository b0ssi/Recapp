# -*- coding: utf-8 -*-
###############################################################################
##    bs.ctrl.backup                                                         ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  Nov 09, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################
'''
This package hosts all views used by the *Backup-Monitor*.
'''

from PySide import QtCore, QtGui

import bs.config


class BMMainView(QtGui.QFrame):
    ''' ..

    This is the master view for the backup-monitor that directly sits in the
    window, hosting all graphical elements except for the window and menu.
    '''

    _queues = None

    def __init__(self):
        super(BMMainView, self).__init__()

        self._queues = []

        self._init_ui()

    def _init_ui(self):
        # style
        self.setStyleSheet("background: #%s url(./img/backup_monitor_bg.png) \
                            no-repeat" % (bs.config.PALETTE[0], ))
        # queues
        for i in range(8):
            widget = BMQueueView(self, i)
            self._queues.append(widget)
#             x = 10 + i * 85
#             y = 10
#             widget.setGeometry(x, y, widget.width(), widget.height())


class BMQueueView(QtGui.QFrame):
    """ ..

    :param QtGui.QWidget parent: The parent-``QtGui.QWidget`` for this object.
    :param int index: The queue's number (0 - 7 e.g.)

    This is the the queue GUI the backup-job-nodes get dispatched into.
    """
    _index = None

    _backup_jobs = None

    def __init__(self, parent, index):
        super(BMQueueView, self).__init__(parent)

        self._index = index

        self._backup_jobs = []

        self._init_ui()

    def _init_ui(self):
        for i in range(32):
            self.add_backup_job()

    def _update_size(self):
        # recalculates cumulative size of all positioned self._backup_jobs and
        # resizes itself.
        width = 0
        height = 0
        for backup_job in self._backup_jobs:
            br = QtCore.QRect(0, 0,
                              backup_job.x() + backup_job.width(),
                              backup_job.y() + backup_job.height())
            width = max(width, br.width())
            height = max(height, br.height())
        self.resize(width, height)

    def update_position(self, percentage):
        """ ..

        :param float percentage: The y-position (0...1) to which to set the \
        container to.

        Sets the container's y-position to a given percentage.
        At 0 the queue is scrolled all the way down and \
        the first (lowest) item sits just above the item that is being backed \
        up. At 1 the queue is scrolled all the way up, showing the last \
        element in the queue (top most), while overflow-cropping the first \
        (lowest) items, if the queue is big enough.
        """
        x = 10 + self._index * 85
        y = percentage * 30 + (1 - percentage) * (319 - self.height())
        self.setGeometry(x, y, self.width(), self.height())

    def add_backup_job(self):
        """ ..

        :param bs.ctrl.session.BackupSetCtrl BackupSetCtrl: The \
        :class:`~bs.ctrl.session.BackupSetCtrl` to dispatch as a new job.

        Adds a backup-set as a new job to the list.
        """
        self._backup_jobs.append(BMQueueJobView(self))
        # update y-positions
        for backup_job in self._backup_jobs:
            x = 0
            y = 31 * (len(self._backup_jobs) - self._backup_jobs.index(backup_job, ) - 1)
            backup_job.move(x, y)
        self._update_size()
        self.update_position(0.0)


class BMQueueJobView(QtGui.QFrame):
    """ ..

    :param QtGui.QWidget parent: The parent-``QtGui.QWidget`` for this object.

    This is the widget that represents a single job that sits in the queue.
    """
    def __init__(self, parent):
        super(BMQueueJobView, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("background: #%s; border-radius: 3px" % (bs.config.PALETTE[2], ))
        self.setGeometry(0, 0, 84, 30)
        self.resize(84, 30)
