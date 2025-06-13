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

import sys
sys.path.append('..')
from utils.get_path import get_resource_path
from utils.parse_mile import mile_str2num, mile_num2str
