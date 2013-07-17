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

""" * """
from PySide import QtCore, QtGui
import binascii
import bs.config
import bs.gui.view_sets
import re


class BSFrame(QtGui.QFrame):
    """ * """

    _css = None
    _css_enabled_default = None
    _css_enabled_hover = None
    _css_enabled_active = None
    _css_disabled = None

    def __init__(self, parent):
        super(BSFrame, self).__init__(parent)

    @property
    def css(self):
        return self._css

    @css.setter
    def css(self, arg):
        """ *
        argument 1 needs to be of following format:
        (
         (object,
          class_constraint,
          pattern,
          (
           (dataset1),
           (dataset2),
           ...
          )
         ),
         ...
        )
        where `class_constraint` needs to be either ".", "" or `None`.
        This decides whether the css is constrained to the object only/object
        and all sub-types or to whole hierarchy.
        "." will wrap the css definitions into `.classname {...}`: constrains to instances of class only
        "" will wrap the css definitions into `classname {...}` constrains to any instance of class or subtype
        `None` will not wrap the css definitions: only constrains to object hierarchy (leaving out
        `[.]class {}` completely in css string).
        """
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
        """ *
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
        """ *
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
        """ *
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
        """ *
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
        """ *
        Compiles CSS style code-string from self.css and sets css on all
        nodes saved in self.css.
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
        """ *
        Compiles CSS style code-string from self.css and sets css on all
        nodes saved in self.css.
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
    """ * """

    _pos_offset = None  # stores local pos offset for drag-ability

    def __init__(self, parent):
        super(BSDraggable, self).__init__(parent)

    def mousePressEvent(self, e):
        """ * """
        self._pos_offset = e.pos()

    def mouseMoveEvent(self, e):
        """ * """
        if e.buttons() == QtCore.Qt.MouseButton.LeftButton:
            x = self.mapToParent(e.pos()).x() - self._pos_offset.x()
            y = self.mapToParent(e.pos()).y() - self._pos_offset.y()
            self.setGeometry(x,
                             y,
                             self.width(),
                             self.height())


class BSCanvas(BSDraggable):
    """ * """
    def __init__(self, parent):
        super(BSCanvas, self).__init__(parent)

        parent.resizeSignal.connect(self.resizeEvent)

    def mouseMoveEvent(self, e):
        """ * """
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
        """ * """
        self.setGeometry(0, 0, self.width(), self.height())
        super(BSCanvas, self).mouseReleaseEvent(e)

    def resizeEvent(self, e):
        """ * """
        self.setGeometry(0,
                         0,
                         self.parent().width(),
                         self.parent().height())
        super(BSCanvas, self).resizeEvent(e)


class BSArrow(QtGui.QWidget):
    """ * """
    _source = None
    _target = None

    _stroke_width = None
    _line_cap = None
    _join_style = None

    def __init__(self, source, target):
        super(BSArrow, self).__init__(source.parent())

        self._source = source
        self._target = target
        self._source.assign_to_arrow_as_source(self)
        self._target.assign_to_arrow_as_target(self)

        # associate with parent (canvas)
        self.parent().arrow_widgets.append(self)
        # style set-up
        self._stroke_width = 3
        self._stroke_style = QtCore.Qt.SolidLine
        self._line_cap = QtCore.Qt.RoundCap
        self._join_style = QtCore.Qt.MiterJoin
        # INIT UI
        self.lower()
        self.show()

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, arg):
        self._source = arg

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, arg):
        self._target = arg

    def delete(self):
        """ *
        Removes the arrow from associated objects (source, target) and deletes
        the widget.
        """
        # unassign arrow from source, target
        self._source.unassign_from_arrow(self)
        self._target.unassign_from_arrow(self)
        self.parent().arrow_widgets.pop(self.parent().arrow_widgets.index(self))
        self.deleteLater()

    def paintEvent(self, e=None):
        """ * """
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
        """ * """
        margin = 100
        self.setGeometry(self._target.geometry().united(self._source.geometry()).x() - margin,
                         self._target.geometry().united(self._source.geometry()).y() - margin,
                         self._target.geometry().united(self._source.geometry()).width() + margin * 2,
                         self._target.geometry().united(self._source.geometry()).height() + margin * 2
                         )


class BSArrowCarrier(BSDraggable):
    """ * """
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
        """ *
        Registers object's signals.
        """
        self._app.global_mouse_pos_signal.connect(self.move_to)
        self._app.global_mouse_press_signal.connect(self.record_mouse_pos)
        self._app.global_mouse_release_signal.connect(self.mouse_release_action)

    def unregister_signals(self):
        """ *
        Unregisters object's signals. Called, when object is not used anymore.
        """
        self._app.global_mouse_pos_signal.disconnect(self.move_to)
        self._app.global_mouse_press_signal.disconnect(self.record_mouse_pos)
        self._app.global_mouse_release_signal.disconnect(self.mouse_release_action)

    def _reset(self):
        """ * """
        self._source = None
        self._arrow_inbound = None

    def move_to(self, e):
        """ * """
