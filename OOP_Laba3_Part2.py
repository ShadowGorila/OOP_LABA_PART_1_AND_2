import sys
import json
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QSlider, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab3_mvc_state.json")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаб. 3, Часть 2 — MVC")
        self.setMinimumSize(480, 180)
        self.resize(580, 200)

        self._model = NumberModel()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(14, 14, 14, 14)

        group = QGroupBox("Числа A, B, C  (всегда A ≤ B ≤ C,  диапазон 0 – 100)")
        g_layout = QVBoxLayout(group)
        g_layout.setSpacing(10)

        self._row_a = NumberRow("A")
        self._row_b = NumberRow("B")
        self._row_c = NumberRow("C")

        g_layout.addWidget(self._row_a)
        g_layout.addWidget(self._row_b)
        g_layout.addWidget(self._row_c)
        main_layout.addWidget(group)

        self._update_count = 0
        self._counter_lbl = QLabel("Обновлений вида: 0")
        self._counter_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._counter_lbl.setStyleSheet("color: #888; font-size: 11px;")
        main_layout.addWidget(self._counter_lbl)

        self._row_a.value_edited.connect(self._model.set_a)
        self._row_b.value_edited.connect(self._model.set_b)
        self._row_c.value_edited.connect(self._model.set_c)

        self._model.changed.connect(self._refresh_view)

    def _refresh_view(self):
        self._update_count += 1
        self._counter_lbl.setText(f"Обновлений вида: {self._update_count}")
        self._row_a.set_value(self._model.a)
        self._row_b.set_value(self._model.b)
        self._row_c.set_value(self._model.c)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())