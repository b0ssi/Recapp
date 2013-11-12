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

import math
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
    _details_view = None

    def __init__(self):
        super(BMMainView, self).__init__()

        self._queue_scroll_areas = []
        self._details_view = BMDetailsView(self)

        self._init_ui()

    def _init_ui(self):
        # style/bg
        self.setStyleSheet(".BMMainView {background: #%s}" % (bs.config.PALETTE[0], ))
        widget = QtGui.QLabel(self)
        widget.setPixmap(QtGui.QPixmap("./img/backup_monitor_bg.png"))
        # queues
        for i in range(8):
            wrapper = QtGui.QWidget(self)
            scroll_area_widget = bs.gui.lib.ScrollArea(wrapper)
            queue_widget = BMQueueView(scroll_area_widget, i)
            self._queue_scroll_areas.append(scroll_area_widget)
            x = 10 + i * 85
            y = 0
            wrapper.move(x, y)
            scroll_area_widget.setGeometry(0, 0, 85, 319)
            scroll_area_widget.scroll_to(0.0, 1.0)

#         # DEV
#         def test():
#             self._queue_scroll_areas[0].central_widget.add_backup_job()
#         button = QtGui.QPushButton(self)
#         button.move(10, 370)
#         button.clicked.connect(test)
# 
#         def test2():
#             self._queue_scroll_areas[0].central_widget.remove_backup_job(0)
#         button = QtGui.QPushButton(self)
#         button.move(50, 370)
#         button.clicked.connect(test2)
# 
#         def test3():
#             self._queue_scroll_areas[0].central_widget._move_backup_job_to_pole_position()
#         button = QtGui.QPushButton(self)
#         button.move(90, 370)
#         button.clicked.connect(test3)
# 
#         def test4():
#             self._queue_scroll_areas[0].central_widget.next_backup_job_to_pole_position()
#         button = QtGui.QPushButton(self)
#         button.move(130, 370)
#         button.clicked.connect(test4)
# 
#         def test5():
#             self._queue_scroll_areas[0].central_widget._backup_job_in_pole_position.set_progress(random.randint(0, 100))
#         button = QtGui.QPushButton(self)
#         button.move(170, 370)
#         button.clicked.connect(test5)
#         # /DEV


class BMQueueView(QtGui.QFrame):
    """ ..

    :param QtGui.QWidget parent: The parent-``QtGui.QWidget`` for this object.
    :param int index: The queue's number (0 - 7 e.g.)

    This is the the queue GUI the backup-job-nodes get dispatched into.
    """
    _index = None

    _backup_jobs = None
    _backup_job_in_pole_position = None
    _activity_led = None

    def __init__(self, parent, index):
        super(BMQueueView, self).__init__(parent)

        self._index = index

        self._backup_jobs = []

        parent.set_central_widget(self)
        self._init_ui()

    def _init_ui(self):
        self._update_size()
        for i in range(random.randint(0, 16)):
            self.add_backup_job()
        self._activity_led = QtGui.QFrame(self.parent().parent())
        self._activity_led.setGeometry(0, 378, 80, 3)
        self._set_activity_led_state(False)

    def _move_backup_job_to_pole_position(self):
        if len(self._backup_jobs) > 0 and \
            not self._backup_job_in_pole_position:
            backup_job_to_move = self._backup_jobs[0]
            self._backup_jobs.pop(0)
            self._backup_job_in_pole_position = backup_job_to_move
            backup_job_to_move.setParent(self.parent().parent())
            # update queue
            self._update_size()
            self._update_backup_jobs_positions()
            self._update_position()
            # reposition backup-job
            backup_job_to_move.move(0, 334)
            backup_job_to_move.show()
            backup_job_to_move.expand()

    def _set_activity_led_state(self, state):
        """ ..

        :param bool state: ``True`` for active, ``False`` for inactive.

        Sets the visual appearance to represent the state of the queue.
        """
        if state:
            self._activity_led.setStyleSheet("border-radius: 1px; background: #%s" % (bs.config.PALETTE[4], ))
        else:
            self._activity_led.setStyleSheet("border-radius: 1px; background: #%s" % (bs.config.PALETTE[10], ))

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
        widget = BMQueueJobView(self, str(len(self._backup_jobs)))
        widget.show()
        self._backup_jobs.append(widget)
        # update size, positions
        self._update_size()
        self._update_backup_jobs_positions()
        self._update_position()
        # move to pole-position if it's the only current job in queue
        self._move_backup_job_to_pole_position()

    def next_backup_job_to_pole_position(self):
        """ ..

        Retires the current backup-job in the pole position and moves the \
        next in the queue to it if queue is not empty.
        """
        # delete current backup-job in pole-position
        if self._backup_job_in_pole_position:
            self._backup_job_in_pole_position.deleteLater()
            self._backup_job_in_pole_position = None
            self._move_backup_job_to_pole_position()

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
        # focus out of backup-job manually
        widget_to_remove.clearFocus()
        # focus in onto next backup-job in list
        backup_job_index = self._backup_jobs.index(widget_to_remove)
        if len(self._backup_jobs) > backup_job_index + 1:
            self._backup_jobs[backup_job_index + 1].setFocus()
        elif len(self._backup_jobs) == backup_job_index + 1 and \
            len(self._backup_jobs) > 1:
            self._backup_jobs[backup_job_index - 1].setFocus()
        elif self._backup_job_in_pole_position:
            self._backup_job_in_pole_position.setFocus()
        # delete
        self._backup_jobs.pop(widget_index_to_remove)
        widget_to_remove.deleteLater()
        # update size, positions
        self._update_size()
        self._update_backup_jobs_positions()
        self._update_position()

    def focusInEvent(self, e):
        self._set_activity_led_state(True)

        super(BMQueueView, self).focusInEvent(e)

    def focusOutEvent(self, e):
        self._set_activity_led_state(False)

        super(BMQueueView, self).focusOutEvent(e)


