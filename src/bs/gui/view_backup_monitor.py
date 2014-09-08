#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" ..

This package hosts all views used by the *Backup-Monitor*.
"""

from PySide import QtCore, QtGui

import bs.config
import bs.ctrl.backup
import bs.gui.lib


class BMMainView(QtGui.QFrame):
    """ ..

    This is the master view for the backup-monitor that directly sits in the
    window, hosting all graphical elements except for the window and menu.
    """

    _queue_scroll_areas = None
    _details_view = None

    def __init__(self):
        """ ..

        """
        super(BMMainView, self).__init__()

        self._queue_scroll_areas = []
        self._details_view = BMDetailsView(self)

        self._init_ui()

    def _init_ui(self):
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        # style/bg
        self.setStyleSheet(".BMMainView {background: #%s}"
                           % (bs.config.PALETTE[0], ))
        widget = QtGui.QLabel(self)
        widget.setPixmap(QtGui.QPixmap("./img/backup_monitor_bg.png"))
        # queues
        for i in range(8):
            wrapper = QtGui.QWidget(self)
            scroll_area_widget = bs.gui.lib.ScrollArea(wrapper)
            BMQueueView(scroll_area_widget, i)
            self._queue_scroll_areas.append(scroll_area_widget)
            x = 10 + i * 85
            y = 0
            wrapper.move(x, y)
            scroll_area_widget.setGeometry(0, 0, 85, 319)
            scroll_area_widget.scroll_to(0.0, 1.0)

    @property
    def details_view(self):
        """ ..

        :type: :class:`~bs.gui.view_backup_monitor.BMDetailsView`
        """
        return self._details_view

    @property
    def queues(self):
        """ ..

        :type: list

        A list containing the eight queue GUIs in ascending order.
        """
        return [x.central_widget for x in self._queue_scroll_areas]

    def has_backup_set_in_queues(self, backup_set):
        """ ..

        :param bs.ctrl.session.BackupSet backup_set: The \
        :class:`~bs.ctrl.session.BackupSet` to check for whether or not it \
        currently already exists in any of the queues.

        Checks whether or not the ``backup_set`` is already queued up in any
        of its queues (or/and is active).
        """
        for queue in self.queues:
            if queue.has_backup_set_in_queue(backup_set):
                return True
        return False

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all
        children.
        """
        # request exit for all children
        for child in self.children() + self._queue_scroll_areas:
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        return True


