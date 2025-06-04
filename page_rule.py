import os
import sys

import numpy as np
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
from utils.parse_mile import mile_str2num, mile_num2str


class UiPageRule:
    def _setup_ui(self):
        self.page = QWidget()
        self.page_layout = QVBoxLayout(self.page)
        self.page_layout.setContentsMargins(0, 0, 0, 0)

        # define components
        self.scene = QGraphicsScene()

        self.view = QGraphicsView(self.scene)

        # 添加背景
        background = self.scene.addRect(0, 0, 800, 600)
        background.setBrush(QBrush(QColor(240, 240, 240)))

        self.page_layout.addWidget(self.view)


class PageRule(QWidget, UiPageRule):
    def __init__(self, parent=None):
        super().__init__(parent)

        # initialize
        self._setup_ui()

        # set the layout of the entire page
        layout = QVBoxLayout(self)
        layout.addWidget(self.page)
        layout.setContentsMargins(0, 0, 0, 0)



