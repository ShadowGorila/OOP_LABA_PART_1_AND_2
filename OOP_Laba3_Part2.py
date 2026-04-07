import sys
import json
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QSlider, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIntValidator

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab3_mvc_state.json")


# ===================== MODEL =====================

class NumberModel(QObject):
    changed = pyqtSignal()

    MIN_VALUE = 0
    MAX_VALUE = 100

    def __init__(self):
        super().__init__()
        self._a = 20
        self._b = 50
        self._c = 80
        self._load()  # загрузка БЕЗ emit

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def c(self):
        return self._c

    def set_all(self, a, b, c):
        a = max(self.MIN_VALUE, min(self.MAX_VALUE, a))
        b = max(self.MIN_VALUE, min(self.MAX_VALUE, b))
        c = max(self.MIN_VALUE, min(self.MAX_VALUE, c))

        if (a, b, c) == (self._a, self._b, self._c):
            return  # никаких лишних сигналов

        self._a, self._b, self._c = a, b, c
        self._save()
        self.changed.emit()

    # A — разрешающее поведение
    def set_a(self, value):
        a = max(self.MIN_VALUE, min(self.MAX_VALUE, value))
        b = max(self._b, a)
        c = max(self._c, b)
        self.set_all(a, b, c)

    # B — ограничивающее поведение
    def set_b(self, value):
        b = max(self._a, min(self._c, value))
        self.set_all(self._a, b, self._c)

    # C — разрешающее поведение
    def set_c(self, value):
        c = max(self.MIN_VALUE, min(self.MAX_VALUE, value))
        b = min(self._b, c)
        a = min(self._a, b)
        self.set_all(a, b, c)

    def _save(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({"a": self._a, "b": self._b, "c": self._c}, f)
        except OSError:
            pass

    def _load(self):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            a = int(data["a"])
            b = int(data["b"])
            c = int(data["c"])

            if self.MIN_VALUE <= a <= b <= c <= self.MAX_VALUE:
                self._a, self._b, self._c = a, b, c

        except (OSError, ValueError, KeyError, TypeError):
            pass


# ===================== VIEW (ROW) =====================

class NumberRow(QWidget):
    value_edited = pyqtSignal(int)

    def __init__(self, label, parent=None):
        super().__init__(parent)

        self._updating = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(f"<b>{label}</b>")
        lbl.setFixedWidth(20)
        layout.addWidget(lbl)

        self._line_edit = QLineEdit()
        self._line_edit.setFixedWidth(60)
        self._line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)

        # ВАЛИДАЦИЯ
        self._line_edit.setValidator(
            QIntValidator(NumberModel.MIN_VALUE, NumberModel.MAX_VALUE)
        )

        layout.addWidget(self._line_edit)

        self._spin = QSpinBox()
        self._spin.setRange(NumberModel.MIN_VALUE, NumberModel.MAX_VALUE)
        layout.addWidget(self._spin)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(NumberModel.MIN_VALUE, NumberModel.MAX_VALUE)
        layout.addWidget(self._slider)

        # сигналы
        self._line_edit.editingFinished.connect(self._on_line_edit_done)
        self._spin.valueChanged.connect(self._on_spin_changed)
        self._slider.valueChanged.connect(self._on_slider_changed)

    def set_value(self, value):
        self._updating = True
        self._line_edit.setText(str(value))
        self._spin.setValue(value)
        self._slider.setValue(value)
        self._updating = False

    def _on_line_edit_done(self):
        if self._updating:
            return

        text = self._line_edit.text()
        if text:
            self.value_edited.emit(int(text))
        else:
            self.value_edited.emit(self._slider.value())

    def _on_spin_changed(self, value):
        if not self._updating:
            self.value_edited.emit(value)

    def _on_slider_changed(self, value):
        if not self._updating:
            self.value_edited.emit(value)


# ===================== MAIN WINDOW =====================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Лаб. 3 — MVC")
        self.resize(580, 200)

        self._model = NumberModel()

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        group = QGroupBox("A ≤ B ≤ C (0–100)")
        g_layout = QVBoxLayout(group)

        self._row_a = NumberRow("A")
        self._row_b = NumberRow("B")
        self._row_c = NumberRow("C")

        g_layout.addWidget(self._row_a)
        g_layout.addWidget(self._row_b)
        g_layout.addWidget(self._row_c)

        layout.addWidget(group)

        # счетчик обновлений
        self._update_count = 0
        self._counter = QLabel()
        self._counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._counter)

        # связи
        self._row_a.value_edited.connect(self._model.set_a)
        self._row_b.value_edited.connect(self._model.set_b)
        self._row_c.value_edited.connect(self._model.set_c)

        self._model.changed.connect(self._refresh_view)

        # ОДНО начальное обновление
        self._refresh_view()

    def _refresh_view(self):
        self._update_count += 1
        self._counter.setText(f"Обновлений: {self._update_count}")

        self._row_a.set_value(self._model.a)
        self._row_b.set_value(self._model.b)
        self._row_c.set_value(self._model.c)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())