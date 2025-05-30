import os
import sys
import yaml

import keyboard

from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow,
        QFormLayout, QBoxLayout, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLineEdit, QLabel, QSpinBox, QPushButton, QTextEdit, QListWidget, QCompleter,
        QStackedWidget, QMenuBar, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
        QSpacerItem, QCheckBox)
from PySide6.QtCore import QUrl, QPropertyAnimation, QEasingCurve, QSize, Qt
from PySide6.QtGui import QIcon, Qt, QMouseEvent

import pyecharts.options as opts
from pyecharts.charts import Line, Scatter
from pyecharts.globals import CurrentConfig

import plotly.graph_objects as go

import numpy as np


from utils.get_path import get_resource_path
from utils.parse_mile import mile_str2num, mile_num2str

from ui_main import UiMain

class MainWindow(QMainWindow, UiMain):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 读取配置文件
        self.config_combobox, self.config_color = self._load_config_combobox(get_resource_path('config_combobox.yaml'),
                                                                             get_resource_path('config_color.yaml'))

        # 初始化ui
        self.setup_ui(self)
        self.init_table_design(0)
        self.init_table_operation(0)

        # 初始化参数
        self.mile_design = [None, None, None]  # K, mile1, mile2
        self.mile_operation = [None, None, None]  # K, mile1, mile2

        # --信号--
        # -> 页面切换
        self.left_sidebar.itemClicked.connect(self.switch_page)

        # -> 添加/删除表格行
        self.pushbutton_design_add.clicked.connect(lambda: self.append_row(self.table_design))
        self.pushbutton_operation_add.clicked.connect(lambda: self.append_row(self.table_operation))

        self.pushbutton_design_delete.clicked.connect(lambda: self.delete_selection_rows(self.table_design))
        self.pushbutton_operation_delete.clicked.connect(lambda: self.delete_selection_rows(self.table_operation))

        # -> 更新起止桩号
        self.lineedit_design_mile1.editingFinished.connect(lambda: self.update_mile('design_mile1'))
        self.lineedit_design_mile2.editingFinished.connect(lambda: self.update_mile('design_mile2'))
        self.lineedit_operation_mile1.editingFinished.connect(lambda: self.update_mile('operation_mile1'))
        self.lineedit_operation_mile2.editingFinished.connect(lambda: self.update_mile('operation_mile2'))

        # -> 更新表格内相对桩号，由更改单元格触发
        self.table_design.cellChanged.connect(self.update_table_design_relative_mile)
        self.table_operation.cellChanged.connect(self.update_table_operation_relative_mile)

        # -> 更新表格内相对桩号，由更改起止桩号触发
        self.lineedit_design_mile1.editingFinished.connect(self.update_table_design_relative_mile_all)
        # self.lineedit_design_mile2.editingFinished.connect(self1.update_table_design_relative_mile_all)
        self.lineedit_operation_mile1.editingFinished.connect(self.update_table_operation_relative_mile_all)
        # self.lineedit_operation_mile2.editingFinished.connect(self.update_table_operation_relative_mile_all)

        # -> 刷新view图
        # self.view()
        self.pushbutton_view_update.clicked.connect(self.view)


    def update_table_design_relative_mile_all(self):
        for row in range(self.table_design.rowCount()):
            self.update_table_design_relative_mile(row, 1)

    def update_table_operation_relative_mile_all(self):
        for row in range(self.table_operation.rowCount()):
            self.update_table_operation_relative_mile(row, 1)

    def update_table_design_relative_mile(self, row, column):
        self.update_table_relative_mile(self.table_design, row, column, self.mile_design[1])

    def update_table_operation_relative_mile(self, row, column):
        self.update_table_relative_mile(self.table_operation, row, column, self.mile_operation[1])

    def update_table_relative_mile(self, table, row, column, start_mile):
        if start_mile is None:
            pass
        else:
            if column in [1, 2]:
                try:
                    mile_num, _ = mile_str2num(table.item(row, column).text())
                    relative_mile_num = np.round(np.abs(mile_num - start_mile))
                    relative_mile_str = f'{relative_mile_num:.0f}'
                except Exception:
                    relative_mile_str = ''

                table.setItem(row, column + 2, QTableWidgetItem(relative_mile_str))

            else:
                pass

    def update_mile(self, name):
        try:
            if name == 'design_mile1':
                self.mile_design[1], self.mile_design[0] = mile_str2num(self.lineedit_design_mile1.text())
            elif name == 'design_mile2':
                self.mile_design[2], self.mile_design[0] = mile_str2num(self.lineedit_design_mile2.text())
            elif name == 'operation_mile1':
                self.mile_operation[1], self.mile_operation[0] = mile_str2num(self.lineedit_operation_mile1.text())
            elif name == 'operation_mile2':
                self.mile_operation[2], self.mile_operation[0] = mile_str2num(self.lineedit_operation_mile2.text())
            else:
                pass
        except Exception as e:
            print(e)

    def view(self):
        data_design = self.get_table_data(self.table_design)
        data_operation = self.get_table_data(self.table_operation)

        def plot(fig, data, keys_total, row, x_max):
            for key in keys_total:
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
            return fig, row, x_max

        fig = go.Figure()
        row = 0
        x_max = 0
        y_label = dict(tickvals=[], ticktext=[])
        if len(data_design) > 0:
            fig, row, x_max = plot(fig, data_design, self.config_combobox['design_combobox'], row, x_max)
        if len(data_operation) > 0:
            fig, row, x_max = plot(fig, data_operation, self.config_combobox['operation_combobox'], row, x_max)

        # 更新通用配置
        fig.update_layout(
            height=100+100*row,
            xaxis=dict(
                range=[0, 100],
                rangeslider=dict(visible=True)
            ),
            yaxis_autorange='reversed',
            yaxis=dict(
                tickmode='array',
                tickvals = y_label['tickvals'],
                ticktext = y_label['ticktext']
            )
        )

        # 更新x轴
        if all(_ is not None for _ in self.mile_operation[:2]):
            if self.mile_operation[2] is None:
                miles_rel, miles_str = self.generate_milenet(
                    mile1_str=self.lineedit_operation_mile1.text(),
                    length=x_max
                )
            else:
                miles_rel, miles_str = self.generate_milenet(
                    mile1_str=self.lineedit_operation_mile1.text(),
                    mile2_str=self.lineedit_operation_mile2.text()
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


    def get_table_data(self, table: QTableWidget):
        data = {}
        for row in range(table.rowCount()):
            mile1_str = None if table.item(row, 1) is None else table.item(row, 1).text()
            mile2_str = None if table.item(row, 2) is None else table.item(row, 2).text()
            mile1_rel_num = None if table.item(row, 3).text() == '' else int(table.item(row, 3).text())
            mile2_rel_num = None if table.item(row, 4).text() == '' else int(table.item(row, 4).text())
            info = None if table.cellWidget(row, 5).currentText() == '' else table.cellWidget(row, 5).currentText()

            # 判断数据是否完整
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
                            miles_rel = [mile1_rel_num, mile2_rel_num],
                            color = color
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

    # 可视化pyecharts，启动较慢，几秒
    # def t(self):
    #     c = (
    #         Line()
    #         .add_xaxis(['a', 'b', 'c'])
    #         .add_yaxis("商家A", [1, 2, 3])
    #         .add_yaxis("商家B", [2, 1, 1])
    #         .set_global_opts(title_opts=opts.TitleOpts(title="Line-基本示例"))
    #     )
    #
    #     CurrentConfig.ONLINE_HOST = get_resource_path('assets')
    #     html_content = """
    #             <!DOCTYPE html>
    #             <html>
    #             <head>
    #                 <meta charset="UTF-8">
    #                 <script type="text/javascript" src="{echarts_js}"></script>
    #             </head>
    #             <body>
    #                 {chart_html}
    #             </body>
    #             </html>
    #             """.format(
    #         echarts_js=CurrentConfig.ONLINE_HOST + "echarts.min.js",
    #         chart_html=c.render_embed()
    #     )
    #
    #     self.browser.setHtml(html_content)
    #     self.browser.show()

    def init_table_design(self, row):
        """初始化设计信息的表格，第一行"""
        # 第一列为勾选框
        self.table_design.setCellWidget(row, 0, QCheckBox())

        # 第4、5列，默认为''
        self.table_design.setItem(row, 3, QTableWidgetItem(''))
        self.table_design.setItem(row, 4, QTableWidgetItem(''))

        # 描述信息列为下拉框
        combobox = QComboBox()
        combobox.setEditable(True)
        combobox.addItems(self._generate_combobox_config('design_combobox'))
        combobox.setCurrentIndex(-1)
        completer = QCompleter(combobox.model())
        completer.setFilterMode(Qt.MatchContains)
        combobox.setCompleter(completer)

        self.table_design.setCellWidget(row, 5, combobox)

        # 操作列为删除该行按钮
        pushbutton = QPushButton('删除')

        pushbutton.clicked.connect(lambda: self.delete_current_row(pushbutton))

        self.table_design.setCellWidget(row, 6, pushbutton)

    def init_table_operation(self, row):
        """初始化运营信息的表格，第一行"""
        # 第一列为勾选框
        self.table_operation.setCellWidget(row, 0, QCheckBox())

        # 第4、5列，默认为''
        self.table_operation.setItem(row, 3, QTableWidgetItem(''))
        self.table_operation.setItem(row, 4, QTableWidgetItem(''))

        # 描述信息列为下拉框
        combobox = QComboBox()
        combobox.setEditable(True)
        combobox.addItems(self._generate_combobox_config('operation_combobox'))
        combobox.setCurrentIndex(-1)
        completer = QCompleter(combobox.model())
        completer.setFilterMode(Qt.MatchContains)
        combobox.setCompleter(completer)

        self.table_operation.setCellWidget(row, 5, combobox)

        # 操作列为删除该行按钮
        pushbutton = QPushButton('删除')

        pushbutton.clicked.connect(lambda: self.delete_current_row(pushbutton))

        self.table_operation.setCellWidget(row, 6, pushbutton)

    def switch_page(self):
        """点击sidebar切换stackpage的页面"""
        self.stack_pages.setCurrentIndex(self.left_sidebar.currentRow())

    def delete_current_row(self, pushbutton):
        """点击表格行内删除按钮，删除该行"""
        table = pushbutton.parent().parent()

        self.delete_single_row(table, table.currentRow())

    def delete_selection_rows(self, table):
        rows = []
        for row in range(table.rowCount()):
            if table.cellWidget(row, 0).isChecked():
                rows.append(row)

        for row in sorted(rows, reverse=True):
            self.delete_single_row(table, row)

    def delete_single_row(self, table, row):
        table.removeRow(row)

        if table.rowCount() == 0:
            table.insertRow(0)
            if self.stack_pages.currentIndex() == 0:
                self.init_table_design(0)
            elif self.stack_pages.currentIndex() == 1:
                self.init_table_operation(0)


    def append_row(self, table):
        table.insertRow(table.rowCount())
        if self.stack_pages.currentIndex() == 0:
            self.init_table_design(table.rowCount() - 1)
        elif self.stack_pages.currentIndex() == 1:
            self.init_table_operation(table.rowCount() - 1)

    def _load_config_combobox(self, *config_path):
        config = []
        for path in config_path:
            with open(path, 'r', encoding='utf-8') as f:
                config.append(yaml.safe_load(f))
        return tuple(config)

    def _generate_combobox_config(self, name):
        config_read = self.config_combobox[name]

        config = []
        for key, values in config_read.items():
            if values:
                for value in values:
                    config.append(f'{key}：{value}')
            else:
                config.append(key)

        return config

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




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