#        super(BSArrowCarrier, self).mouseMoveEvent(e)
        # coordinates in parent's space
        x = self.parent().mapFromGlobal(e.globalPos()).x()
        y = self.parent().mapFromGlobal(e.globalPos()).y()
        self.setGeometry(x + 5,
                         y + 5,
                         self.width(),
                         self.height())
        self.draw_arrows()

    def record_mouse_pos(self, widget, e):
        """ *
        Records current mouse position for figuring out if mouse has moved or
        not in other methods.
        """
        self._mouse_press_global_pos = e.globalPos()

    def mouse_release_action(self, widget, e):
        """ *
        Connects the arrow to the node widget.
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
                isinstance(widget_node, bs.gui.lib.BSNode):
                # BUILDING LOGIC CHECKS
                # start node
                is_allowed_start_node = False
                needs_reconnect = False
                if isinstance(widget_node, bs.gui.view_sets.BSSource) or\
                   isinstance(widget_node, bs.gui.view_sets.BSFilter):
                    if not widget_node.arrow_outbound:
                        is_allowed_start_node = True
                    else:
                        needs_reconnect = True
                # finalize node
                is_allowed_finalize_node = False
                if isinstance(widget_node, bs.gui.view_sets.BSFilter) or\
                   isinstance(widget_node, bs.gui.view_sets.BSTarget):
                    is_allowed_finalize_node = True
                node_to_test = widget_node
                while node_to_test.arrow_outbound:
                    node_to_test = node_to_test.arrow_outbound.target
                    if node_to_test == self._source:
                        is_allowed_finalize_node = False
                        break
                    # if reconnecting and target is the carrier itself, abort
                    if isinstance(node_to_test, bs.gui.lib.BSArrowCarrier):
                        is_allowed_finalize_node = False
                        break
                # EXECUTE ACTION BASED ON CONTEXT
                # if start action
                if not self._source:
                    if widget_aux:
                        if is_allowed_start_node:
                            self.connect_start(widget_node)
                        elif needs_reconnect:
                            self.connect_reconnect(widget_node)
                # else if connection action
                else:
                    if is_allowed_finalize_node:
                        self.connect_finalize(widget_node)
            # cancel
            elif self._source:
                self.connect_cancel()

    def connect_start(self, source):
        """ * """
        self._source = source
        self._arrow_inbound = BSArrow(self._source, self)

    def connect_reconnect(self, source):
        self._source = source
        self._arrow_inbound = self._source.arrow_outbound
        self._arrow_inbound.target.unassign_from_arrow(self._arrow_inbound)
        self._arrow_inbound.target = self

    def connect_finalize(self, target):
        """ * """
        # update data on controllers
        if isinstance(self._source, bs.gui.view_sets.BSSource):
            # re-associate with new backup_filter/backup_target
            if isinstance(target, bs.gui.view_sets.BSTarget):
                self._source.backup_source.backup_source_ass[self._bs.backup_set_current] = target.backup_targets
            else:
                self._source.backup_source.backup_source_ass[self._bs.backup_set_current] = target.backup_filter
        if isinstance(self._source, bs.gui.view_sets.BSFilter):
            # re-associate with new backup_filter/backup_target
            if isinstance(target, bs.gui.view_sets.BSTarget):
                self._source.backup_filter.backup_filter_ass[self._bs.backup_set_current] = target.backup_targets
            else:
                self._source.backup_filter.backup_filter_ass[self._bs.backup_set_current] = target.backup_filter
        # trigger modified signal
        self._bs.set_modified()
        target.assign_to_arrow_as_target(self._arrow_inbound)
        self._arrow_inbound.target = target
        self._arrow_inbound.refresh()
        self._reset()

    def connect_cancel(self):
        # remove association
        if isinstance(self._source, bs.gui.view_sets.BSSource):
            self._source.backup_source.backup_source_ass[self._bs.backup_set_current] = None
        elif isinstance(self._source, bs.gui.view_sets.BSFilter):
            self._source.backup_filter.backup_filter_ass[self._bs.backup_set_current] = None
        # delete arrow
        self._arrow_inbound.delete()
        # re-initialize self
        self._reset()
        self._bs.set_modified()

    def assign_to_arrow_as_target(self, arrow):
        """ * """
        self._arrow_inbound = arrow

    def unassign_from_arrow(self, arrow):
        """ * """
        if arrow == self._arrow_inbound:
            self._arrow_inbound = None

    def draw_arrows(self):
        """ * """
        if self._arrow_inbound:
            self._arrow_inbound.refresh()

    def mouseMoveEvent(self, e):
        """ *
        Override.
        """
        pass


class BSNode(BSDraggable):
    """ * """
    _bs_sets_canvas = None
    _app = None

    _layout = None
    _title = None
    _arrows_inbound = None
    _arrow_outbound = None
    _title_size = None
    _conn_pad = None
    _custom_contents_container = None # used by custom nodes to place custom contents into
#    _mouse_press_global_pos = None  # Holds mouse pos when key was pressed to compare against pos when released
    _border_hex_orig = None

    def __init__(self, bs_sets_canvas, app, has_conn_pad=False):
        super(BSNode, self).__init__(bs_sets_canvas)

        self._bs_sets_canvas = bs_sets_canvas
        self._app = app

        self._arrows_inbound = []

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        # title
        self._title = QtGui.QLabel("")
        # custom_contents_container
        self._custom_contents_container = QtGui.QWidget()
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
        # Drop shadow
        gfx = QtGui.QGraphicsDropShadowEffect(self)
        gfx.setOffset(0)
        gfx.setColor(QtGui.QColor(20, 20, 20))
        gfx.setBlurRadius(4)
        self.setGraphicsEffect(gfx)

    @property
    def title_text(self):
        return self._title.text()

    @title_text.setter
    def title_text(self, text):
        self._title.setText(text)

    @property
    def arrow_inbound(self):
        return self._arrows_inbound

    @property
    def arrow_outbound(self):
        return self._arrow_outbound

    @property
    def title_size(self):
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

    def assign_to_arrow_as_source(self, arrow):
        """ * """
        if arrow is not self._arrow_outbound:
            self._arrow_outbound = arrow

    def assign_to_arrow_as_target(self, arrow):
        """ * """
        if not arrow in self._arrows_inbound:
            self._arrows_inbound.append(arrow)

    def unassign_from_arrow(self, arrow):
        """ *
        Unassigns `arrow` from this widget.
        """
        if arrow in self._arrows_inbound:
            self._arrows_inbound.pop(self._arrows_inbound.index(arrow))
        elif arrow is self._arrow_outbound:
            self._arrow_outbound = None

    def draw_arrows(self):
        """ * """
        if not len(self._arrows_inbound) == 0:
            for arrow_inbound in self._arrows_inbound:
                arrow_inbound.refresh()
        if self._arrow_outbound:
            self._arrow_outbound.refresh()

    def mousePressEvent(self, e):
        """ * """
        super(BSNode, self).mousePressEvent(e)

#        self._mouse_press_global_pos = e.globalPos()
        self.raise_()

    def mouseMoveEvent(self, e):
        """ * """
        self.draw_arrows()
        super(BSNode, self).mouseMoveEvent(e)

    def focusInEvent(self, e):
        """ * """
        self._border_hex_orig = re.search("(border\:[0-9a-zA-Z\ ]+\#)([a-zA-Z0-9]{1,6})", self.styleSheet()).group(2)
        self.setStyleSheet("BSNode {border: 1px solid #333333}")

    def focusOutEvent(self, e):
        """ * """
        self.setStyleSheet("BSNode {border: 1px solid #%s}" % (self._border_hex_orig, ))

    def keyPressEvent(self, e):
        """ * """
        if e.matches(QtGui.QKeySequence.Delete):
            self.remove_node()

    def remove_node(self):
        """ *
        Removes the node's arrows. Additional operations take place on
        inheriting objects.
        """
        # delete arrows
        while len(self._arrows_inbound) > 0:
            arrow_inbound = self._arrows_inbound[0]
            arrow_inbound.delete()
        if self._arrow_outbound:
            self._arrow_outbound.delete()


class BSNodeConnPad(QtGui.QFrame):
    """ * """

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
        icon.setStyleSheet(css)
        icon.setMinimumSize(QtCore.QSize(14, 14))
        self._layout.addWidget(icon, 0, 0, 1, 1)

    def mouseReleaseEvent(self, e):
        """ *
        Override
        """


class BSNodeItem(BSFrame):
    """ * """

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
        return self._title

    @property
    def title_text(self):
        """ * """
        return self._title.text()

    @title_text.setter
    def title_text(self, title):
        """ * """
        self._title.setText(title)

    def mouseMoveEvent(self, e):
        """ *
        Override to ignore
        """


class BSNodeItemButton(BSFrame):
    """ * """
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
        """ * """
        self.setStyleSheet("background: #%s; color: #%s"
                           % (bs.config.PALETTE[1],
                              bs.config.PALETTE[4], ))

    def leaveEvent(self, e):
        """ * """
        self.setStyleSheet("background: None; color: #%s"
                           % (bs.config.PALETTE[6], ))


class BSMessageBox(QtGui.QMessageBox):
    """ * """

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