class BMQueueView(bs.gui.lib.BSFrame):
    """ ..

    :param QtGui.QWidget parent: The parent-``QtGui.QWidget`` for this object.
    :param int index: The queue's number (0 - 7 e.g.)

    This is the the queue GUI the backup-job-nodes get dispatched into.
    """
    _index = None

    _backup_jobs = None
    _backup_job_in_pole_position = None
    _activity_led = None
    _mutex = None

    def __init__(self, parent, index):
        super(BMQueueView, self).__init__(parent)

        self._index = index

        self._backup_jobs = []
        self._mutex = QtCore.QMutex()

        parent.set_central_widget(self)
        self._init_ui()

    @property
    def main_view(self):
        return self.parent().parent().parent()

    def _init_ui(self):
        self._update_size()
        self._activity_led = QtGui.QFrame(self.parent().parent())
        self._activity_led.setGeometry(0, 378, 80, 3)
        # CSS
        self.css = ((self._activity_led,
                     None,
                     "border-radius: 1px; background: #%s",
                     {"has_no_focus":
                      {"enabled":
                       ((bs.config.PALETTE[10], ),
                        (bs.config.PALETTE[10], ),
                        (bs.config.PALETTE[10], ),
                        )
                       },
                      "has_focus":
                      {"enabled":
                       ((bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        (bs.config.PALETTE[4], ),
                        )
                       }
                      }
                     ),
                    )

    def _move_backup_job_to_pole_position(self):
        """ ..

        Moves the backup-job at index 0 of the queue into the pole-position.
        """
        if (len(self._backup_jobs) > 0 and
                not self._backup_job_in_pole_position):
            backup_job_to_move = self._backup_jobs[0]
            self._mutex.lock()
            self._backup_jobs.pop(0)
            self._backup_job_in_pole_position = backup_job_to_move
            backup_job_to_move.setParent(self.parent().parent())
            self._mutex.unlock()
            # update queue
            self._update_size()
            self._update_backup_jobs_positions()
            self._update_position()
            # reposition backup-job
            self._mutex.lock()
            backup_job_to_move.move(0, 334)
            backup_job_to_move.show()
            self._mutex.unlock()
            backup_job_to_move.expand()
            backup_job_to_move.simulate()

    def _update_backup_jobs_positions(self):
        """ ..

        Updates the positions of all current backup-jobs, stacking them from
        the bottom up.
        """
        offset = self.height() - (31 * len(self._backup_jobs) - 1)
        if offset < 0:
            offset = 0
        self._mutex.lock()
        for backup_job in self._backup_jobs:
            x = 0
            y = offset + 31 * (len(self._backup_jobs) -
                               self._backup_jobs.index(backup_job, ) - 1)
            backup_job.move(x, y)
        self._mutex.unlock()

    def _update_position(self):
        """ ..

        Updates the queue widget's position.
        """
        self._mutex.lock()
        self.move(self.x(),
                  0 - (self.height() - self.parent().height()))
        self._mutex.unlock()

    def _update_size(self):
        """ ..

        Recalculates cumulative size of all positioned self._backup_jobs and
        resizes itself.
        """
        width = 0
        height = 0
        for backup_job in self._backup_jobs:
            width = max(width, backup_job.width())
            height += backup_job.height() + 1
        height -= 1
        # set to minimum size of scroll-area parent
        if height < self.parent().height():
            height = self.parent().height()
        self._mutex.lock()
        self.resize(width, height)
        self._mutex.unlock()

    def add_backup_job(self, backup_set):
        """ ..

        :param bs.ctrl.session.BackupSetCtrl BackupSetCtrl: The\
        :class:`~bs.ctrl.session.BackupSetCtrl` to dispatch as a new job.

        Adds a backup-set as a new job to the list.
        """
        widget = BMQueueJobView(self, backup_set)
        widget.show()
        self._mutex.lock()
        self._backup_jobs.append(widget)
        self._mutex.unlock()
        # update queue
        self._update_size()
        self._update_backup_jobs_positions()
        self._update_position()
        # move to pole-position if it's the only current job in queue
        self._move_backup_job_to_pole_position()

    def has_backup_set_in_queue(self, backup_set):
        """ ..

        :param bs.ctrl.session.BackupSet backup_set: The\
        :class:`~bs.ctrl.session.BackupSet` to check for whether or not it\
        currently already exists in any of the queues.

        Checks whether or not the ``backup_set`` is already queued up
        (or active).
        """
        with QtCore.QMutexLocker(self._mutex):
            if backup_set in [x.backup_set for x in self._backup_jobs]:
                return True
            if (self._backup_job_in_pole_position and
                    self._backup_job_in_pole_position.backup_set == backup_set):
                return True
            return False

    def next_backup_job_to_pole_position(self):
        """ ..

        Retires the current backup-job in the pole position and moves the
        next in the queue to it if queue is not empty.
        """
        # delete current backup-job in pole-position
        if self._backup_job_in_pole_position:
            self._backup_job_in_pole_position.deleteLater()
            self._mutex.lock()
            self._backup_job_in_pole_position = None
            self._mutex.unlock()
            self._move_backup_job_to_pole_position()

    def remove_backup_job(self, backup_job):
        """ ..

        :param QtGui.QWidget backup_job: The\
        :class:`~bs.gui.view_backup_monitor.BMQueueJobView` to be\
        removed. This parameter can be overloaded by an ``int`` type, which\
        is then interpreted as the index in the\
        :class:`~bs.gui.view_backup_monitor.BMQueueJobView`-list of the\
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
        elif (len(self._backup_jobs) == backup_job_index + 1 and
              len(self._backup_jobs) > 1):
            self._backup_jobs[backup_job_index - 1].setFocus()
        elif self._backup_job_in_pole_position:
            self._backup_job_in_pole_position.setFocus()
        # delete
        self._mutex.lock()
        self._backup_jobs.pop(widget_index_to_remove)
        self._mutex.unlock()
        widget_to_remove.deleteLater()
        # update size, positions
        self._update_size()
        self._update_backup_jobs_positions()
        self._update_position()

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all \
        children.
        """
        # request exit for all children
        for child in self.children():
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        # pole_position:
        self._backup_job_in_pole_position.request_exit()
        return True


class BMQueueJobView(bs.gui.lib.BSFrame):
    """ ..

    :param QtGui.QWidget parent: The parent-``QtGui.QWidget`` for this object.
    :param bs.ctrl.session.BackupSetCtrl backup_set: The \
    :class:`~bs.ctrl.session.BackupSetCtrl` associated with this backup-job.

    The widget that represents a single job that sits in the queue.
    """

    _backup_set = None
    _progress_bar = None
    _title = None
    # queue of backup_ctrl that are due for processing
    __backup_ctrls_to_process = None
    _backup_ctrl_being_processed = None
    _pre_process_data_thread = None
    _pre_process_data_worker = None
    # these are global counts for all backup-controllers
    _byte_count_current = None
    _byte_count_total = None
    _updated_signal = QtCore.Signal(bs.ctrl.backup.BackupUpdateEvent)
    _finished_signal = QtCore.Signal(bs.ctrl.backup.BackupUpdateEvent)

    def __init__(self, parent, backup_set):
        """ ..

        """
        super(BMQueueJobView, self).__init__(parent)

        self._backup_set = backup_set
        self._title = self._backup_set.set_name
        self._byte_count_current = 0
        self._byte_count_total = 0

        # connect signals
        for backup_ctrl in self._backup_ctrls_to_process:
            backup_ctrl.updated_signal.connect(self.update_details_view_event)

        self._init_ui()

    @property
    def _backup_ctrls_to_process(self):
        """ ..

        :type: *list*

        A live list of backup-controllers to be processed.
        """
        if not self.__backup_ctrls_to_process:
            l = [self.backup_set.backup_ctrls[x] for x in self.backup_set.backup_sources]
            self.__backup_ctrls_to_process = l
        return self.__backup_ctrls_to_process

    @property
    def backup_set(self):
        """ ..

        :type: :class:`~bs.ctrl.session.BackupSetCtrl`
        :permissions: read

        The :class:`~bs.ctrl.session.BackupSetCtrl` represented by this \
        backup-job.
        """
        return self._backup_set

    @property
    def details_view(self):
        """ ..

        :type: :class:`~bs.gui.view_backup_monitor.BMDetailsView`
        """
        target = self
        while not isinstance(target, BMMainView):
            target = target.parent()
        return target.details_view

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

    def _init_ui(self):
        """ ..

        """
        # CSS
        self.setStyleSheet(".BMQueueJobView {background: #%s; "
                           "border-radius: 3px}"
                           % (bs.config.PALETTE[2], ))
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setGeometry(0, 0, 84, 30)
        self.resize(84, 30)
        # progress-bar
        self._progress_bar = QtGui.QFrame(self)
        self._progress_bar.setGeometry(1, 30, 2, 2)
        self._progress_bar.setStyleSheet("background: #%s"
                                         % (bs.config.PALETTE[10], ))
        # title
        self._title = QtGui.QLabel(self._title, self)
        self._title.move(11, 8)

    def backup(self):
        """ ..

        :rtype: *void*

        Runs a full backup on its associated\
        :class:`~bs.ctrl.backup.BackupCtrl`.
        """
        if not self._backup_ctrl_being_processed:
            index = 0
        else:
            index = self._backup_ctrls_to_process.index(self._backup_ctrl_being_processed) + 1
        # update details UI
        if index < len(self._backup_ctrls_to_process):
            backup_ctrl = self._backup_ctrls_to_process[index]
            self._backup_ctrl_being_processed = backup_ctrl
            worker = backup_ctrl.backup()[0]
            worker.finished.connect(self.backup,
                                    QtCore.Qt.QueuedConnection)
            worker.start()
        else:
            self._backup_ctrl_being_processed = None
            # move on to next backup-job
            self._get_queue().next_backup_job_to_pole_position()
            # reset details view
            self.details_view.reset()

    def deleteLater(self):
        """ ..

        Override.
        """
        # disconnect signals
        for backup_ctrl in self._backup_ctrls_to_process:
            backup_ctrl.updated_signal.disconnect(self.update_details_view_event)
        # reset focus back to main view, before deleting (queue focus indicator
        # would not get deactivated otherwise
        self._get_queue().main_view.setFocus()

        super(BMQueueJobView, self).deleteLater()

    def expand(self):
        """ ..

        Expands the widget to show extra details in pole-position.
        """
        self.resize(self.width(), 38)

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Executes exit calls to related objects and forwards request to all \
        children.
        """
        # request exit for all children
        for child in self.children() + self._backup_ctrls_to_process:
            try:
                if not child.request_exit():
                    return False
            except AttributeError:
                pass
        # exit threads
        if (self._pre_process_data_thread and
                self._pre_process_data_thread.is_alive()):
            if not self._backup_ctrl_being_processed.request_exit():
                return False
        return True

    def set_progress(self, current, total):
        """ ..

        :param int current: Current number of bytes processed.
        :param int total: Total number of bytes processed.

        Updates the widget to represent the progress in percent in its UI.
        """
        s = 0.0
        if total != 0:
            s = current / total
        width = round((self.width() - 2) * s)
        height = self._progress_bar.height()
        self._progress_bar.resize(width, height)

    def simulate(self):
        """ ..

        :rtype: *void*

        Initiates threaded pre-processing of this backup-job including all \
        associated :class:`~bs.ctrl.backup.BackupCtrl`. When completed, \
        invokes execution of the next next \
        :class:`~bs.gui.view_backup_monitor.BMQueueJobView` in queue.
        """
        if not self._backup_ctrl_being_processed:
            index = 0
        else:
            index = self._backup_ctrls_to_process.index(self._backup_ctrl_being_processed) + 1
        # update details UI
        if index < len(self._backup_ctrls_to_process):
            backup_ctrl = self._backup_ctrls_to_process[index]
            self._backup_ctrl_being_processed = backup_ctrl
            worker = backup_ctrl.simulate()[0]
            worker.finished.connect(self.simulate,
                                    QtCore.Qt.QueuedConnection)
            worker.start()
        else:
            self._backup_ctrl_being_processed = None
            # execute backup
            self.backup()

    def focusInEvent(self, e):
        """ ..

        :param QtCore.QEvent e:

        Override.
        """
        self.setStyleSheet(".BMQueueJobView {background: #%s; "
                           "border: 1px solid #%s; border-radius: 3px}"
                           % (bs.config.PALETTE[2],
                              bs.config.PALETTE[9], ))
        self._get_queue().focusInEvent(e)

    def focusOutEvent(self, e):
        """ ..

        :param QtCore.QEvent e:

        Override.
        """
        self.setStyleSheet(".BMQueueJobView {background: #%s; "
                           "border-radius: 3px}"
                           % (bs.config.PALETTE[2], ))
        self._get_queue().focusOutEvent(e)
        # reset details view
        self.details_view.reset()

    def keyReleaseEvent(self, e):
        """ ..

        :param QtCore.QEvent e:

        Override.
        """
        # del
        if e.matches(QtGui.QKeySequence.Delete):
            # remove itself
            if isinstance(self.parent(), BMQueueView):
                self.parent().remove_backup_job(self)

        super(BMQueueJobView, self).keyReleaseEvent(e)

    def update_details_view_event(self, e):
        """ ..

        :param bs.ctrl.backup.BackupUpdateEvent e:
        :rtype: *void*

        This event emits when the currently running backup-execution updates
        (this happens after each fractional process has been completed; this
        could be the hashing- or encryption-/compression-/packing-process
        etc. and the step is dependent on the corresponding buffer-size
        used; gets evoked often throughout the processing of one (especially
        larger) file). Populates the *details-view* of the *backup-monitor*
        with details about the last processed file.
        """
        # CALC DATA
        current = 0
        total = 0
        for backup_ctrl in self._backup_ctrls_to_process:
            if backup_ctrl.byte_count_current:
                current += backup_ctrl.byte_count_current
            if backup_ctrl.byte_count_total:
                total += backup_ctrl.byte_count_total
        # all done, reset counts
        if current == total:
            for backup_ctrl in self._backup_ctrls_to_process:
                backup_ctrl.reset()
            current = 0
            total = 0
        # UPDATE
        # own progress-bar
        self.set_progress(current, total)
        # details view
        if self.hasFocus():
            # file-path
            if (e.file_path and
                    self.details_view.current_item_path != e.file_path):
                self.details_view.current_item_path = e.file_path
            # progress-bar
            self.details_view.progress_bar.set_progress(current,
                                                        total)


class BMDetailsView(QtGui.QWidget):
    """ ..

    :param QtGui.QWidget parent: The widget to be assigned as the parent.

    The widget displaying the active backup-job's details.
    """

    _current_item_path = None
    _current_item_path_label = None
    _mutex = None
    _progress_bar = None

    def __init__(self, parent):
        """ ..

        """
        super(BMDetailsView, self).__init__(parent)

        self._mutex = QtCore.QMutex()

        self._init_ui()

    def _init_ui(self):
        """ ..

        """
        self.move(0, 381)
        self._progress_bar = BMDetailsProgressBarView(self)
        # current item path
        widget = QtGui.QLabel("Current Item", self)
        widget.setStyleSheet("font-weight: bold; color: #%s"
                             % (bs.config.PALETTE[2], ))
        widget.move(15, 20)
        self._current_item_path_label = QtGui.QLabel(self)
        self._current_item_path_label.move(112, 20)
        self._current_item_path_label.setMinimumWidth(400)
        self._current_item_path_label.setStyleSheet("color: #%s"
                                                    % (bs.config.PALETTE[9], ))

    @property
    def current_item_path(self):
        """ ..

        :type: str
        :permissions: read/write
        """
        return self._current_item_path

    @current_item_path.setter
    def current_item_path(self, arg):
        """ ..

        """
        self._mutex.lock()
        self._current_item_path = arg
        self._current_item_path_label.setText(self._current_item_path)
        self._mutex.unlock()

    @property
    def progress_bar(self):
        """ ..

        :type: :class:`~bs.gui.view_backup_monitor.BMDetailsProgressBarView`
        """
        return self._progress_bar

    def reset(self):
        """ ..

        Resets (empties) this widgets and its GUI elements.
        """
        # empty item-path
        self.current_item_path = ""
        # empty progress-bar
        self._progress_bar.set_progress(0, 0)


class BMDetailsProgressBarView(QtGui.QWidget):
    """ ..

    :param QtGui.QWidget parent: The widget to be assigned as the parent.

    The progress bar for the details view.
    """

    _bar_bg = None
    _bar_marker = None
    _bar_capacity_min_label = None
    _bar_capacity_max = None
    _bar_capacity_max_label = None
    _bar_capacity_current = None
    _bar_capacity_current_label = None
    _mutex = None

    def __init__(self, parent):
        """ ..

        """
        super(BMDetailsProgressBarView, self).__init__(parent)

        self._bar_capacity_current = 0
        self._bar_capacity_max = 0
        self._mutex = QtCore.QMutex()

        self._init_ui()

    @property
    def bar_capacity_current(self):
        """ ..

        :type: *int*
        :permissions: *read*

        The accumulated capacity backed-up so far (, displayed on the \
        "0%-mark" of the progress-bar).
        """
        return self._bar_capacity_current

    @property
    def bar_capacity_max(self):
        """ ..

        :type: *int*
        :permissions: *read*

        The maximum capacity accumulated and to be backed up displayed on \
        the "100%-mark" of the progress-bar.
        """
        return self._bar_capacity_max

    def _init_ui(self):
        """ ..

        """
        self.resize(699, 134)
        self.move(14, 57)
        # progress bar
        self._bar_bg = QtGui.QFrame(self)
        self._bar_bg.resize(675, 3)
        self._bar_bg.move(0, 16)
        self._bar_bg.setStyleSheet("border-radius: 1px; background: #%s"
                                   % (bs.config.PALETTE[9]))
        # progress bar marker
        self._bar_marker = QtGui.QFrame(self)
        self._bar_marker.resize(0, 3)
        self._bar_marker.move(0, 16)
        self._bar_marker.setStyleSheet("background: #%s"
                                       % (bs.config.PALETTE[4]))
        # labels
        self._bar_capacity_min_label = QtGui.QLabel(self)
        self._bar_capacity_min_label.setStyleSheet("color: #%s"
                                                   % (bs.config.PALETTE[9]))
        self._bar_capacity_min_label.move(0, 0)
        self._bar_capacity_min_label.resize(75, 30)
        self._bar_capacity_min_label.setAlignment(QtCore.Qt.AlignTop)
        self._bar_capacity_min_label.setAlignment(QtCore.Qt.AlignLeft)
        self._bar_capacity_max_label = QtGui.QLabel(self)
        self._bar_capacity_max_label.setStyleSheet("color: #%s"
                                                   % (bs.config.PALETTE[9]))
        self._bar_capacity_max_label.move(600, 0)
        self._bar_capacity_max_label.resize(75, 30)
        self._bar_capacity_max_label.setAlignment(QtCore.Qt.AlignTop)
        self._bar_capacity_max_label.setAlignment(QtCore.Qt.AlignRight)
        self._bar_capacity_current_label = QtGui.QLabel("0.00%", self)
        self._bar_capacity_current_label.setStyleSheet("color: #%s"
                                                       % (bs.config.PALETTE[9]))
        self._bar_capacity_current_label.resize(50,
                                                self._bar_capacity_current_label.height())
        self._bar_capacity_current_label.setAlignment(QtCore.Qt.AlignRight)
        self._bar_capacity_current_label.move(0, 22)
        self.set_progress(0, 0)

    def set_progress(self, current, total):
        """ ..

        :param int current: The size in bytes currently completed.
        :param int total: The total size in bytes.

        Sets the progress bar and its labels to the corresponding state. \
        Calculates percentage autonomously.
        """
        # update progress-indicator
        if total == 0:
            percentage = 0
        else:
            percentage = float(current / total)
        # set marker position
        w = round(percentage * self._bar_bg.width())
        h = self._bar_marker.height()
        self._mutex.lock()
        self._bar_marker.resize(w, h)
        self._mutex.unlock()
        # set current percentage position
        if self._bar_marker.x() < 13:
            x = -15
        elif x > self._bar_bg.width() - 13 - 13:
            x = self._bar_bg.width() - 52
        else:
            x = self._bar_marker.x() - 28
        y = self._bar_capacity_current_label.y()
        self._mutex.lock()
        self._bar_capacity_current_label.move(x, y)
        # update private vars
        if self._bar_capacity_current != current:
            self._bar_capacity_current = current
        if self._bar_capacity_max != total:
            self._bar_capacity_max = total
        self._mutex.unlock()
        # update labels
        text_formatted_min = "0"
        text_formatted_max = bs.utils.format_data_size(self._bar_capacity_max)
        if self._bar_capacity_max == 0:
            text_formatted_min = ""
            text_formatted_max = ""
        self._mutex.lock()
        self._bar_capacity_min_label.setText(text_formatted_min)
        self._bar_capacity_max_label.setText(text_formatted_max)
        self._bar_capacity_current_label.setText("%.2f%s"
                                                 % (percentage * 100.00, "%", ))
        self._mutex.unlock()
