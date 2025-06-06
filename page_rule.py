import os
import sys

import numpy as np
import yaml

from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QSizePolicy,
        QFormLayout, QBoxLayout, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLineEdit, QLabel, QSpinBox, QPushButton, QTextEdit, QListWidget, QListWidgetItem, QCompleter,
        QStackedWidget, QMenuBar, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
        QSpacerItem, QCheckBox, QAbstractItemView, QGraphicsProxyWidget, QGraphicsScene, QGraphicsView,
        QGraphicsItem, QGraphicsLineItem)
from PySide6.QtCore import QUrl, QPropertyAnimation, QEasingCurve, QSize, Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import QIcon, Qt, QFont, QBrush, QColor, QPen, QPainter, QPainterPath
from PySide6.QtWebEngineWidgets import QWebEngineView

from utils.get_path import get_resource_path
from utils.parse_mile import mile_str2num, mile_num2str


class UiPageRule:
    def _setup_ui(self):
        self.page = QWidget()
        self.page_layout = QVBoxLayout(self.page)
        self.page_layout.setContentsMargins(0, 0, 0, 0)

        # define components
        self.scene = DiagramScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.pushbutton_add = QPushButton('添加节点')
        self.pushbutton_connect = QPushButton('连接模式')

        # tool
        self.tool_layout = QHBoxLayout()
        self.tool_layout.addWidget(self.pushbutton_add)
        self.tool_layout.addWidget(self.pushbutton_connect)
        self.tool_layout.addStretch()

        #  compile components
        self.page_layout.addLayout(self.tool_layout)
        self.page_layout.addWidget(self.view)


class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        # grid
        self.grid_lines = []
        self.grid_size = 20
        self.grid_visible = True

        self.draw_grid()

        # connection
        self.flag_connect = False
        self.tmp_connection_line: ConnectionLine | None = None
        self.start_point_item: ConnectionPoint | None = None

        self.connections = []

    def draw_grid(self):
        for line in self.grid_lines:
            self.removeItem(line)
        self.grid_lines.clear()

        pen = QPen(QColor(220, 220, 220), 1)
        for x in range(0, int(self.sceneRect().width()), self.grid_size):
            line = self.addLine(x, 0, x, self.sceneRect().height(), pen)
            self.grid_lines.append(line)

        for y in range(0, int(self.sceneRect().height()), self.grid_size):
            line = self.addLine(0, y, self.sceneRect().width(), y, pen)
            self.grid_lines.append(line)

    def update_size(self, size: QSize):
        self.setSceneRect(0, 0, size.width(), size.height())
        self.draw_grid()

    def mousePressEvent(self, event):
        select_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if isinstance(select_item, ConnectionPoint):
            if select_item.point_type == 'output':
                self.flag_connect = True
                # self.tmp_connection_line = ConnectionLine(select_item.parentItem())
                self.tmp_connection_line = ConnectionLine()
                self.addItem(self.tmp_connection_line)

                self.start_point_item = select_item
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.flag_connect:
            self.tmp_connection_line.update_line(self.start_point_item.scenePos(), event.scenePos())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        select_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if self.flag_connect:
            self.flag_connect = False
            if isinstance(select_item, ConnectionPoint):
                if select_item.point_type == 'input':
                    self.tmp_connection_line.update_points(self.start_point_item, select_item)
                    self.start_point_item.update_connection_line(self.tmp_connection_line)
                    select_item.update_connection_line(self.tmp_connection_line)
                else:
                    self.clear_tmp_line()
            else:
                self.clear_tmp_line()
        super().mouseReleaseEvent(event)

    def clear_tmp_line(self):
        self.removeItem(self.tmp_connection_line)
        self.tmp_connection_line = None


class NodeCombobox(QGraphicsProxyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        # define components
        self.title = QLabel('设计信息')
        self.combobox = QComboBox()
        self.combobox.addItems(['1', '222222222'])

        self.container_layout.addWidget(self.title, alignment=Qt.AlignHCenter)
        self.container_layout.addWidget(self.combobox)

        # set proxy widget
        self.setWidget(self.container)
        self.setFlag(QGraphicsProxyWidget.ItemIsMovable, True)
        self.setFlag(QGraphicsProxyWidget.ItemIsSelectable, True)

        # add connection node, must after setting proxy widget
        self.input_point = ConnectionPoint(self, 'input')
        self.output_point = ConnectionPoint(self, 'output')
        self.update_connection_points()

        # params for dragging and moving
        self.dragging = False
        self.drag_start_position = QPointF()
        self.original_position = QPointF()

        # above the background
        self.setZValue(1)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_position = event.scenePos()
            self.original_position = self.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.scenePos() - self.drag_start_position
            self.setPos(self.original_position + delta)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.update_connection_line(self.input_point)
            self.update_connection_line(self.output_point)
        return super().itemChange(change, value)

    def update_connection_line(self, connection_point):
        if connection_point.connection_line is not None:
            connection_point.connection_line.update_line()

    def set_style(self):
        self.combobox.setStyleSheet("""
            QComboBox {
                border: 1px solid gray;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                background-color: white;
            }
        """)

    def update_connection_points(self):
        self.input_point.setPos(0, self.boundingRect().height() / 2)
        self.output_point.setPos(self.boundingRect().width(), self.boundingRect().height() / 2)


class ConnectionPoint(QGraphicsItem):
    def __init__(self, parent=None, point_type="input"):
        super().__init__(parent)
        # point params
        self.radius = 6

        # point type: input or output
        self.point_type = point_type

        # allow hover event
        self.is_hovered = False
        self.setAcceptHoverEvents(True)

        #
        self.connection_line: ConnectionLine | None = None


    def boundingRect(self):
        """control the boundary of the graphics item """
        return QRectF(-self.radius, -self.radius,
                      self.radius * 2, self.radius * 2)

    def shape(self):
        """control the shape of the item: circle"""
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            color = QColor(255, 0, 0)
        elif self.is_hovered:
            color = QColor(224, 224, 224)
        else:
            color = QColor(153, 0, 255)

        # 绘制连接点
        painter.setPen(QPen(color, 1.5))
        painter.setBrush(QBrush(color.lighter(150)))
        painter.drawEllipse(self.boundingRect())

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        event.accept()
        # super().mousePressEvent(event)

    def update_connection_line(self, line_item):
        self.connection_line = line_item

class ConnectionLine(QGraphicsLineItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = None

        self.setPen(QPen(QColor(255, 50, 50), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(0)

    def update_line(self, start_pos=None, end_pos=None):
        if self.points is None:
            self.setLine(QLineF(start_pos, end_pos))
        else:
            self.setLine(QLineF(self.points[0].scenePos(), self.points[1].scenePos()))

    def update_points(self, *point_items):
        self.points = point_items

class PageRule(QWidget, UiPageRule):
    def __init__(self, parent=None):
        super().__init__(parent)

        # initialize
        self._setup_ui()
        self.setMouseTracking(True)

        # set the layout of the entire page
        layout = QVBoxLayout(self)
        layout.addWidget(self.page)
        layout.setContentsMargins(0, 0, 0, 0)

        self.pushbutton_add.clicked.connect(self.add_node)

    def add_node(self):
        node = NodeCombobox()
        self.scene.addItem(node)
        self.scene.update_size(self.size())
        node.setPos(self.width() // 2, self.height() // 2)

    def update_scene_size(self, size: QSize):
        self.scene.update_size(size)

