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
from utils.parse_mile import mile_str2num


class UiPageView:
    def _setup_ui(self, form):
        self.page = QWidget()
        self.page_layout = QVBoxLayout(self.page)
        self.page_layout.setContentsMargins(0, 0, 0, 0)

        # define components
        self.browser = QWebEngineView()
        self.pushbutton_update = QPushButton('刷新')

        # toolbar
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.addWidget(self.pushbutton_update)
        self.toolbar_layout.addStretch()

        # compile components
        self.page_layout.addLayout(self.toolbar_layout)
        self.page_layout.addWidget(self.browser)

class PageView(QWidget, UiPageView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # initialize
        self._setup_ui(self)

        # set the layout of the entire page
        layout = QVBoxLayout(self)
        layout.addWidget(self.page)
        layout.setContentsMargins(0, 0, 0, 0)

        # signals
        # -> update view
        self.pushbutton_update.clicked.connect(self.update_view)

    def update_view(self):
        pass

    def get_data(self):
        pass