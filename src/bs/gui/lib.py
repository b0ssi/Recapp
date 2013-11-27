# -*- coding: utf-8 -*-
###############################################################################
##    bs.gui.nodes                                                           ##
###############################################################################
###############################################################################
##    Author:         Bossi                                                  ##
##                    © 2013 All rights reserved                             ##
##                    www.isotoxin.de                                        ##
##                    frieder.czeschla@isotoxin.de                           ##
##    Creation Date:  May 24, 2013                                           ##
##    Version:        0.0.000000                                             ##
##                                                                           ##
##    Usage:                                                                 ##
##                                                                           ##
###############################################################################
""" ..

This package contains all abstract *view-classes*.
"""

from PySide import QtCore, QtGui

import bs.config
import logging
import math
import re


class BSFrame(QtGui.QFrame):
    """ ..

    :param PySide.QtGui.QWidget parent:

    This is a stylizable superclass that features a few extra methods for \
    easy CSS stye management across multiple states/events, visual control \
    of enabled/disabled node state etc.
    """

    _css = None
    _css_enabled_default = None
    _css_enabled_hover = None
    _css_enabled_active = None
    _css_disabled = None

    def __init__(self, parent):
        super(BSFrame, self).__init__(parent)

    @property
    def css(self):
        """
        :type: *tuple*
        :permissions: *read/write*

        The CSS code assigned to the node. The format of this tuple is as \
        follows:

        argument 1 needs to be of following format:

        .. code-block:: python

            (
                (object,
                    class_constraint,
                    pattern,
                    (
                        (dataset1),
                        (dataset2),
                        (dataset3),
                        (dataset4),
                        (dataset5),
                        (dataset6),
                    ),
                ),
                ...
            )

        where

        - `class_constraint` needs to be either `"."`, `""` or `None`. This \
        decides whether the css is constrained to the object only/object and \
        all inheriting sub-types or to the object's hierarchy tree.

            - `"."` will wrap the css definitions into `.classname {...}`: \
                constrains to instances of class only.
            - `""` will wrap the css definitions into `classname {...}` \
                constrains to any instance of class or subtype
            - `None` will not wrap the css definitions: only constrains to \
                object hierarchy (leaving out `[.]class {}` completely in css string).

        - `pattern` is a pattern-string that uses the six `dataset#` tuples \
        to substitute its placeholders with corresponding data, e.g.: \

            - Pattern: `"color: #%s, background: %s"`
            - dataset1: `("012345", "3px solid green", )`
            - dataset2: `...`

        The six datasets represent the following states, respectively:

        - normal (in enabled mode)
        - hover (in enabled mode)
        - active (in enabled mode)
        - normal (in disabled mode)
        - hover (in disabled mode)
        - active (in disabled mode)

        By the use of this method complex, object-state dependent styles can \
        be easily defined so that multiple nested objects' styles can be \
        controlled through the events of only the one top parent e.g.
        """
        return self._css

    @css.setter
    def css(self, arg):
        out = []
        for dataset in arg:
            # extract data
            obj = dataset[0]
            class_constraint = dataset[1]
            pattern = dataset[2]
            data = dataset[3]
            # extract stylesheets
            css_definitions = []
            for n in data:
                if not class_constraint is None:
                    css_definition = "%s%s {" % (class_constraint, str(obj.__class__.__name__), )
                    css_definition += pattern % n
                    css_definition += "}"
                else:
                    css_definition = pattern % n
                css_definitions.append(css_definition)
            out.append((obj, css_definitions, ))
        self._css = out
        # set initial style
        self.setEnabled(self.isEnabled())

    def enterEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Compiles CSS style code-string from self.css and sets css on all
        nodes saved in self.css.
        """
        super(BSFrame, self).enterEvent(e)

        if self.css:
            if self.isEnabled():
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][1]
                    obj.setStyleSheet(css_definition)
            else:
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][4]
                    obj.setStyleSheet(css_definition)

    def leaveEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Compiles CSS style code-string from self.css and sets css on all
        nodes saved in self.css.
        """
        super(BSFrame, self).leaveEvent(e)

        if self.css:
            if self.isEnabled():
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][0]
                    obj.setStyleSheet(css_definition)
            else:
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][3]
                    obj.setStyleSheet(css_definition)

    def mousePressEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Compiles CSS style code-string from self.css and sets css on all
        nodes saved in self.css.
        """
        super(BSFrame, self).mousePressEvent(e)

        if self.css:
            if self.isEnabled():
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][2]
                    obj.setStyleSheet(css_definition)
            # disabled widgets don't receive mousePressEvent or mouseReleaseEvent

    def mouseReleaseEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Compiles CSS style code-string from self.css and sets css on all
        nodes saved in self.css.
        """
        super(BSFrame, self).mouseReleaseEvent(e)

        if self.css:
            if self.isEnabled():
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][1]
                    obj.setStyleSheet(css_definition)
            # disabled widgets don't receive mousePressEvent or mouseReleaseEvent

    def setEnabled(self, mode=True):
        """ ..

        :param bool mode:
        :rtype: *void*

        Overrides :meth:`PySide.QtGui.QWidget.setDisabled`; also sets CSS.
        """
        if self.css:
            if mode:
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][0]
                    obj.setStyleSheet(css_definition)
            else:
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][3]
                    obj.setStyleSheet(css_definition)

        super(BSFrame, self).setEnabled(mode)

    def setDisabled(self, mode=True):
        """ ..

        :param bool mode:
        :rtype: *void*

        Overrides :meth:`PySide.QtGui.QWidget.setDisabled`; also sets CSS.
        """
        if self.css:
            if not mode:
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][0]
                    obj.setStyleSheet(css_definition)
            else:
                for dataset in self.css:
                    obj = dataset[0]
                    css_definition = dataset[1][3]
                    obj.setStyleSheet(css_definition)

        super(BSFrame, self).setDisabled(mode)


