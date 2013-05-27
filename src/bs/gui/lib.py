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

import bs.config

from PySide import QtCore, QtGui


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
        and all subtypes or to whole hierarcy.
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
        for child in self.children():
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
        super(BSArrow, self).__init__(source.parentWidget())

        self._source = source
        self._target = target
        self._source.assign_to_arrow(self)
        self._target.assign_to_arrow(self)

        self._stroke_width = 3
        self._stroke_style = QtCore.Qt.SolidLine
        self._line_cap = QtCore.Qt.RoundCap
        self._join_style = QtCore.Qt.MiterJoin
        # INIT UI
        self.lower()
        self.show()

    @property
    def target(self):
        return self._target

    def paintEvent(self, e=None):
        """ * """
        path = QtGui.QPainterPath()
        # p1a
        p1a = self._source.parentWidget().mapToGlobal(self._source.geometry().center())
        p1a.setX(p1a.x() + self._source.width() / 2 + 10)
        p1a = self.mapFromGlobal(p1a)
        # p2a
        p2a = self._target.parentWidget().mapToGlobal(self._target.geometry().center())
        p2a.setX(p2a.x() - self._target.width() / 2 - 10)
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


class BSNode(BSDraggable):
    """ * """

    _layout = None
    _title = None
    _arrows = None

    def __init__(self, parent):
        super(BSNode, self).__init__(parent)

        self._arrows = []

        # title
        self._title = QtGui.QLabel("")
        # layout
        self._layout = QtGui.QGridLayout(self)
        self._layout.addWidget(self._title, 0, 0, 1, 1)
        self._layout.setSpacing(1)
        self._layout.setContentsMargins(5, 5, 5, 41)
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
    def title_size(self):
        pass

    @title_size.setter
    def title_size(self, size):
        self._title.setStyleSheet("margin-left: 1px; margin-top: %spx; margin-bottom: %spx; font-size: %spx; color: #%s"
                                  % (
                                     size / 9,
                                     size - 8,
                                     size,
                                     bs.config.PALETTE[0]))
        self._layout.setContentsMargins(self._layout.contentsMargins().left(),
                                        self._layout.contentsMargins().top(),
                                        self._layout.contentsMargins().right(),
                                        size * 2 + 5)

    def add_item(self, bs_node_item):
        """ *
        Adds bs_node_item to the widget.
        """
        pos_y = self._layout.count()
        self._layout.addWidget(bs_node_item, pos_y, 0, 1, 1)

    def assign_to_arrow(self, arrow):
        """ * """
        if not arrow in self._arrows:
            self._arrows.append(arrow)

    def draw_arrows(self):
        """ * """
        if not len(self._arrows) == 0:
            for arrow in self._arrows:
                arrow.refresh()

    def mousePressEvent(self, e):
        """ * """
        self.raise_()
        super(BSNode, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        """ * """
        self.draw_arrows()
        super(BSNode, self).mouseMoveEvent(e)


class BSNodeItem(BSFrame):
    """ * """

    _layout = None
    _title = None
    _btn_del = None

    def __init__(self, parent):
        super(BSNodeItem, self).__init__(parent)

        # layout
        self._layout = QtGui.QGridLayout(self)
        self._layout.setContentsMargins(11, 0, 6, 0)
        self._layout.setRowMinimumHeight(0, 28)
        self._title = QtGui.QLabel("")
#        self._title.setStyleSheet("color: #%s" % (bs.config.PALETTE[3], ))
        self._layout.addWidget(self._title, 0, 0, 1, 1)
        # CSS
#        self.setStyleSheet("BSNodeItem {background: #%s}"
#                           % (bs.config.PALETTE[1], ))

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

#    def enterEvent(self, e):
#        """ * """
#        super(BSNodeItem, self).enterEvent(e)
#
#        self.setStyleSheet("BSNodeItem {background: #%s}"
#                           % (bs.config.PALETTE[0]))
#        self._title.setStyleSheet("QLabel {color: #%s}"
#                                  % (bs.config.PALETTE[4], ))

    def leaveEvent(self, e):
        """ * """
        super(BSNodeItem, self).leaveEvent(e)

#        self.setStyleSheet("BSNodeItem {background: #%s}"
#                           % (bs.config.PALETTE[1]))
#        self._title.setStyleSheet("QLabel {color: #%s}"
#                                  % (bs.config.PALETTE[3], ))

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
