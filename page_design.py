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


class UiPageDesign:
    def _setup_ui(self, form):
        self.page = QWidget(form)
        self.page_layout = QVBoxLayout(self.page)
        self.page_layout.setContentsMargins(0, 0, 0, 0)

        # define components in this page
        self.label_mile = QLabel("设计桩号:")
        self.label_info = QLabel("设计信息")
        self.label_connection_symbol = QLabel("~")
        self.table = QTableWidget(1, 7)
        self.lineedit_mile1 = QLineEdit()
        self.lineedit_mile2 = QLineEdit()
        self.pushbutton_add = QPushButton("添加")
        self.pushbutton_delete = QPushButton("删除")

        # 设置桩号输入标签的格式
        self.label_mile.setFont(self.fonts(0))

        # 设置桩号输入框的格式
        self.lineedit_mile1.setFixedWidth(200)
        self.lineedit_mile1.setPlaceholderText("输入起始桩号")
        self.lineedit_mile1.setAlignment(Qt.AlignCenter)
        self.lineedit_mile1.setFont(self.fonts(0))

        self.lineedit_mile2.setFixedWidth(200)
        self.lineedit_mile2.setPlaceholderText("输入结束桩号")
        self.lineedit_mile2.setAlignment(Qt.AlignCenter)
        self.lineedit_mile2.setFont(self.fonts(0))

        # 设置表格的表头
        header = self.table.horizontalHeader()
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

        self.table.setHorizontalHeaderLabels(
            ['', '起始桩号', '结束桩号', '起始相对桩号', '结束相对桩号', '描述信息', '操作'])

        # 设置表格选择模式
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        # 组装
        # -> 桩号输入区
        self.mile_layout = QHBoxLayout()
        self.mile_layout.addWidget(self.label_mile)
        self.mile_layout.addWidget(self.lineedit_mile1)
        self.mile_layout.addWidget(self.label_connection_symbol)
        self.mile_layout.addWidget(self.lineedit_mile2)
        self.mile_layout.addStretch()

        # -> 工具栏
        self.tool_layout = QHBoxLayout()
        self.tool_layout.addWidget(self.pushbutton_add)
        self.tool_layout.addWidget(self.pushbutton_delete)
        self.tool_layout.addStretch()

        # -> 所有布局
        self.page_layout.addLayout(self.mile_layout)
        self.page_layout.addWidget(self.label_info)
        self.page_layout.addLayout(self.tool_layout)
        self.page_layout.addWidget(self.table)

    def fonts(self, mode):
        font = QFont()
        if mode == 0:
            font.setFamily("Microsoft YaHei")
            font.setPointSize(12)

        elif mode == 1:
            font.setFamily("Microsoft YaHei")
            font.setPointSize(10)

        return font


