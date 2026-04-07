import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint

class CCircle:
    RADIUS = 30  # постоянный радиус для всех кругов

    def __init__(self, x: int, y: int):
        self._x = x          # приватные координаты центра
        self._y = y
        self._selected = False  # признак выделения

    #  Проверка попадания точки внутрь круга 
    def contains_point(self, x: int, y: int) -> bool:
        dx = self._x - x
        dy = self._y - y
        return dx * dx + dy * dy <= self.RADIUS * self.RADIUS

    #  Рисование себя на переданном QPainter 
    def draw(self, painter: QPainter):
        if self._selected:
            # выделенный круг — красная толстая обводка + светло-красная заливка
            painter.setBrush(QColor(255, 180, 180))
            painter.setPen(QPen(QColor(200, 0, 0), 3))
        else:
            # обычный круг — синяя обводка + светло-голубая заливка
            painter.setBrush(QColor(173, 216, 230))
            painter.setPen(QPen(QColor(0, 80, 160), 2))

        painter.drawEllipse(
            self._x - self.RADIUS,
            self._y - self.RADIUS,
            self.RADIUS * 2,
            self.RADIUS * 2
        )

    #  Управление выделением 
    def set_selected(self, value: bool):
        self._selected = value

    def is_selected(self) -> bool:
        return self._selected






# 
#  Главное окно
# 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаб. 3, Часть 1 — Круги на форме")
        self.resize(700, 500)

        self._canvas = Canvas(self)
        self.setCentralWidget(self._canvas)

        # строка состояния с подсказками
        self.statusBar().showMessage(
            "ЛКМ — добавить круг | ЛКМ по кругу — выделить | "
            "Ctrl+ЛКМ — мультивыделение | Del — удалить выделенные"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())