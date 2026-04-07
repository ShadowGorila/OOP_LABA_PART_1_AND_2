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



class CircleStorage:
    def __init__(self):
        self._items: list[CCircle] = []   # приватное хранилище

    def add(self, circle: CCircle):
        # Добавляет круг в контейнер.
        self._items.append(circle)

    def remove_selected(self):
        # Удаляет все выделенные круги из контейнера.
        self._items = [c for c in self._items if not c.is_selected()]

    def count(self) -> int:
        # Количество кругов в контейнере.
        return len(self._items)

    def get(self, index: int) -> CCircle:
        # Получить круг по индексу.
        return self._items[index]

    def __iter__(self):
        # Итерация: for circle in storage.
        return iter(self._items)

    def deselect_all(self):
        # Снять выделение со всех кругов.
        for circle in self._items:
            circle.set_selected(False)

    def find_at(self, x: int, y: int) -> list[CCircle]:
        # Найти все круги, в которые попала точка (x, y).
        return [c for c in self._items if c.contains_point(x, y)]


class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._storage = CircleStorage()   # контейнер всех кругов
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)   # чтобы ловить клавиши
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: white;")

    #  Перерисовка (событие Paint) 
    def paintEvent(self, event):
        # Всё объекты из контейнера отрисовываются при каждом Paint.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # рисуем каждый круг — сам объект знает, как себя нарисовать
        for circle in self._storage:
            circle.draw(painter)

        # подсказка, если кругов нет
        if self._storage.count() == 0:
            painter.setPen(QColor(180, 180, 180))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Кликните ЛКМ, чтобы добавить круг")


    def mousePressEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())
        ctrl_held = event.modifiers() & Qt.KeyboardModifier.ControlModifier

        if event.button() == Qt.MouseButton.LeftButton:
            hits = self._storage.find_at(x, y)

            if hits:
                #  клик по кругу — выделение 
                if not ctrl_held:
                    # без Ctrl: снять все, выделить только верхний
                    self._storage.deselect_all()
                    for c in hits:
                        c.set_selected(True)
                else:
                    for c in hits:
                        c.set_selected(not c.is_selected())  # с Ctrl: переключить выделение
            else:
                #  клик по пустому месту — создать новый круг 
                if not ctrl_held:
                    self._storage.deselect_all()
                new_circle = CCircle(x, y)
                self._storage.add(new_circle)

            self.update()   # запросить перерисовку

    #  Нажатие клавиши 
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            # удалить все выделенные круги
            self._storage.remove_selected()
            self.update()

    #  Изменение размера окна 
    def resizeEvent(self, event):
        # Обрабатываем изменение размера — просто перерисовываем.
        super().resizeEvent(event)
        self.update()


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