from .common_imports import *
from .connection_point import ConnectionPoint


class NodeGlobalRange(QGraphicsProxyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        # define components
        self.title = QLabel('全局范围')
        self.label1 = QLabel('起始桩号')
        self.label2 = QLabel('结束桩号')
        self.lineedit1 = QLineEdit()
        self.lineedit1.setAlignment(Qt.AlignCenter)
        self.lineedit2 = QLineEdit()
        self.lineedit2.setAlignment(Qt.AlignCenter)

        # input layout
        self.input_layout = QGridLayout()
        self.input_layout.addWidget(self.label1, 0, 0)
        self.input_layout.addWidget(self.lineedit1, 0, 1)
        self.input_layout.addWidget(self.label2, 1, 0)
        self.input_layout.addWidget(self.lineedit2, 1, 1)

        # compile
        self.container_layout.addWidget(self.title, alignment=Qt.AlignCenter)
        self.container_layout.addLayout(self.input_layout)

        # set proxy widget
        self.setWidget(self.container)
        self.setFlag(QGraphicsProxyWidget.ItemIsMovable, True)
        self.setFlag(QGraphicsProxyWidget.ItemIsSelectable, True)

        # set style
        self.set_style()

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
            new_pos = self.original_position + delta

            if new_pos.y() < 0:
                new_pos.setY(0)
            elif (new_pos.y() + self.boundingRect().height()) > self.scene().sceneRect().height():
                new_pos.setY(self.scene().sceneRect().height() - self.boundingRect().height())
            else:
                pass

            if new_pos.x() < 0:
                new_pos.setX(0)
            elif (new_pos.x() + self.boundingRect().width()) > self.scene().sceneRect().width():
                new_pos.setX(self.scene().sceneRect().width() - self.boundingRect().width())
            else:
                pass

            self.setPos(new_pos)
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
        for connection_line in connection_point.connection_lines:
            connection_line.update_line()

    def set_style(self):
        self.container.setStyleSheet("""
                            QWidget {
                                background-color: #f8f9fa;
                                border-radius: 10px;
                                border: 1px solid #dee2e6;
                            }
                        """)

        self.title.setStyleSheet("""
                            QLabel {
                                background-color: transparent;
                                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                                font-size: 14px;
                                border: 1px solid transparent;
                            }
                        """)

        label_style = """
                    QLabel {
                        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                        font-size: 12px;
                        color: #6c757d;
                        border: 1px solid transparent;
                    }
                """
        self.label1.setStyleSheet(label_style)
        self.label2.setStyleSheet(label_style)

        lineedit_style = """
                    QLineEdit {
                        background-color: #ffffff;
                        border: 1px solid #ced4da;
                        border-radius: 5px;
                        font-size: 12px;
                        color: #212529;
                        padding: 2px 0px;
                    }
                    QLineEdit:focus {
                        border: 1px solid #4dabf7;
                        outline: none;
                    }
                """
        self.lineedit1.setStyleSheet(lineedit_style)
        self.lineedit2.setStyleSheet(lineedit_style)

        self.container_layout.setSpacing(2)

    def update_connection_points(self):
        self.input_point.setPos(0, self.boundingRect().height() / 2)
        self.output_point.setPos(self.boundingRect().width(), self.boundingRect().height() / 2)

