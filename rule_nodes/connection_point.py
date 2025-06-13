from .common_imports import *
from .connection_line import ConnectionLine


class ConnectionPoint(QGraphicsItem):
    def __init__(self, parent=None, point_type="input"):
        super().__init__(parent)
        # point params
        self.radius = 6

        # point type: input or output
        self.point_type = point_type

        # allow hover event
        self.setAcceptHoverEvents(True)

        # state flag
        self.is_hovered = False
        self.is_connected = False

        # bind connection line
        self.connection_lines: list[ConnectionLine] = []


    def boundingRect(self):
        """control the boundary of the graphics item """
        return QRectF(-self.radius, -self.radius,
                      self.radius * 2, self.radius * 2)

    def shape(self):
        """control the shape of the item: circle"""
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            color = QColor('#ADD8E6')
        elif self.is_hovered:
            color = QColor('#ADD8E6')
        elif self.is_connected:
            color = QColor('#00FF7F')
        else:
            color = QColor('#ADD8E6')

        # 绘制连接点
        painter.setPen(QPen(color, 1.5))
        painter.setBrush(QBrush(color.lighter(150)))
        painter.drawEllipse(self.boundingRect())

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        event.accept()
        # super().mousePressEvent(event)

    def update_connection_line(self, line_item, mode='add'):
        if mode == 'add':
            self.connection_lines.append(line_item)
            self.is_connected = True
        elif mode == 'remove':
            for i in range(len(self.connection_lines)):
                if id(self.connection_lines[i]) == id(line_item):
                    del self.connection_lines[i]
                    break
            if len(self.connection_lines) == 0:
                self.is_connected = False
                self.update()
        else:
            pass