class PageDesign(QWidget, UiPageDesign):
    def __init__(self, parent=None):
        super().__init__(parent)
        # read config
        self.config_combobox = self.load_config_combobox(get_resource_path('config_combobox.yaml'))
        self.config_color = self.load_config_color(get_resource_path('config_color.yaml'))

        # initialize
        self._setup_ui(self)
        self.init_table(0)

        # set the layout of the entire page
        layout = QVBoxLayout(self)
        layout.addWidget(self.page)
        layout.setContentsMargins(0, 0, 0, 0)

        # default params
        self.k_miles = [None, None, None]

        # signals
        # -> add a new row in the table
        self.pushbutton_add.clicked.connect(self.append_row)
        self.pushbutton_delete.clicked.connect(self.delete_selection_rows)

        # -> update save miles
        self.lineedit_mile1.editingFinished.connect(lambda: self.update_save_miles('entrance'))
        self.lineedit_mile2.editingFinished.connect(lambda: self.update_save_miles('exit'))

        # -> update relative miles, triggered by changing cell
        self.table.cellChanged.connect(self.update_table_relative_mile_row)

        # -> update relative miles, triggered by changing entrance and exit miles
        self.lineedit_mile1.editingFinished.connect(self.update_table_relative_mile_all)
        self.lineedit_mile2.editingFinished.connect(self.update_table_relative_mile_all)

    def update_table_relative_mile_all(self):
        for row in range(self.table.rowCount()):
            self.update_table_relative_mile_row(row, 1)

    def update_table_relative_mile_row(self, row, column):
        if self.k_miles[1] is None:
            pass
        else:
            if column in [1, 2]:
                try:
                    mile_num, _ = mile_str2num(self.table.item(row, column).text())
                    relative_mile_num = np.round(np.abs(mile_num - self.k_miles[1]))
                    relative_mile_str = f'{relative_mile_num:.0f}'
                except Exception:
                    relative_mile_str = ''

                self.table.setItem(row, column + 2, QTableWidgetItem(relative_mile_str))
            else:
                pass

    def update_save_miles(self, name):
        try:
            if name == 'entrance':
                self.k_miles[1], self.k_miles[0] = mile_str2num(self.lineedit_mile1.text())
            elif name == 'exit':
                self.k_miles[2], self.k_miles[0] = mile_str2num(self.lineedit_mile2.text())
            else:
                pass
        except Exception as e:
            print(e)

    def load_config_combobox(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config['design_combobox']

    def load_config_color(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def generate_combobox_options(self):
        config = []
        for key, values in self.config_combobox.items():
            if values:
                for value in values:
                    config.append(f'{key}：{value}')
            else:
                config.append(key)
        return config

    def init_table(self, row):
        # 第一列为勾选框
        self.table.setCellWidget(row, 0, QCheckBox())

        #
        self.table.setItem(row, 1, QTableWidgetItem(''))
        self.table.setItem(row, 2, QTableWidgetItem(''))
        self.table.setItem(row, 3, QTableWidgetItem(''))
        self.table.setItem(row, 4, QTableWidgetItem(''))

        #
        combobox = QComboBox()
        combobox.setEditable(True)
        combobox.addItems(self.generate_combobox_options())
        combobox.setCurrentIndex(-1)
        completer = QCompleter(combobox.model())
        completer.setFilterMode(Qt.MatchContains)
        combobox.setCompleter(completer)

        self.table.setCellWidget(row, 5, combobox)

        #
        pushbutton = QPushButton('删除')
        pushbutton.clicked.connect(self.delete_current_row)
        self.table.setCellWidget(row, 6, pushbutton)

    def delete_current_row(self):
        self.delete_single_row(self.table.currentRow())

    def delete_single_row(self, row):
        self.table.removeRow(row)

        if self.table.rowCount() == 0:
            self.table.insertRow(0)
            self.init_table(0)

    def append_row(self):
        """add a new row in the table"""
        self.table.insertRow(self.table.rowCount())
        self.init_table(self.table.rowCount() - 1)

    def delete_selection_rows(self):
        rows = []
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 0).isChecked():
                rows.append(row)

        for row in sorted(rows, reverse=True):
            self.delete_single_row(row)

    def get_table_data(self):
        data = {}
        for row in range(self.table.rowCount()):
            mile1_str = None if self.table.item(row, 1).text() == '' else self.table.item(row, 1).text()
            mile2_str = None if self.table.item(row, 2).text() == '' else self.table.item(row, 2).text()
            mile1_rel_num = None if self.table.item(row, 3).text() == '' else int(self.table.item(row, 3).text())
            mile2_rel_num = None if self.table.item(row, 4).text() == '' else int(self.table.item(row, 4).text())
            info = None if self.table.cellWidget(row, 5).currentText() == '' else self.table.cellWidget(row, 5).currentText()

            if ((mile1_rel_num is not None) or (mile2_rel_num is not None)) and (info is not None):
                info_split = info.split('：')
                if len(info_split) == 1:
                    color = self.config_color['default']
                elif len(info_split) == 2:
                    color = self.config_color[info_split[1]]
                else:
                    print('?')
                    continue

                mile1_rel_num = mile1_rel_num if mile1_rel_num is not None else mile2_rel_num
                mile2_rel_num = mile2_rel_num if mile2_rel_num is not None else mile1_rel_num

                if info_split[0] in data.keys():
                    data[info_split[0]].append(
                        dict(
                            miles_rel=[mile1_rel_num, mile2_rel_num],
                            color=color
                        )
                    )
                else:
                    data[info_split[0]] = [
                        dict(
                            miles_rel=[mile1_rel_num, mile2_rel_num],
                            color=color
                        )
                    ]
        return data
