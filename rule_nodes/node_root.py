from numpy.ma.core import count

from .common_imports import *
from .connection_point import ConnectionPoint


class NodeRoot(QGraphicsProxyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # init
        self.container = QWidget()
        self.container.setFixedWidth(120)
        self.container_layout = QVBoxLayout(self.container)

        # define components
        self.title = QLabel('规则链起点')

        self.label = QLabel('执行顺序')
        self.lineedit = QLineEdit()
        self.lineedit.setAlignment(Qt.AlignCenter)

        #
        self.label_layout = QHBoxLayout()
        self.label_layout.addWidget(self.label)
        self.label_layout.addWidget(self.lineedit)

        # compile
        self.container_layout.addWidget(self.title, alignment=Qt.AlignCenter)
        self.container_layout.addLayout(self.label_layout)

        # set proxy widget
        self.setWidget(self.container)
        self.setFlag(QGraphicsProxyWidget.ItemIsMovable, True)
        self.setFlag(QGraphicsProxyWidget.ItemIsSelectable, True)

        # set style
        self.set_style()

        # add connection node, must after setting proxy widget
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
        self.lineedit.setStyleSheet("""
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
        """)
        self.label.setStyleSheet("""
                QLabel {
                    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                    font-size: 12px;
                    color: #6c757d;
                    border: 1px solid transparent;
                }
            """)

        self.container_layout.setSpacing(2)

    def update_connection_points(self):
        self.output_point.setPos(self.boundingRect().width(), self.boundingRect().height() / 2)