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

import plotly.graph_objects as go

from utils.get_path import get_resource_path
from utils.parse_mile import mile_str2num, mile_num2str


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

    def update_view(
            self, data_design, data_operation, combobox_design, combobox_operation,
            mile1_str_operation=None, mile2_str_operation=None
    ):
        fig = go.Figure()
        row = 0
        x_max = 0
        y_label = dict(tickvals=[], ticktext=[])

        if len(data_design) > 0:
            fig, row, x_max, y_label = self._plot(fig, row, x_max, y_label, data_design, combobox_design)
        if len(data_operation) > 0:
            fig, row, x_max, y_label = self._plot(fig, row, x_max, y_label, data_operation, combobox_operation)

        # 更新通用配置
        fig.update_layout(
            height=100 + 100 * row,
            xaxis=dict(
                range=[0, 100],
                rangeslider=dict(visible=True)
            ),
            yaxis_autorange='reversed',
            yaxis=dict(
                tickmode='array',
                tickvals=y_label['tickvals'],
                ticktext=y_label['ticktext']
            )
        )

        # 更新x轴
        if mile1_str_operation is None:
            pass
        else:
            if mile2_str_operation is None:
                miles_rel, miles_str = self.generate_milenet(
                    mile1_str=mile1_str_operation,
                    length=x_max
                )
            else:
                miles_rel, miles_str = self.generate_milenet(
                    mile1_str=mile1_str_operation,
                    mile2_str=mile2_str_operation
                )

            fig.update_layout(
                xaxis_range=[min(miles_rel), max(miles_rel)],
                xaxis=dict(
                    tickmode='array',
                    tickvals=miles_rel,
                    ticktext=miles_str
                )
            )

        # 显示图像
        html_content = fig.to_html(full_html=True,
                                   include_plotlyjs='cdn',
                                   config={'responsive': False})
        self.browser.setHtml(html_content, baseUrl=QUrl.fromLocalFile(''))
        self.browser.show()

    def _plot(self, fig, row, x_max, y_label, data, keys_total):
        for key in keys_total.keys():
            if key in data.keys():
                row += 1

                y_label['tickvals'].append(row)
                y_label['ticktext'].append(key)

                for data_each in data[key]:
                    x1, x2 = data_each['miles_rel'][0] - 0.5, data_each['miles_rel'][1] + 0.5
                    y1, y2 = row - 0.25, row + 0.25
                    fig.add_trace(
                        go.Scatter(
                            x=[x1, x1, x2, x2, x1],
                            y=[y1, y2, y2, y1, y1],
                            line=dict(color=data_each['color']),
                            mode='lines',
                            fill='toself',
                            fillcolor=data_each['color'],
                            showlegend=False,
                        )
                    )

                    # 保存最大的x
                    x_max = max(x_max, data_each['miles_rel'][1])
        return fig, row, x_max, y_label

    def generate_milenet(self, mile1_str, mile2_str=None, mile_step=100, length=None):
        assert (mile2_str is not None) or (length is not None), '桩号网格参数异常'

        mile1_num, front_k = mile_str2num(mile1_str)
        if mile2_str is not None:
            mile2_num, _ = mile_str2num(mile2_str)
            length = mile2_num - mile1_num

        # 起始桩号
        miles_rel = [0]
        miles_str = [mile1_str]

        # 第一段的结束桩号
        mile1_rel = mile_step - (mile1_num % mile_step)
        if np.isclose(mile_step, mile1_rel):
            miles_rel.append(mile_step)
            miles_str.append(mile_num2str(mile1_num + mile_step, front_k, 'short'))
            mile1_rel = mile_step
        else:
            miles_rel.append(mile1_rel)
            miles_str.append(mile_num2str(mile1_num + mile1_rel, front_k, 'short'))

        # 各段的结束桩号
        while True:
            mile2_rel = mile1_rel + mile_step

            if mile2_rel >= length:
                miles_rel.append(length)
                if mile2_str is None:
                    miles_str.append(mile_num2str(mile1_num + length, front_k, 'short'))
                else:
                    miles_str.append(mile2_str)
                break
            else:
                miles_rel.append(mile2_rel)
                miles_str.append(mile_num2str(mile1_num + mile2_rel, front_k, 'short'))
                mile1_rel += mile_step

        return miles_rel, miles_str


