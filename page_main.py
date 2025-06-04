import os
import sys
import yaml

import keyboard

from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow,
        QFormLayout, QBoxLayout, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy,
        QLineEdit, QLabel, QSpinBox, QPushButton, QTextEdit, QListWidget, QListWidgetItem, QCompleter,
        QStackedWidget, QMenuBar, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
        QSpacerItem, QCheckBox, QAbstractItemView, QGraphicsProxyWidget, QGraphicsScene, QGraphicsView)
from PySide6.QtCore import QUrl, QPropertyAnimation, QEasingCurve, QSize, Qt, QPointF
from PySide6.QtGui import QIcon, Qt, QFont, QBrush, QColor, QPen, QPainter
from PySide6.QtWebEngineWidgets import QWebEngineView


from utils.get_path import get_resource_path
from utils.parse_mile import mile_str2num, mile_num2str


from page_design import PageDesign
from page_operation import PageOperation
from page_view import PageView
from page_rule import PageRule


class UiPageMain:
    def _setup_ui(self, main_window):
        if not main_window.objectName():
            main_window.setObjectName("main_window")
        main_window.resize(1200, 800)

        # 设置中心窗口组件
        self.central_widget = QWidget(main_window)
        self.central_layout = QHBoxLayout(self.central_widget)
        main_window.setCentralWidget(self.central_widget)

        # 左侧sidebars
        self._left_sidebars()

        # 中间stackpage
        self._stack_page()

        # menu bar
        self.menubar = QMenuBar(main_window)
        self.menubar.setObjectName("menubar")
        self.menubar_file = self.menubar.addMenu("文件")
        self.menubar_file_open = self.menubar_file.addAction("打开")
        main_window.setMenuBar(self.menubar)

        # status bar
        self.statusbar = QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

    def _left_sidebars(self):
        # 设置左侧sidebars
        self.left_sidebar = QListWidget()
        self.left_sidebar.setFixedWidth(200)
        self.left_sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.central_layout.addWidget(self.left_sidebar)

        self.left_sidebar.setFont(self.fonts(0))
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

        self.sidebar_rule = QListWidgetItem(QIcon(get_resource_path('icons/sidebar_view.png')), "规则链",
                                            self.left_sidebar)
        self.sidebar_rule.setSizeHint(QSize(200, 50))

    def _stack_page(self):
        self.stack_pages = QStackedWidget()
        self.central_layout.addWidget(self.stack_pages)

        self.page_design = PageDesign()
        self.page_operation = PageOperation()
        self.page_view = PageView()
        self.page_rule = PageRule()

        self.stack_pages.addWidget(self.page_design)
        self.stack_pages.addWidget(self.page_operation)
        self.stack_pages.addWidget(self.page_view)
        self.stack_pages.addWidget(self.page_rule)

        # 默认显示页
        self.stack_pages.setCurrentIndex(2)

    def fonts(self, mode):
        font = QFont()
        if mode == 0:
            font.setFamily("Microsoft YaHei")
            font.setPointSize(12)

        elif mode == 1:
            font.setFamily("Microsoft YaHei")
            font.setPointSize(10)

        return font


class PageMain(QMainWindow, UiPageMain):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui(self)

        # signals
        # -> switch pages
        self.left_sidebar.itemClicked.connect(self.switch_page)

        # -> view
        self.page_view.pushbutton_update.clicked.connect(self.view)

    def switch_page(self):
        self.stack_pages.setCurrentIndex(self.left_sidebar.currentRow())

    def view(self):
        self.page_view.update_view(
            self.page_design.get_table_data(),
            self.page_operation.get_table_data(),
            self.page_design.config_combobox,
            self.page_operation.config_combobox,
            self.page_operation.mile1_str,
            self.page_operation.mile2_str
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PageMain()
    window.show()
    sys.exit(app.exec())