class BMQueueJobView(bs.gui.lib.BSFrame):
    """ ..

    :param QtGui.QWidget parent: The parent-``QtGui.QWidget`` for this object.
    :param str title: The title to be displayed on the widget.

    This is the widget that represents a single job that sits in the queue.
    """

    _progress_bar = None
    _title = None

    def __init__(self, parent, title):
        super(BMQueueJobView, self).__init__(parent)

        self._title = title

        self._init_ui()

    def _init_ui(self):
        # CSS
        self.setStyleSheet(".BMQueueJobView {background: #%s; border-radius: 3px}"
                           % (bs.config.PALETTE[2], ))
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setGeometry(0, 0, 84, 30)
        self.resize(84, 30)
        # progress-bar
        self._progress_bar = QtGui.QFrame(self)
        self._progress_bar.setGeometry(1, 30, 2, 2)
        self._progress_bar.setStyleSheet("background: #%s" % (bs.config.PALETTE[10], ))
        # title
        self._title = QtGui.QLabel(self._title, self)
        self._title.move(11, 8)

    def _get_queue(self):
        """ ..

        :rtype bs.gui.view_backup_monitor.BMQueueView: The corresponding \
        :class:`BMQueueView` for this backup-job widget.

        Gets the corresponding queue, depending on what widget's parent is \
        (wrapper if in pole-position, queue if in queue)
        """
        if isinstance(self.parent(), BMQueueView):
            return self.parent()
        else:
            return self.parent().children()[0].central_widget

    def expand(self):
        """ ..

        Expands the widget to show extra details in pole-position.
        """
        self.resize(self.width(), 38)

    def set_progress(self, percentage):
        """ ..

        :param int percentage: The percentage to set the progress-bar to.

        Updates the widget to represent the progress in percent in its UI.
        """
        self._progress_bar.resize(round((self.width() - 2) * (percentage / 100)), self._progress_bar.height())

    def keyReleaseEvent(self, e):
        # del
        if e.matches(QtGui.QKeySequence.Delete):
            # remove itself
            if isinstance(self.parent(), BMQueueView):
                self.parent().remove_backup_job(self)

        super(BMQueueJobView, self).keyReleaseEvent(e)

    def focusInEvent(self, e):
        self.setStyleSheet(".BMQueueJobView {background: #%s; border: 1px solid #%s; border-radius: 3px}"
                           % (bs.config.PALETTE[2],
                              bs.config.PALETTE[9], ))
        self._get_queue().focusInEvent(e)

    def focusOutEvent(self, e):
        self.setStyleSheet(".BMQueueJobView {background: #%s; border-radius: 3px}"
                           % (bs.config.PALETTE[2], ))
        self._get_queue().focusOutEvent(e)

