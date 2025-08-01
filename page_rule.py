import os
import sys

import PySide6.QtGui
import numpy as np
import yaml

from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QSizePolicy,
                               QFormLayout, QBoxLayout, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLineEdit, QLabel, QSpinBox, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
                               QCompleter,
                               QStackedWidget, QMenuBar, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView,
                               QComboBox,
                               QSpacerItem, QCheckBox, QAbstractItemView, QGraphicsProxyWidget, QGraphicsScene,
                               QGraphicsView, QMenu,
                               QGraphicsItem, QGraphicsLineItem, QGraphicsPolygonItem)
from PySide6.QtCore import QUrl, QPropertyAnimation, QEasingCurve, QSize, Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import QIcon, Qt, QFont, QBrush, QColor, QPen, QPainter, QPainterPath, QPolygonF, QAction
from PySide6.QtWebEngineWidgets import QWebEngineView

from utils.get_path import get_resource_path
from utils.parse_mile import mile_str2num, mile_num2str

from rule_nodes.connection_point import ConnectionPoint
from rule_nodes.connection_line import ConnectionLine
from rule_nodes.node_global_range import NodeGlobalRange
from rule_nodes.node_local_range import NodeLocalRange
from rule_nodes.node_root import NodeRoot
from rule_nodes.node_equipment import NodeEquipment

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

        self.label_nodes = QLabel('节点')
        self.pushbutton_add_node0 = QPushButton('规则链起点')
        self.pushbutton_add_node1 = QPushButton('全局范围')
        self.pushbutton_add_node2 = QPushButton('局部范围')
        self.pushbutton_add_node3 = QPushButton('监测设备')

        # tool
        self.tool_layout = QHBoxLayout()
        self.tool_layout.addWidget(self.pushbutton_add_node0)
        self.tool_layout.addWidget(self.pushbutton_add_node1)
        self.tool_layout.addWidget(self.pushbutton_add_node2)
        self.tool_layout.addWidget(self.pushbutton_add_node3)
        self.tool_layout.addStretch()

        #  compile components
        self.page_layout.addWidget(self.label_nodes)
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
        self.root_nodes = []

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
        try:
            select_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        except:
            select_item = None

        if select_item is not None and isinstance(select_item, ConnectionPoint):
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
                if select_item.point_type == 'input' and len(select_item.connection_lines) == 0:
                    self.tmp_connection_line.update_points(self.start_point_item, select_item)
                    self.start_point_item.update_connection_line(self.tmp_connection_line)
                    select_item.update_connection_line(self.tmp_connection_line)
                else:
                    self.clear_tmp_line()
            else:
                self.clear_tmp_line()
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        try:
            select_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        except:
            select_item = None

        # define menu
        menu = QMenu()

        # -> delete connection line
        action_delete_line = QAction('删除连接线', self)
        action_delete_line.triggered.connect(lambda: self.delete_connection_line(select_item))
        menu.addAction(action_delete_line)

        # -> delete node
        action_delete_node = QAction('删除节点', self)
        action_delete_node.triggered.connect(lambda: self.delete_node(select_item))
        menu.addAction(action_delete_node)
        # finish
        menu.exec(event.screenPos())

    def clear_tmp_line(self):
        self.removeItem(self.tmp_connection_line)
        self.tmp_connection_line = None

    def delete_connection_line(self, connection_line):
        if isinstance(connection_line, ConnectionLine):
            for point in connection_line.points:
                point.update_connection_line(connection_line, 'remove')
            self.removeItem(connection_line)
        else:
            pass

    def delete_node(self, node):
        if isinstance(node, NodeGlobalRange) or isinstance(node, NodeLocalRange):
            input_connection_lines = node.input_point.connection_lines.copy()
            for input_connection_line in input_connection_lines:
                self.delete_connection_line(input_connection_line)
            output_connection_lines = node.output_point.connection_lines.copy()
            for output_connection_line in output_connection_lines:
                self.delete_connection_line(output_connection_line)
            self.removeItem(node)
        elif isinstance(node, NodeRoot):
            # remove connection line
            output_connection_lines = node.output_point.connection_lines.copy()
            for output_connection_line in output_connection_lines:
                self.delete_connection_line(output_connection_line)

            # remove from self.root_nodes
            for i in range(len(self.root_nodes)):
                if id(self.root_nodes[i]) == id(node):
                    del self.root_nodes[i]
                    break

            # remove node
            self.removeItem(node)
        elif isinstance(node, NodeEquipment):
            input_connection_lines = node.input_point.connection_lines.copy()
            for input_connection_line in input_connection_lines:
                self.delete_connection_line(input_connection_line)
            self.removeItem(node)
        else:
            pass


class PageRule(QWidget, UiPageRule):
    def __init__(self, parent=None):
        super().__init__(parent)

        # initialize
        self._setup_ui()
        self.setMouseTracking(True)
        self.nodes_table = {
            0: 'NodeRoot',
            1: 'NodeGlobalRange',
            2: 'NodeLocalRange',
            3: 'NodeEquipment',
        }

        # set the layout of the entire page
        layout = QVBoxLayout(self)
        layout.addWidget(self.page)
        layout.setContentsMargins(0, 0, 0, 0)

        self.pushbutton_add_node0.clicked.connect(lambda: self.add_node(0))
        self.pushbutton_add_node1.clicked.connect(lambda: self.add_node(1))
        self.pushbutton_add_node2.clicked.connect(lambda: self.add_node(2))
        self.pushbutton_add_node3.clicked.connect(lambda: self.add_node(3))


    def add_node(self, node_index):
        node = eval(self.nodes_table[node_index])()
        self.scene.addItem(node)
        self.scene.update_size(self.size())
        node.setPos(self.width() // 2, self.height() // 2)

        # save
        if node_index == 0:
            self.scene.root_nodes.append(node)

    def update_scene_size(self, size: QSize):
        self.scene.update_size(size)

