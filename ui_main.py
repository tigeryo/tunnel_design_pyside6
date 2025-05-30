import os
import sys
import yaml

from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow,
        QFormLayout, QBoxLayout, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLineEdit, QLabel, QSpinBox, QPushButton, QTextEdit, QListWidget, QListWidgetItem, QCompleter,
        QStackedWidget, QMenuBar, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
        QSpacerItem, QCheckBox, QAbstractItemView, QGraphicsProxyWidget, QGraphicsScene, QGraphicsView)
from PySide6.QtCore import QUrl, QPropertyAnimation, QEasingCurve, QSize, Qt, QPointF
from PySide6.QtGui import QIcon, Qt, QFont, QBrush, QColor, QPen, QPainter
from PySide6.QtWebEngineWidgets import QWebEngineView


from utils.get_path import get_resource_path

class UiMain(object):
    def setup_ui(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)

        # 设置中心窗口组件
        self.central_widget = QWidget(MainWindow)
        self.central_layout = QHBoxLayout(self.central_widget)
        MainWindow.setCentralWidget(self.central_widget)

        # 左侧sidebars
        self._left_sidebars()

        # 中间stackpage
        self._stack_page()

        # menu bar
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar_file = self.menubar.addMenu("文件")
        self.menubar_file_open = self.menubar_file.addAction("打开")
        MainWindow.setMenuBar(self.menubar)

        # status bar
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

    def _left_sidebars(self):
        # 设置左侧sidebars
        self.left_sidebar = QListWidget()
        self.left_sidebar.setFixedWidth(200)
        self.left_sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.central_layout.addWidget(self.left_sidebar)

        self.left_sidebar.setFont(self._fonts(0))
        self.left_sidebar.setIconSize(QSize(20, 20))

        self.sidebar_design = QListWidgetItem(QIcon(get_resource_path('icons/sidebar_design.png')), "设计信息",
                                              self.left_sidebar)
        self.sidebar_design.setSizeHint(QSize(200, 50))

        self.sidebar_operation = QListWidgetItem(QIcon(get_resource_path('icons/sidebar_operation.png')), "运营信息",
                                                 self.left_sidebar)
        self.sidebar_operation.setSizeHint(QSize(200, 50))

        self.sidebar_view = QListWidgetItem(QIcon(get_resource_path('icons/sidebar_view.png')), "可视化面板",
                                            self.left_sidebar)
        self.sidebar_view.setSizeHint(QSize(200, 50))

    def _stack_page(self):
        self.stack_pages = QStackedWidget()
        self.central_layout.addWidget(self.stack_pages)

        # 将所有page添加到stack pages
        self._page_design()
        self._page_operation()
        self._page_view()
        self.stack_pages.addWidget(self.page_design)
        self.stack_pages.addWidget(self.page_operation)
        self.stack_pages.addWidget(self.page_view)

        # 默认显示第一页
        self.stack_pages.setCurrentIndex(2)

    def _page_design(self):
        self.page_design = QWidget()
        self.page_design_layout = QVBoxLayout(self.page_design)

        # -> 定义所有页面组件
        self.label_design_mile = QLabel("设计桩号:")
        self.label_design_info = QLabel("设计信息")
        self.label_design_symbol = QLabel("~")
        self.table_design = QTableWidget(1, 7)
        self.lineedit_design_mile1 = QLineEdit()
        self.lineedit_design_mile2 = QLineEdit()
        self.pushbutton_design_add = QPushButton("添加")
        self.pushbutton_design_delete = QPushButton("删除")

        # -> 设置桩号输入标签的格式
        self.label_design_mile.setFont(self._fonts(0))

        # -> 设置桩号输入框的格式
        self.lineedit_design_mile1.setFixedWidth(200)
        self.lineedit_design_mile1.setPlaceholderText("输入起始桩号")
        self.lineedit_design_mile1.setAlignment(Qt.AlignCenter)
        self.lineedit_design_mile1.setFont(self._fonts(0))

        self.lineedit_design_mile2.setFixedWidth(200)
        self.lineedit_design_mile2.setPlaceholderText("输入结束桩号")
        self.lineedit_design_mile2.setAlignment(Qt.AlignCenter)
        self.lineedit_design_mile2.setFont(self._fonts(0))

        # -> 设置表格的表头
        header = self.table_design.horizontalHeader()
        header.resizeSection(0, 20)
        for i in range(header.count()):
            if i == 0:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
                # header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                # header.setDefaultSectionSize(20)
            elif i == header.count() - 1:
                # header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                # header.setDefaultSectionSize(20)
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.table_design.setHorizontalHeaderLabels(['', '起始桩号', '结束桩号', '起始相对桩号', '结束相对桩号', '描述信息', '操作'])

        # -> 设置表格选择模式
        self.table_design.setSelectionMode(QAbstractItemView.SingleSelection)

        # -> 设置表格第一行格式
        # item = QTableWidgetItem()
        # item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        # item.setCheckState(Qt.CheckState.Unchecked)
        # self.table_design.setItem(0, 0, item)

        # -> 组装桩号输入区
        self.design_mile_layuout = QHBoxLayout()
        self.design_mile_layuout.addWidget(self.label_design_mile)
        self.design_mile_layuout.addWidget(self.lineedit_design_mile1)
        self.design_mile_layuout.addWidget(self.label_design_symbol)
        self.design_mile_layuout.addWidget(self.lineedit_design_mile2)
        self.design_mile_layuout.addStretch()

        # -> 组装工具栏
        self.design_tool_layout = QHBoxLayout()
        self.design_tool_layout.addWidget(self.pushbutton_design_add)
        self.design_tool_layout.addWidget(self.pushbutton_design_delete)
        self.design_tool_layout.addStretch()

        # -> 组装页面所有布局
        self.page_design_layout.addLayout(self.design_mile_layuout)
        self.page_design_layout.addWidget(self.label_design_info)
        self.page_design_layout.addLayout(self.design_tool_layout)
        self.page_design_layout.addWidget(self.table_design)

    def _page_operation(self):
        self.page_operation = QWidget()
        self.page_operation_layout = QVBoxLayout(self.page_operation)

        # -> 定义所有页面组件
        self.label_operation_mile = QLabel("运营桩号:")
        self.label_operation_info = QLabel("运营信息")
        self.label_operation_symbol = QLabel("~")
        self.table_operation = QTableWidget(1, 7)
        self.lineedit_operation_mile1 = QLineEdit()
        self.lineedit_operation_mile2 = QLineEdit()
        self.pushbutton_operation_add = QPushButton("添加")
        self.pushbutton_operation_delete = QPushButton("删除")

        # -> 设置桩号输入标签的格式
        self.label_operation_mile.setFont(self._fonts(0))

        # -> 设置桩号输入框的格式
        self.lineedit_operation_mile1.setFixedWidth(200)
        self.lineedit_operation_mile1.setPlaceholderText("输入起始桩号")
        self.lineedit_operation_mile1.setAlignment(Qt.AlignCenter)
        self.lineedit_operation_mile1.setFont(self._fonts(0))

        self.lineedit_operation_mile2.setFixedWidth(200)
        self.lineedit_operation_mile2.setPlaceholderText("输入结束桩号")
        self.lineedit_operation_mile2.setAlignment(Qt.AlignCenter)
        self.lineedit_operation_mile2.setFont(self._fonts(0))

        # -> 设置表格的表头
        header = self.table_operation.horizontalHeader()
        header.resizeSection(0, 20)
        for i in range(header.count()):
            if i == 0:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
                # header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                # header.setDefaultSectionSize(20)
            elif i == header.count() - 1:
                # header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                # header.setDefaultSectionSize(20)
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.table_operation.setHorizontalHeaderLabels(['', '起始桩号', '结束桩号', '起始相对桩号', '结束相对桩号', '描述信息', '操作'])

        # -> 设置表格选择模式，单选
        self.table_operation.setSelectionMode(QAbstractItemView.SingleSelection)

        # -> 设置表格第一行格式
        # item = QTableWidgetItem()
        # item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        # item.setCheckState(Qt.CheckState.Unchecked)
        # self.table_design.setItem(0, 0, item)

        # -> 组装桩号输入区
        self.operation_mile_layuout = QHBoxLayout()
        self.operation_mile_layuout.addWidget(self.label_operation_mile)
        self.operation_mile_layuout.addWidget(self.lineedit_operation_mile1)
        self.operation_mile_layuout.addWidget(self.label_operation_symbol)
        self.operation_mile_layuout.addWidget(self.lineedit_operation_mile2)
        self.operation_mile_layuout.addStretch()

        # -> 组装工具栏
        self.operation_tool_layout = QHBoxLayout()
        self.operation_tool_layout.addWidget(self.pushbutton_operation_add)
        self.operation_tool_layout.addWidget(self.pushbutton_operation_delete)
        self.operation_tool_layout.addStretch()

        # -> 组装页面所有布局
        self.page_operation_layout.addLayout(self.operation_mile_layuout)
        self.page_operation_layout.addWidget(self.label_operation_info)
        self.page_operation_layout.addLayout(self.operation_tool_layout)
        self.page_operation_layout.addWidget(self.table_operation)

    def _page_view(self):
        self.page_view = QWidget()
        self.page_view_layout = QVBoxLayout(self.page_view)

        # -> 定义所有组件
        self.browser = QWebEngineView()
        self.pushbutton_view_update = QPushButton('刷新')

        # -> 工具栏
        self.view_tool_layout = QHBoxLayout()
        self.view_tool_layout.addWidget(self.pushbutton_view_update)
        self.view_tool_layout.addStretch()

        # -> 组装页面有所有组件
        self.page_view_layout.addLayout(self.view_tool_layout)
        self.page_view_layout.addWidget(self.browser)

    def _page_rule(self):
        print('test')
        pass

    def _fonts(self, mode):
        font = QFont()
        if mode == 0:
            font.setFamily("Microsoft YaHei")
            font.setPointSize(12)

        elif mode == 1:
            font.setFamily("Microsoft YaHei")
            font.setPointSize(10)

        return font


class Node(QGraphicsProxyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.container = QWidget()
        layout = QVBoxLayout(self.container)

        self.title = QLabel('标题')
        layout.addWidget(self.title)

        self.combobox = QComboBox()
        self.combobox.addItems(['1', '2'])
        layout.addWidget(self.combobox)

        # 设置代理窗口小部件
        self.setWidget(self.container)
        self.setFlag(QGraphicsProxyWidget.ItemIsMovable, True)
        self.setFlag(QGraphicsProxyWidget.ItemIsSelectable, True)

        # 记录拖动状态
        self.dragging = False
        self.drag_start_position = QPointF()
        self.original_position = QPointF()

    def mousePressEvent(self, event):
        pass