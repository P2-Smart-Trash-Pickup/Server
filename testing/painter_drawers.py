kmport math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter


def drawLineArrow(
    painter: QPainter,
    old_point: QPointF,
    new_point: QPointF,
    arrow_width: float = 8.0,
    arrow_height_ratio: float = 0.6,
    line_color: str = "#FF0000",
    arrow_color: str = "#FF0000",
) -> QPainter:
    painter.setPen(QColor.fromString(line_color))
    painter.setBrush(QColor.fromString(arrow_color))

    painter.drawLine(old_point, new_point)

    diff_point = new_point.__sub__(old_point)

    mid_point = diff_point.__mul__(0.5).__add__(old_point)

    arrow_tip = diff_point.__mul__(arrow_height_ratio).__add__(old_point)

    angle = math.atan2(diff_point.y(), diff_point.x())

    angle1 = angle + math.pi / 2

    m1 = mid_point.__add__(
        QPointF(arrow_width * math.cos(angle1), arrow_width * math.sin(angle1))
    )

    angle2 = angle - math.pi / 2

    m2 = mid_point.__add__(
        QPointF(arrow_width * math.cos(angle2), arrow_width * math.sin(angle2))
    )

    painter.drawPolygon([m1, m2, arrow_tip], Qt.FillRule.OddEvenFill)

    return painter


def drawCircleRect(
    painter: QPainter,
    x_cord: float,
    y_cord: float,
    radius: float,
    line_color: str = "#000000",
    fill_color: str = "#FFFFFF",
) -> QPainter:
    painter.setPen(QColor.fromString(line_color))
    painter.setBrush(QColor.fromString(fill_color))

    rectangle = QRectF(x_cord, y_cord, radius, radius)
    painter.drawEllipse(rectangle)

    return painter


def drawCirclePoint(
    painter: QPainter,
    point: QPointF,
    radius: float,
    line_color: str = "#000000",
    fill_color: str = "#FFFFFF",
) -> QPainter:
    painter.setPen(QColor.fromString(line_color))
    painter.setBrush(QColor.fromString(fill_color))

    painter.drawEllipse(point, radius, radius)

    return painter
