from .common_imports import *


class ConnectionLine(QGraphicsLineItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = None

        self.setPen(QPen(QColor(255, 50, 50), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.setZValue(0)

        # state flag
        self.is_hovered = False

        self.setAcceptHoverEvents(True)


    def paint(self, painter, option, widget = ...):
        if self.isSelected():
            color = QColor('#9370DB')
        elif self.is_hovered:
            color = QColor('#9370DB')
        else:
            color = QColor('#008B8B')

        painter.setPen(QPen(color, 1.5))
        painter.setBrush(QBrush(color.lighter(150)))
        painter.drawLine(self.line())

        self.update_arrow(color)

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def update_line(self, start_pos=None, end_pos=None):
        if self.points is None:
            self.setLine(QLineF(start_pos, end_pos))
        else:
            self.setLine(QLineF(self.points[0].scenePos(), self.points[1].scenePos()))

    def update_points(self, *point_items):
        self.points = point_items

    def update_arrow(self, color):
        """更新箭头位置"""
        # 清除旧箭头
        for item in self.childItems():
            if isinstance(item, QGraphicsPolygonItem):
                self.scene().removeItem(item)

        # 创建新箭头
        line = self.line()
        if line.length() == 0:
            return

        # 箭头大小
        arrow_size = 12

        # # 箭头角度计算
        # angle = line.angle()
        # rad_angle = angle * 3.141592653589793 / 180.0

        # 箭头位置（在终点）
        arrow_point = line.p2()

        # 创建箭头多边形
        arrow_poly = QPolygonF()

        # 箭头顶点1
        p1 = arrow_point - QPointF(
            arrow_size * 0.8 * (line.dx() / line.length()),
            arrow_size * 0.8 * (line.dy() / line.length())
        )

        # 箭头顶点2
        p2 = p1 + QPointF(
            arrow_size * 0.5 * (line.dx() / line.length() * 0.5 - line.dy() / line.length()),
            arrow_size * 0.5 * (line.dy() / line.length() * 0.5 + line.dx() / line.length())
        )

        # 箭头顶点3
        p3 = p1 + QPointF(
            arrow_size * 0.5 * (line.dx() / line.length() * 0.5 + line.dy() / line.length()),
            arrow_size * 0.5 * (line.dy() / line.length() * 0.5 - line.dx() / line.length())
        )

        arrow_poly.append(arrow_point)
        arrow_poly.append(p2)
        arrow_poly.append(p3)
        arrow_poly.append(arrow_point)

        # 创建箭头图形项
        arrow = QGraphicsPolygonItem(arrow_poly, self)
        arrow.setBrush(QBrush(color.lighter(150)))
        arrow.setPen(QPen(color, 1.5))