class BMDetailsView(QtGui.QWidget):
    """ ..

    :param QtGui.QWidget parent: The widget to be assigned as the parent.

    The widget displaying the active backup-job's details.
    """

    _current_item_path = None
    _current_item_path_label = None
    _progress_bar = None

    def __init__(self, parent):
        super(BMDetailsView, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        self.move(0, 381)
        self._progress_bar = BMDetailsProgressBarView(self)
        # current item path
        widget = QtGui.QLabel("Current Item", self)
        widget.setStyleSheet("font-weight: bold; color: #%s" % (bs.config.PALETTE[2], ))
        widget.move(15, 20)
        self._current_item_path_label = QtGui.QLabel(self)
        self._current_item_path_label.move(112, 20)
        self._current_item_path_label.setStyleSheet("color: #%s" % (bs.config.PALETTE[9], ))
        self.current_item_path = "C:\\sldkfj"

    @property
    def progress_bar(self):
        """ ..
        :rtype BMDetailsProgressBarView:
        """
        return self._progress_bar

    @property
    def current_item_path(self):
        return self._current_item_path

    @current_item_path.setter
    def current_item_path(self, arg):
        self._current_item_path = arg
        self._current_item_path_label.setText(self._current_item_path)


class BMDetailsProgressBarView(QtGui.QWidget):
    """ ..

    :param QtGui.QWidget parent: The widget to be assigned as the parent.

    The progress bar for the details view.
    """

    _bar_bg = None
    _bar_marker = None
    _bar_capacity_min = None
    _bar_capacity_max = None
    _bar_capacity_current = None

    def __init__(self, parent):
        super(BMDetailsProgressBarView, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        self.resize(699, 134)
        self.move(14, 57)
        # progress bar
        self._bar_bg = QtGui.QFrame(self)
        self._bar_bg.resize(675, 3)
        self._bar_bg.move(0, 16)
        self._bar_bg.setStyleSheet("border-radius: 1px; background: #%s" % (bs.config.PALETTE[9]))
        # progress bar marker
        self._bar_marker = QtGui.QFrame(self)
        self._bar_marker.resize(4, 3)
        self._bar_marker.move(0, 16)
        self._bar_marker.setStyleSheet("background: #%s" % (bs.config.PALETTE[4]))
        # labels
        self._bar_capacity_min = QtGui.QLabel(bs.utils.format_data_size(0), self)
        self._bar_capacity_min.setStyleSheet("color: #%s" % (bs.config.PALETTE[10]))
        self._bar_capacity_min.move(0, 0)
        self._bar_capacity_max = QtGui.QLabel(bs.utils.format_data_size(100), self)
        self._bar_capacity_max.setStyleSheet("color: #%s" % (bs.config.PALETTE[10]))
        self._bar_capacity_max.move(600, 0)
        self._bar_capacity_max.resize(75, 30)
        self._bar_capacity_max.setAlignment(QtCore.Qt.AlignTop)
        self._bar_capacity_max.setAlignment(QtCore.Qt.AlignRight)
        self._bar_capacity_current = QtGui.QLabel("0.00%", self)
        self._bar_capacity_current.setStyleSheet("color: #%s" % (bs.config.PALETTE[9]))
        self._bar_capacity_current.resize(50, self._bar_capacity_current.height())
        self._bar_capacity_current.setAlignment(QtCore.Qt.AlignRight)
        self._bar_capacity_current.move(0, 22)
        self.set_progress(0, 100)

    def set_progress(self, current, total):
        """ ..

        :param int current: The size in bytes currently completed.
        :param int total: The total size in bytes.

        Sets the progress bar to the corresponding state. Calculates \
        percentage by itself.
        """
        # update progress-indicator
        percentage = float(current / total)
        # set marker position
        x = round(percentage * (self._bar_bg.width() - self._bar_marker.width()))
        y = self._bar_marker.y()
        self._bar_marker.move(x, y)
        # set current percentage position
        if self._bar_marker.x() < 13:
            x = -15
        elif x > self._bar_bg.width() - 13 - 13:
            x = self._bar_bg.width() - 52
        else:
            x = self._bar_marker.x() - 28
        y = self._bar_capacity_current.y()
        self._bar_capacity_current.move(x, y)
        # update labels
        self._bar_capacity_max.setText(bs.utils.format_data_size(total))
        self._bar_capacity_current.setText("%.2f%s" % (percentage * 100.00, "%", ))