class BSDraggable(BSFrame):
    """ ..

    :param PySide.QtGui.QWidget parent:

    Superclass for all draggables in the project.
    """

    _pos_offset = None  # stores local pos offset for drag-ability

    def __init__(self, parent):
        super(BSDraggable, self).__init__(parent)

    def mousePressEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Records mouse position for cross-checking on other mouse events on \
        this class.
        """
        self._pos_offset = e.pos()

        super(BSDraggable, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Performs the actual drag on mouse moves.
        """
        if e.buttons() == QtCore.Qt.MouseButton.LeftButton:
            x = self.mapToParent(e.pos()).x() - self._pos_offset.x()
            y = self.mapToParent(e.pos()).y() - self._pos_offset.y()
            self.setGeometry(x,
                             y,
                             self.width(),
                             self.height())


class BSArrow(QtGui.QWidget):
    """ ..

    :param bs.gui.view_sets.BS bs:
    :param bs.gui.lib.BSNode source:
    :param bs.gui.lib.BSNode target:

    This class draws an arrow between two :class:`BSNode`, *source* and \
    *target*.
    """
    _bs = None
    _source = None
    _target = None

    _stroke_width = None
    _line_cap = None
    _join_style = None
    _btn_del = None

    def __init__(self, bs, source, target):
        super(BSArrow, self).__init__(source.parent())

        self._bs = bs
        self._source = source
        self._target = target
        self._source.assign_to_arrow_as_source(self)
        self._target.assign_to_arrow_as_target(self)

        # associate with parent (canvas)
        self.parent().bs_arrow_widgets.append(self)
        # style set-up
        self._stroke_width = 3
        self._stroke_style = QtCore.Qt.SolidLine
        self._line_cap = QtCore.Qt.RoundCap
        self._join_style = QtCore.Qt.MiterJoin
        # INIT UI
        self.lower()
        self.show()
        # Delete button
        self._btn_del = BSArrowBtnDel(self._bs, self, self.parent())

    @property
    def source(self):
        """
        :type: :class:`BSNode`
        :permissions: *read/write*

        The source node the arrow connects from (visual origin of arrow).
        """
        return self._source

    @source.setter
    def source(self, arg):
        self._source = arg

    @property
    def target(self):
        """
        :type: :class:`BSNode`
        :permissions: *read/write*

        The target node the arrow connects to (visual destination of arrow).
        """
        return self._target

    @target.setter
    def target(self, arg):
        self._target = arg

    def delete(self):
        """ ..

        :rtype: *void*

        Removes the arrow from associated :class:`BSNode` (*source*, \
        *target*) and deletes the widget.
        """
        # unassign arrow from source, target
        self._source.unassign_from_arrow(self)
        self._target.unassign_from_arrow(self)
        self.parent().bs_arrow_widgets.pop(self.parent().bs_arrow_widgets.index(self))
        self._btn_del.deleteLater()
        self.deleteLater()

    def paintEvent(self, e=None):
        """ ..

        :rtype: *void*

        Override of :class:`PySide.QtGui.QWidget.paintEvent`.
        """
        path = QtGui.QPainterPath()
        # p1a
        p1a = self._source.parentWidget().mapToGlobal(self._source.geometry().center())
        p1a.setX(p1a.x() + self._source.width() / 2 + 2)
        p1a = self.mapFromGlobal(p1a)
        # p2a
        p2a = self._target.parentWidget().mapToGlobal(self._target.geometry().center())
        p2a.setX(p2a.x() - self._target.width() / 2 - 5)
        p2a = self.mapFromGlobal(p2a)
        # calc distance
        vec1 = QtGui.QVector2D(p1a)
        vec2 = QtGui.QVector2D(p2a)
        point_distance = int((vec2 - vec1).length())
        if point_distance > 500:
            point_distance = 500
        # p1b
        p1b = QtCore.QPoint(p1a.x(), p1a.y())
        p1b.setX(p1b.x() + point_distance / 2)
        # p2b
        p2b = QtCore.QPoint(p2a.x(), p2a.y())
        p2b.setX(p2b.x() - point_distance / 2)
        # draw path
        path.moveTo(p1a.x(),
                    p1a.y()
                    )
        path.cubicTo(p1b.x(), p1b.y(),
                   p2b.x(), p2b.y(),
                   p2a.x(), p2a.y())
        path = self._draw_arrow_head(path, p2a.x(), p2a.y())
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(199, 199, 255),
                         self._stroke_width,
                         self._stroke_style,
                         self._line_cap,
                         self._join_style)
        painter.setPen(pen)
        painter.drawPath(path)
        # del button
        side_len = 12
        btn_del_pos = self.mapToParent(QtCore.QPoint(p1a.x() + (p2a.x() - p1a.x()) / 2 - side_len / 2,
                                                     p1a.y() + (p2a.y() - p1a.y()) / 2 - side_len / 2
                                                     )
                                       )
        self._btn_del.setGeometry(btn_del_pos.x(),
                                  btn_del_pos.y(),
                                  side_len,
                                  side_len)

        super(BSArrow, self).paintEvent(e)

    def _draw_arrow_head(self, path, current_x, current_y):
        """ * """
        wing_length = 5
        path.moveTo(current_x - 1, current_y - 1)
        path.lineTo(current_x - wing_length, current_y - wing_length)
        path.moveTo(current_x - 1, current_y + 1)
        path.lineTo(current_x - wing_length, current_y + wing_length)
        return path

    def refresh(self):
        """ ..

        :rtype: *void*

        Refreshes this :class:`BSArrow`'s geometry, invoking a repaint event.
        """
        margin = 100
        self.setGeometry(self._target.geometry().united(self._source.geometry()).x() - margin,
                         self._target.geometry().united(self._source.geometry()).y() - margin,
                         self._target.geometry().united(self._source.geometry()).width() + margin * 2,
                         self._target.geometry().united(self._source.geometry()).height() + margin * 2
                         )


