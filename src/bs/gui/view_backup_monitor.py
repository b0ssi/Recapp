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

import random

from PySide import QtCore, QtGui

import bs.config
import bs.gui.lib


class BMMainView(QtGui.QFrame):
    ''' ..

    This is the master view for the backup-monitor that directly sits in the
    window, hosting all graphical elements except for the window and menu.
    '''

    _queue_scroll_areas = None

    def __init__(self):
        super(BMMainView, self).__init__()

        self._queue_scroll_areas = []

        self._init_ui()

    def _init_ui(self):
        # style/bg
        self.setStyleSheet(".BMMainView {background: #%s}" % (bs.config.PALETTE[0], ))
        widget = QtGui.QLabel(self)
        widget.setPixmap(QtGui.QPixmap("./img/backup_monitor_bg.png"))
        # queues
        for i in range(8):
            scroll_area_widget = bs.gui.lib.ScrollArea(self)
            queue_widget = BMQueueView(scroll_area_widget, i)
            self._queue_scroll_areas.append(scroll_area_widget)
            x = 10 + i * 85
            y = 0
            scroll_area_widget.setGeometry(x, y, 85, 319)
            scroll_area_widget.scroll_to(0.0, 1.0)

        # DEV
        def test():
            self._queue_scroll_areas[0]._central_widget.add_backup_job()
        button = QtGui.QPushButton(self)
        button.move(10, self.height() - button.height())
        button.clicked.connect(test)

        def test2():
            self._queue_scroll_areas[0]._central_widget.remove_backup_job(0)
        button = QtGui.QPushButton(self)
        button.move(50, self.height() - button.height())
        button.clicked.connect(test2)
        # /DEV


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

        parent.set_central_widget(self)
        self._init_ui()

    def _init_ui(self):
        self._update_size()

    def _update_size(self):
        """ ..

        Recalculates cumulative size of all positioned self._backup_jobs and \
        resizes itself.
        """
        width = 0
        height = 0
        for backup_job in self._backup_jobs:
            width = max(width, backup_job.width())
            height += backup_job.height() + 1
        height -= 1
        # set to minimum size of scroll-area parent
        if height < self.parent().height(): height = self.parent().height()
        self.resize(width, height)

    def _update_position(self):
        """ ..

        Updates the queue widget's position.
        """
        self.move(self.x(),
                  0 - (self.height() - self.parent().height()))

    def _update_backup_jobs_positions(self):
        """ ..

        Updates the positions of all current backup-jobs, stacking them from \
        the bottom up.
        """
        offset = self.height() - (31 * len(self._backup_jobs) - 1)
        if offset < 0: offset = 0
        for backup_job in self._backup_jobs:
            x = 0
            y = offset + 31 * (len(self._backup_jobs) - self._backup_jobs.index(backup_job, ) - 1)
            backup_job.move(x, y)

    def add_backup_job(self):
        """ ..

        :param bs.ctrl.session.BackupSetCtrl BackupSetCtrl: The \
        :class:`~bs.ctrl.session.BackupSetCtrl` to dispatch as a new job.

        Adds a backup-set as a new job to the list.
        """
        widget = BMQueueJobView(self)
        label = QtGui.QLabel(str(len(self._backup_jobs)), widget)
        widget.show()
        self._backup_jobs.append(widget)
        # update size, positions
        self._update_size()
        self._update_backup_jobs_positions()
        self._update_position()

    def remove_backup_job(self, backup_job):
        """ ..

        :param QtGui.QWidget backup_job: The \
        :class:`~bs.gui.view_backup_monitor.BMQueueJobView` to be \
        removed. This parameter can be overloaded by an ``int`` type, which is then \
        interpreted as the index in the \
        :class:`~bs.gui.view_backup_monitor.BMQueueJobView`-list of the \
        backup-job to be removed.

        Removes the backup-job at ``index`` in the queue.
        """
        if isinstance(backup_job, int):
            widget_index_to_remove = backup_job
            widget_to_remove = self._backup_jobs[backup_job]
        elif isinstance(backup_job, BMQueueJobView):
            widget_index_to_remove = self._backup_jobs.index(backup_job, )
            widget_to_remove = backup_job
        self._backup_jobs.pop(widget_index_to_remove)
        widget_to_remove.deleteLater()
        # update size, positions
        self._update_size()
        self._update_backup_jobs_positions()
        self._update_position()


class BMQueueJobView(bs.gui.lib.BSFrame):
    """ ..

    :param QtGui.QWidget parent: The parent-``QtGui.QWidget`` for this object.

    This is the widget that represents a single job that sits in the queue.
    """
    def __init__(self, parent):
        super(BMQueueJobView, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        # CSS
        self.setStyleSheet(".BMQueueJobView {background: #%s; border-radius: 3px}"
                           % (bs.config.PALETTE[2], ))
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setGeometry(0, 0, 84, 30)
        self.resize(84, 30)

    def keyReleaseEvent(self, e):
        # del
        if e.matches(QtGui.QKeySequence.Delete):
            # focus in onto next backup-job in list
            own_index = self.parent()._backup_jobs.index(self)
            try:
                self.parent()._backup_jobs[own_index + 1].setFocus()
            except:
                try:
                    self.parent()._backup_jobs[own_index - 1].setFocus()
                except:
                    pass
            # remove itself
            self.parent().remove_backup_job(self)

        super(BMQueueJobView, self).keyReleaseEvent(e)

    def focusInEvent(self, e):
        self.setStyleSheet(".BMQueueJobView {background: #%s; border: 1px solid #%s; border-radius: 3px}"
                           % (bs.config.PALETTE[2],
                              bs.config.PALETTE[9], ))

    def focusOutEvent(self, e):
        self.setStyleSheet(".BMQueueJobView {background: #%s; border-radius: 3px}"
                           % (bs.config.PALETTE[2], ))