class BSArrowBtnDel(BSFrame):
    """ ..

    :param bs.gui.view_sets.BS bs:
    :param bs.gui.lib.BSArrow bs_arrow:
    :param bs.gui.lib.BSCanvas bs_canvas:

    This is the button-widget to be used to interact with :class:`BSArrow`, \
    usually to delete the arrow.
    """
    _bs = None
    _bs_arrow = None
    _bs_canvas = None

    _mouse_press_global_pos = None

    def __init__(self, bs, bs_arrow, bs_canvas):
        super(BSArrowBtnDel, self).__init__(bs_canvas)

        self._bs = bs
        self._bs_arrow = bs_arrow
        self._bs_canvas = bs_canvas

        self._init_ui()

    def _init_ui(self):
        css = "BSFrame {background: #C7C7FF; border-radius: 6px}"
        css += "BSFrame:hover {background: #FF0000}"
        self.setStyleSheet(css)
        self.setGeometry(0, 0, 0, 0)  # will display at default initial widget size in canvas' origin if drawing arrow is out of screen space otherwise
        self.show()
        self._bs_canvas.restack()

    def mouseMoveEvent(self, e):
        # Override-implementation to suppress and prevent event from \
        # traveling down the hierarchy.
        pass

    def mousePressEvent(self, e):
        # Records global mouse-position to be used on \
        # :meth:`mouseReleaseEvent` to check if mouse has moved in the mean \
        # time.
        self._mouse_press_global_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        #Deletes the arrow on mouse-button-release, unless the mouse changed \
        # position since its :meth:`mousePressEvent`.
        if self._mouse_press_global_pos == e.globalPos():
            if e.button() & QtCore.Qt.MouseButton.LeftButton:
                # remove association
                self._bs_arrow.source.backup_entity.disassociate(self._bs.backup_set_current,
                                                                 self._bs_arrow.target.backup_entity)
                # delete gui arrow
                self._bs_arrow.delete()


class BSArrowCarrier(BSDraggable):
    """ ..

    :param bs.gui.lib.BSCanvas parent:
    :param bs.gui.window_main.Application app:
    :param bs.gui.view_sets.BS bs:

    An invisible widget that "picks up" and "carries" the new arrow when \
    newly connecting two nodes.
    """
    _app = None
    _bs = None

    _source = None
    _arrow_inbound = None
    _mouse_press_global_pos = None

    def __init__(self, parent, app, bs):
        super(BSArrowCarrier, self).__init__(parent)

        self._app = app
        self._bs = bs

        self.setStyleSheet("background: red")
        self.setGeometry(0, 0, 50, 50)
        # gonnect to global_mouse_pos_signal
        self.register_signals()

        self.show()
        self.lower()

    def register_signals(self):
        """ ..

        :rtype: *void*

        Registers object's signals.
        """
        self._app.global_mouse_pos_signal.connect(self.move_to)
        self._app.global_mouse_press_signal.connect(self.record_mouse_pos)
        self._app.global_mouse_release_signal.connect(self.mouse_release_action)

    def unregister_signals(self):
        """ ..

        :rtype: *void*

        Unregisters object's signals. Called when object is not used anymore.
        """
        self._app.global_mouse_pos_signal.disconnect(self.move_to)
        self._app.global_mouse_press_signal.disconnect(self.record_mouse_pos)
        self._app.global_mouse_release_signal.disconnect(self.mouse_release_action)

    def _reset(self):
        """ * """
        self._source = None
        self._arrow_inbound = None

    def move_to(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        This re-implemented event makes sure this :class:`BSArrowCarrier` \
        stays with the mouse pointer.
        """
        # only move when no button pressed:
        # when button pressed and connection arrow is active, canvas would
        # move this carrier plus global mouseMove signal this carrier as well
        # incl. the arrow, leading to polarized jumps of canvas.
        if e.buttons() == QtCore.Qt.MouseButton.NoButton:
            # coordinates in parent's space
            x = self.parent().mapFromGlobal(e.globalPos()).x()
            y = self.parent().mapFromGlobal(e.globalPos()).y()
            self.setGeometry(x + 5,
                             y + 5,
                             self.width(),
                             self.height())
            self.draw_arrows()

    def record_mouse_pos(self, widget, e):
        """ ..

        :param PySide.QtGui.QWidget widget:
        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Records current mouse position for figuring out if mouse has moved or
        not in other methods.
        """
        self._mouse_press_global_pos = e.globalPos()

    def mouse_release_action(self, widget, e):
        """ ..

        :param PySide.QtGui.QWidget widget:
        :param PySide.QtCore.QEvent e:

        Handles the connection event when either a target node or a blank \
        space on the :class:`BSCanvas` is clicked. In the former case the \
        intermittent arrow is connected to the :class:`BSNode`, if the node \
        is valid, in the latter the connection process is canceled and \
        :meth:`connect_cancel` is called.
        """
        if (e.globalPos() == self._mouse_press_global_pos) and\
            e.button() == QtCore.Qt.MouseButton.LeftButton:
            # try to get node base-object
            widget_node = None  # (Parent-node-widget) of clicked widget
            widget_aux = None  # (clicked node (if child of widget_node)
            while not widget is self.parent():
                if isinstance(widget, BSNode):
                    widget_node = widget
                    break
                # capture widget_aux
                if isinstance(widget, BSNodeConnPad):
                    widget_aux = widget
                try:
                    widget = widget.parent()
                except:
                    widget = self.parent()
            # if clicked on node
            if widget_node and\
                isinstance(widget_node, BSNode):
                # BUILDING LOGIC CHECKS
                # finalize node
                is_allowed_finalize_node = False
                if self._source:
                    import bs.gui.view_sets
                    if widget_node.backup_entity not in self._source.backup_entity.backup_entity_ass[self._bs.backup_set_current] and\
                        not isinstance(widget_node, bs.gui.view_sets.BSSource):
                        is_allowed_finalize_node = True
                    # check for illegal round-trip connection-attempt
                    if not isinstance(widget_node.backup_entity, list):
                        objects_to_test = [x for x in widget_node.backup_entity.backup_entity_ass[self._bs.backup_set_current]]
                        objects_tested = []
                        while len(objects_to_test) > 0:
                            # get get associations from next object in list
                            if not isinstance(objects_to_test[0], list):
                                for obj in objects_to_test[0].backup_entity_ass[self._bs.backup_set_current]:
                                    if obj not in (objects_to_test + objects_tested) and\
                                        not isinstance(obj, list):
                                        objects_to_test.append(obj)
                            # check: is start object
                            if objects_to_test[0] == self._source.backup_entity:
                                is_allowed_finalize_node = False
                                break
                            objects_tested.append(objects_to_test[0])
                            objects_to_test.pop(0)
                # EXECUTE ACTION BASED ON CONTEXT
                # if start action
                if not self._source:
                    if widget_aux:
                        self.connect_start(widget_node)
                # else if connection action
                else:
                    if is_allowed_finalize_node:
                        self.connect_finalize(widget_node)
            # cancel
            elif self._source:
                self.connect_cancel()

    def connect_start(self, source):
        """ ..

        :param bs.gui.lib.BSNode source:
        :rtype: *void*

        Initializes a new interactive connection process, creating an \
        intermittent :class:`BSArrow`, binding it to the :class:`BSNode` this \
        process was initialized with and this :class:`BSArrowCarrier`.
        """
        self._source = source
        self._arrow_inbound = BSArrow(self._bs, self._source, self)

    def connect_reconnect(self, source):
        """
        :param bs.gui.lib.BSNode source:
        :rtype: *void*

        **DEPRECATED, NOT IN USE ANYMORE**

        Picks up an already connected arrow from its connected *target* and \
        binds it to this :class:`BSArrowCarrier` so that it is ready to be \
        connected to a :class:`BSNode` again.
        """
        self._source = source
        self._arrow_inbound = self._source.arrow_outbound
        self._arrow_inbound.target.unassign_from_arrow(self._arrow_inbound)
        self._arrow_inbound.target = self

    def connect_finalize(self, target):
        """ ..

        :param bs.gui.lib.BSNode target:
        :rtype: *void*

        Finalizes the connection process, connecting the intermittent \
        :class:`BSArrow` to the target :class:`BSNode` that was clicked on.
        """
        # update data on controllers
        # re-associate with new backup_filter/backup_target
        self._source.backup_entity.associate(self._bs.backup_set_current, target.backup_entity)
        # trigger modified signal
        self._bs.set_modified()
        target.assign_to_arrow_as_target(self._arrow_inbound)
        self._arrow_inbound.target = target
        self._arrow_inbound.refresh()
        self._reset()

    def connect_cancel(self):
        """
        :rtype: *void*

        Cancels an active connection-process where the intermittent \
        :class:`BSArrow` is connected to the target-node as well as this \
        :class:`BSArrowCarrier`, deleting the arrow.
        """
        # delete arrow
        self._arrow_inbound.delete()
        # re-initialize self
        self._reset()

    def assign_to_arrow_as_target(self, arrow):
        """ ..

        :param bs.gui.lib.BSArrow arrow:
        :rtype: *void*

        Assigns this :class:`BSArrowCarrier` to *arrow* as a *target-node*. \
        Binding this node to the mouse-cursor-position, this makes the new \
        arrow follow the mouse cursor.
        """
        self._arrow_inbound = arrow

    def unassign_from_arrow(self, arrow):
        """ ..

        :param bs.gui.lib.BSArrow arrow:
        :rtype: void

        Unassigns the carrier from its arrow, if currently assigned.
        """
        if arrow == self._arrow_inbound:
            self._arrow_inbound = None

    def draw_arrows(self):
        """ ..

        :rtype: *void*

        If exists, redraws the intermittent arrow connected to this \
        :class:`BSArrowCarrier`.
        """
        if self._arrow_inbound:
            self._arrow_inbound.refresh()


class BSCanvas(BSDraggable):
    """ ..

    :param PySide.QtGui.QWidget parent:

    Canvas superclass. Supports certain features to manage drag & dropable \
    :class:`BSNode` on its canvas.
    """
    def __init__(self, parent):
        super(BSCanvas, self).__init__(parent)

        parent.resizeSignal.connect(self.resizeEvent)

    def mouseMoveEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Drags the canvas including all child nodes relative to mouse move \
        events.
        """
        if e.buttons() == QtCore.Qt.MouseButton.LeftButton:
            for child in self.children():
                if not isinstance(child, QtGui.QAction):
                    child.setGeometry(child.x() - (self._pos_offset.x() - e.x()),
                                      child.y() - (self._pos_offset.y() - e.y()),
                                      child.width(),
                                      child.height()
                                      )
            self._pos_offset = e.pos()
            self.setGeometry(0, 0, self.width(), self.height())
        super(BSCanvas, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Resets the canvas' geometry after a drag event to crop the parent \
        (window).
        """
        self.setGeometry(0, 0, self.width(), self.height())
        super(BSCanvas, self).mouseReleaseEvent(e)

    def resizeEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Adjusts own geometry to parent when resized.
        """
        self.setGeometry(0,
                         0,
                         self.parent().width(),
                         self.parent().height())
        super(BSCanvas, self).resizeEvent(e)


class BSMessageBox(QtGui.QMessageBox):
    """ ..

    :param PySide.QtGui.QMessageBox.Icon icon:
    :param str title:
    :param str message:

    A modal message box used to display confirmations or simple \
    notifications. Not much different from :class:`PySide.QtGui.QMessageBox` \
    except for its custom CSS stylizing ability.
    """

    def __init__(self, icon, title, message):
        super(BSMessageBox, self).__init__(icon, title, message)

        css = "BSMessageBox {background: #%s}"\
              "BSMessageBox QPushButton {background: #%s; color: #%s; width: 70px; height: 20px; border-radius: 3px}"\
              "BSMessageBox QPushButton:hover {background: #%s; color: #%s}"\
              % (bs.config.PALETTE[2],
                 bs.config.PALETTE[1],
                 bs.config.PALETTE[3],
                 bs.config.PALETTE[0],
                 bs.config.PALETTE[4],
                 )
        self.setStyleSheet(css)


class BSNode(BSDraggable):
    """ ..

    :param bs.gui.view_sets.BS bs:
    :param bs.gui.view_sets.BSSetsCanvas bs_sets_canvas:
    :param bs.gui.window_main.Application app:
    :param bool has_conn_pad:

    The superclass to all floating, draggable nodes. Offers node-specific \
    features such as arrow-connectors, arrow-association-management, node \
    association management, etc.
    """
    _bs = None
    _bs_sets_canvas = None
    _app = None

    _layout = None
    _title = None
    _arrows_inbound = None
    _arrows_outbound = None
    _title_size = None
    _conn_pad = None
    _custom_contents_container = None # used by custom nodes to place custom contents into
    _border_hex_orig = None

    def __init__(self, bs, bs_sets_canvas, app, has_conn_pad=False):
        """ ..

        """
        super(BSNode, self).__init__(bs_sets_canvas)

        self._bs = bs
        self._bs_sets_canvas = bs_sets_canvas
        self._app = app

        self._arrows_inbound = []
        self._arrows_outbound = []

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        # title
        self._title = QtGui.QLabel("")
        # custom_contents_container

        class CustomContentsContainer(QtGui.QWidget):
            def request_exit(self):
                """ ..

                :rtype: *bool*

                Executes exit calls to related objects and forwards request \
                to all children.
                """
                # request exit for all children
                for child in self.children():
                    try:
                        if not child.request_exit():
                            return False
                    except AttributeError as e:
                        pass
                return True
        self._custom_contents_container = CustomContentsContainer(self)
        self._custom_contents_container._layout = QtGui.QGridLayout(self._custom_contents_container)
        # layout
        self._layout = QtGui.QGridLayout(self)
        self._layout.addWidget(self._title, 0, 0, 1, 1)
        # conn_pad
        if has_conn_pad:
            self._conn_pad = BSNodeConnPad()
            self._layout.addWidget(self._conn_pad, 0, 1, 2, 1)
        self._layout.addWidget(self._custom_contents_container, 1, 0, 1, 1)
        self._layout.setSpacing(1)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(170)
        # Drop shadow
        gfx = QtGui.QGraphicsDropShadowEffect(self)
        gfx.setOffset(0)
        gfx.setColor(QtGui.QColor(20, 20, 20))
        gfx.setBlurRadius(4)
        self.setGraphicsEffect(gfx)

    @property
    def arrows_inbound(self):
        """
        :type: *list*

        A list of all inbound :class:`BSArrow` connecting to this node as a \
        target.
        """
        return self._arrows_inbound

    @property
    def arrows_outbound(self):
        """
        :type: *list*

        A list of all outbound :class:`BSArrow` connecting from this node as a \
        source.
        """
        return self._arrows_outbound

    def assign_to_arrow_as_source(self, arrow):
        """ ..

        :param bs.gui.lib.BSArrow arrow:
        :rtype: *void*

        Assigns a :class:`BSArrow` to this node as an *outbound* arrow, \
        making this node a *source*.
        """
        if arrow is not self._arrows_outbound:
            self._arrows_outbound.append(arrow)

    def assign_to_arrow_as_target(self, arrow):
        """ ..

        :param bs.gui.lib.BSArrow arrow:
        :rtype: *void*

        Assigns a :class:`BSArrow` to this node as an *inbound* arrow, \
        making this node a *target*.
        """
        if not arrow in self._arrows_inbound:
            self._arrows_inbound.append(arrow)

    def draw_arrows(self):
        """ ..

        :rtype: *void*

        Invokes connected in- and outbound arrows to redraw themselves.
        """
        if not self._arrows_inbound == []:
            for arrow_inbound in self._arrows_inbound:
                arrow_inbound.refresh()
        if not self._arrows_outbound == []:
            for arrow_outbound in self._arrows_outbound:
                arrow_outbound.refresh()

    def remove_node(self):
        """ ..

        :rtype: *void*

        Remove the node's arrows. Additional operations take place on \
        inheriting objects.
        """
        # request exits
        if self.request_exit():
            # remove association
            for arrow_inbound in self._arrows_inbound:
                arrow_inbound.source.backup_entity.disassociate(self._bs.backup_set_current, self.backup_entity)
            # delete arrows
            while len(self._arrows_inbound) > 0:
                arrow_inbound = self._arrows_inbound[0]
                arrow_inbound.delete()
            while len(self._arrows_outbound) > 0:
                arrow_outbound = self._arrows_outbound[0]
                arrow_outbound.delete()
            self._bs.set_modified()
        else:
            logging.warning("%s: Node could net be removed as active threads"\
                            "did not shut down properly." % (self.__class__.__name__, ))

    def request_exit(self):
        """ ..

        :rtype: *bool*

        Set in place to be overridden by inheriting objects. This method is \
        to be called externally to request an exit on threaded operations \
        running on this object.
        """
        return True

    @property
    def title_text(self):
        """
        :type: *str*
        :permissions: *read/write*

        The title's text.
        """
        return self._title.text()

    @title_text.setter
    def title_text(self, text):
        self._title.setText(text)

    @property
    def title_size(self):
        """
        :type: *int*
        :permissions: *read/write*

        The title's size in px.
        """
        return self._title_size

    @title_size.setter
    def title_size(self, size):
        self._title_size = size
        self._title.setStyleSheet("margin-left: 1px; margin-top: %spx; margin-bottom: %spx; font-size: %spx; color: #%s"
                                  % (self._title_size / 9,
                                     self._title_size - 8,
                                     self._title_size,
                                     bs.config.PALETTE[0]))
        self._layout.setContentsMargins(self._layout.contentsMargins().left(),
                                        self._layout.contentsMargins().top(),
                                        self._layout.contentsMargins().right(),
                                        self._layout.contentsMargins().bottom()) #self._title_size * 2 + 5)
        self._title.setMinimumHeight(self._title_size + (self._title_size / 9) + (self._title_size - 8))

    def unassign_from_arrow(self, arrow):
        """ ..

        :param bs.gui.lib.BSArrow arrow:
        :rtype: *void*

        Unassign `arrow` from this widget.
        """
        # pop from in- outbound list
        if arrow in self._arrows_inbound:
            self._arrows_inbound.pop(self._arrows_inbound.index(arrow))
        elif arrow in self._arrows_outbound:
            self._arrows_outbound.pop(self._arrows_outbound.index(arrow))
        self._bs.set_modified()

    def focusInEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Mark the node visually when focusing in on it.
        """
        self._border_hex_orig = re.search("(border\:[0-9a-zA-Z\ ]+\#)([a-zA-Z0-9]{1,6})", self.styleSheet()).group(2)
        self.setStyleSheet("BSNode {border: 1px solid #%s}" % (bs.config.PALETTE[9], ))

    def focusOutEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Unmark the node visually when focusing out of it.
        """
        self.setStyleSheet("BSNode {border: 1px solid #%s}" % (self._border_hex_orig, ))

    def keyPressEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Perform actions on node in reaction to key-presses:

        - [del]: Delete the node.
        """
        if e.matches(QtGui.QKeySequence.Delete):
            self.remove_node()

        super(BSNode, self).keyPressEvent(e)

    def mousePressEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Raise the node above its siblings.
        """
        super(BSNode, self).mousePressEvent(e)

#        self._mouse_press_global_pos = e.globalPos()
        self.raise_()

    def mouseMoveEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Redraw connected arrows on mouse move.
        """
        self.draw_arrows()
        super(BSNode, self).mouseMoveEvent(e)


class BSNodeConnPad(QtGui.QFrame):
    """ ..

    The interactive widget on a node used to start connectino-arrows from.
    """

    _layout = None

    def __init__(self):
        super(BSNodeConnPad, self).__init__()

        self._init_ui()

    def _init_ui(self):
        # layout
        self._layout = QtGui.QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        # connect-icon
        icon = QtGui.QFrame()
        css = "QFrame {border-top-right-radius: 2px; border-bottom-right-radius: 2px;  background: #%s}" % (bs.config.PALETTE[1], )
        css += "QFrame:hover {background: #%s}" % (bs.config.PALETTE[4], )
        self.setMaximumWidth(14)
        self.setMinimumWidth(14)
        self.setStyleSheet(css)
#         icon.setMinimumSize(QtCore.QSize(14, 14))
#         self._layout.addWidget(icon, 0, 0, 1, 1)

    def mouseMoveEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Empty override
        """

    def mousePressEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Empty override
        """

    def mouseReleaseEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Empty override
        """


class BSNodeItem(BSFrame):
    """ ..

    :param PySide.QtGui.QWidget parent:

    An elementary sub-item of a :class:`BSNode`.
    """

    _layout = None
    _title = None
    _btn_del = None

    def __init__(self, parent):
        super(BSNodeItem, self).__init__(parent)

        self.setMinimumHeight(28)
        # layout
        self._layout = QtGui.QGridLayout(self)
        self._layout.setContentsMargins(11, 0, 6, 0)
        self._title = QtGui.QLabel("")
        self._layout.addWidget(self._title, 0, 0, 1, 1)

    @property
    def title(self):
        """
        :type: :class:`PySide.QtGui.QLabel`

        The :class:`BSNodeItem`'s title :class:`PySide.QtGui.QLabel`.
        """
        return self._title

    @property
    def title_text(self):
        """ ..

        :rtype: *str*
        :permissions: *read/write*

        The title's text.
        """
        return self._title.text()

    @title_text.setter
    def title_text(self, title):
        """ ..

        """
        self._title.setText(str(title))

    def mouseMoveEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Empty override.
        """


class BSNodeItemButton(BSFrame):
    """ ..

    :param PySide.QtGui.QWidget parent:
    :param str title:

    Used to create a nested button on a :class:`BSNodeItem`.
    """
    _title = None

    _layout = None

    def __init__(self, parent, title):
        super(BSNodeItemButton, self).__init__(parent)

        self._title = title

        self._init_ui()

    def _init_ui(self):
        self._layout = QtGui.QGridLayout(self)
        title = QtGui.QLabel(self._title)
        self._layout.addWidget(title, 0, 0, 1, 1)
        # CSS
        self.setStyleSheet("color: #%s"
                           % (bs.config.PALETTE[6], ))

    def enterEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Set the defined *hover* StyleSheet.
        """
        self.setStyleSheet("background: #%s; color: #%s"
                           % (bs.config.PALETTE[1],
                              bs.config.PALETTE[4], ))

    def leaveEvent(self, e):
        """ ..

        :param PySide.QtCore.QEvent e:
        :rtype: *void*

        Set the defined *normal* StyleSheet.
        """
        self.setStyleSheet("background: None; color: #%s"
                           % (bs.config.PALETTE[6], ))


class ScrollArea(QtGui.QFrame):
    """ ..

    :param QtGui.QWidget parent: The parent widget the scroll view is to \
    be assigned to.

    This is a fixed-size scroll frame that allows one :attr:`central_widget` \
    to hold arbitrary contents that can scroll if the :attr:`central_widget` \
    is larger than the this scroll-view in either one or both directions x \
    and y.
    """

    _central_widget = None
    _central_widget_animation = None
    _scroll_bar_v = None
    _scroll_bar_h = None
    _scroll_bar_animation = None
    _scroll_bar_animation_property = None

    def __init__(self, parent):
        super(ScrollArea, self).__init__(parent)

        self._init_ui()

    def _init_ui(self):
        # scroll bars
        self._scroll_bar_h = QtGui.QFrame(self)
        self._scroll_bar_h.resize(0, 0)
        self._scroll_bar_v = QtGui.QFrame(self)
        self._scroll_bar_v.resize(0, 0)
        self._scroll_bar_animation = QtCore.QPropertyAnimation(self, "_scroll_bar_animation_property", self)
        self._scroll_bar_animation.setDuration(200)
#         self.setFocusPolicy(QtCore.Qt.ClickFocus)

    @property
    def central_widget(self):
        """ ..

        The central widget frame that holds all the contents for the \
        scroll-view. Should be scaled explicitly and will cause the \
        scroll-area to scroll x-/y-wise repsectively if larger than \
        scroll-view in corresponding direction(s).
        """
        return self._central_widget

    def _calculate_scroll(self, delta_x, delta_y):
        """ ..

        :param int delta_y: Distance in px to travel. Can be negative (scroll \
        down) or positive (scroll up).

        Calculates the exact cp position (0...1) to scroll to, incl. top/end \
        cap-offs and calls the scroll method.
        """
        scroll_margin_x = self._central_widget.width() - self.width()
        scroll_margin_y = self._central_widget.height() - self.height()
        new_x_f = 0.0
        new_y_f = 0.0
        # build scroll-to percentages
        new_x = self._central_widget.x() + delta_x
        new_y = self._central_widget.y() + delta_y
        if scroll_margin_x > 0:
            new_x_f = abs(self._central_widget.x() + delta_x) / scroll_margin_x
        if scroll_margin_y > 0:
            new_y_f = abs(self._central_widget.y() + delta_y) / scroll_margin_y
        # call scroll_to
        if (new_y <= 0 and \
            new_y + self._central_widget.height() >= self.height()) or \
            (new_x <= 0 and \
            new_x + self._central_widget.width() >= self.width()):
            self.scroll_to(new_x_f, new_y_f)
        elif delta_x > new_x > 0:
            self.scroll_to(0.0, new_y_f)
        elif self.width() < self._central_widget.x() + self._central_widget.width() < self.width() + abs(delta_x) and \
            delta_x < 0:
            self.scroll_to(1.0, new_y_f)
        elif delta_y > new_y > 0:
            self.scroll_to(new_x_f, 0.0)
        elif self.height() < self._central_widget.y() + self._central_widget.height() < self.height() + abs(delta_y) and \
            delta_y < 0:
            self.scroll_to(new_x_f, 1.0)

    def _get_scroll_bar_alpha(self):
        return 0

    def _set_scroll_bar_alpha(self, arg):
        """ ..

        :param int arg: Transparency. This is an 8-bit int.
        """
        self._scroll_bar_v.setStyleSheet("QWidget {background: rgba(0, 0, 0, %s); border-radius: 2px}" % (arg, ))
        self._scroll_bar_h.setStyleSheet("QWidget {background: rgba(0, 0, 0, %s); border-radius: 2px}" % (arg, ))

    _scroll_bar_animation_property = QtCore.Property("int", _get_scroll_bar_alpha, _set_scroll_bar_alpha)

    def _update_scroll_bars(self, scroll_to_x_f, scroll_to_y_f):
        """ ..

        Updates scrollbars' positions and sizes.
        """
        if self._central_widget.width() > 0 and self._central_widget.height() > 0:
            # these are offsets by which the scrollbars are shortened and limited to move into the lr corner (necessary, if both are visible for them to not intersect 
            scroll_bar_h_corner_offset = None
            scroll_bar_v_corner_offset = None
            # deactivate scrollbars if unnecessary (widget width/height <= width/height of scroll area
            if self._central_widget.width() <= self.width():
                self._scroll_bar_h.setHidden(True)
                scroll_bar_v_corner_offset = 0
            else:
                self._scroll_bar_h.setHidden(False)
                scroll_bar_v_corner_offset = 4
            if self._central_widget.height() <= self.height():
                self._scroll_bar_v.setHidden(True)
                scroll_bar_h_corner_offset = 0
            else:
                self._scroll_bar_v.setHidden(False)
                scroll_bar_h_corner_offset = 4
            # horizontal scrollbar
            self._scroll_bar_h.raise_()
            width = math.floor(self.width() / self._central_widget.width() * self.width()) - scroll_bar_h_corner_offset
            self._scroll_bar_h.resize(width, 4)
            x = math.floor((self.width() - scroll_bar_h_corner_offset - width) * scroll_to_x_f)
            y = self.height() - 4
            self._scroll_bar_h.move(x, y)
            # vertical scrollbar
            self._scroll_bar_v.raise_()
            height = math.floor(self.height() / self._central_widget.height() * self.height()) - scroll_bar_v_corner_offset
            self._scroll_bar_v.resize(4, height)
            x = self.width() - 5
            y = math.floor((self.height() - scroll_bar_v_corner_offset - height) * scroll_to_y_f)
            self._scroll_bar_v.move(x, y)

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
            except AttributeError as e:
                pass
        return True

    def scroll_to(self, x, y, animate=True):
        """ ..

        :param float x: The x-position (0...1) to scroll to.
        :param float y: The y-position (0...1) to scroll to.
        :param bool animate: Whether or not to animate the transition.

        At 0, the central widget is repositioned so that the top/left border \
        sits on the top/left border of the scroll area, respectively. If 1, \
        the widget is repositioned so that the bottom/right border sits on \
        the bottom/right border of the scroll widget, respectively.
        """
        # calc scroll attributes
        scroll_margin_x = self._central_widget.width() - self.width()
        if scroll_margin_x < 0: scroll_margin_x = 0
        scroll_margin_y = self._central_widget.height() - self.height()
        if scroll_margin_y < 0: scroll_margin_y = 0
        new_x = 0 - x * scroll_margin_x
        new_y = 0 - y * scroll_margin_y
        # execute scroll
        if animate:
            self._central_widget_animation.setStartValue(self.central_widget.pos())
            self._central_widget_animation.setEndValue(QtCore.QPoint(new_x, new_y))
            self._central_widget_animation.start()
        else:
            self._central_widget.move(new_x, new_y)
        self._update_scroll_bars(x, y)

    def set_central_widget(self, central_widget):
        """ ..

        :param QtGui.QWidget central_widget: The primary widget that hosts \
        all remaining contents for the scroll area.

        Sets the central widget to :attr:`central_widget`.

        .. Note:: Currently the central-widget cannot be resized, the \
        scroll-area would have to get fully updated. Implement if necessary.
        """
        self._central_widget = central_widget
        # animation setup
        self._central_widget_animation = ScrollAreaAnimation(self._central_widget, "pos", self)
        self._central_widget_animation.setDuration(100)

    def keyPressEvent(self, e):
        if e.matches(QtGui.QKeySequence.MoveToPreviousLine):
            self._calculate_scroll(0, 40)
        if e.matches(QtGui.QKeySequence.MoveToNextLine):
            self._calculate_scroll(0, -40)
        if e.matches(QtGui.QKeySequence.MoveToPreviousChar):
            self._calculate_scroll(40, 0)
        if e.matches(QtGui.QKeySequence.MoveToNextChar):
            self._calculate_scroll(-40, 0)

    def wheelEvent(self, e):
        # scroll widget up/down
        if e.orientation() == e.orientation().Vertical:
            delta = e.delta() / 3
            self._calculate_scroll(0, delta)


class ScrollAreaAnimation(QtCore.QPropertyAnimation):
    """ ..

    This is the animation object that animates the central-widget in the \
    scroll area.
    """
    _finish_timer = None

    def __init__(self, target_widget, property_name, parent):
        super(ScrollAreaAnimation, self).__init__(target_widget,
                                                  property_name,
                                                  parent)
        self._finish_timer = QtCore.QTimer(self)
        self._finish_timer.setInterval(2000)
        self._finish_timer.timeout.connect(self._finalize_animation)

    def _finalize_animation(self):
        # hide scrollbars
        self.parent()._scroll_bar_animation.setStartValue(128)
        self.parent()._scroll_bar_animation.setEndValue(0)
        self.parent()._scroll_bar_animation.start()
        self._finish_timer.stop()

    def start(self):
        if not self._finish_timer.isActive():
            self.parent()._scroll_bar_animation.setStartValue(0)
            self.parent()._scroll_bar_animation.setEndValue(128)
            self.parent()._scroll_bar_animation.start()
        self._finish_timer.start()

        super(ScrollAreaAnimation, self).start()
