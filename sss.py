import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit,
    QCheckBox, QRadioButton, QComboBox, QSpinBox,
    QSlider, QProgressBar, QListWidget, QTabWidget,
    QGroupBox, QMenuBar, QMenu, QStatusBar, QSplitter,
    QColorDialog
)
from PyQt6.QtGui import QPainter, QColor, QPen, QAction, QFont
from PyQt6.QtCore import Qt, QTimer, QPoint


class DrawCanvas(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dynamic_buttons: list[QPushButton] = []
        self.points: list[QPoint] = []
        self.setMinimumHeight(120)
        self.setStyleSheet("background-color: #f0f4ff; border: 1px solid #aaa;")

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor("#3a6fc4"), 6)
        painter.setPen(pen)
        for pt in self.points:
            painter.drawEllipse(pt, 4, 4)
        painter.end()

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        if event.button() == Qt.MouseButton.LeftButton:
            self.points.append(pos)
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self._create_dynamic_button(pos)

    def _create_dynamic_button(self, pos: QPoint):
        btn = QPushButton(f"Кнопка #{len(self.dynamic_buttons) + 1}", self)
        btn.move(pos)
        btn.resize(110, 30)
        btn.clicked.connect(lambda checked, b=btn: self._on_dynamic_click(b))
        btn.show()
        self.dynamic_buttons.append(btn)

    def _on_dynamic_click(self, btn: QPushButton):
        btn.setText("Нажата!")
        btn.setStyleSheet("background-color: #c8f7c5;")

    def clear_canvas(self):
        self.points.clear()
        for btn in self.dynamic_buttons:
            btn.deleteLater()
        self.dynamic_buttons.clear()
        self.update()


class StopwatchWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._elapsed_ms = 0
        self._running = False
        self._timer = QTimer(self)
        self._timer.setInterval(10)
        self._timer.timeout.connect(self._on_tick)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.display = QLabel("00:00.00")
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setStyleSheet(
            "font-size: 52px; font-family: monospace; font-weight: bold;"
            "color: #1a1a2e; background: #e8eaf6; border-radius: 12px; padding: 16px 32px;"
        )
        layout.addWidget(self.display)

        btn_row = QHBoxLayout()

        self.btn_start = QPushButton("Старт")
        self.btn_start.setFixedHeight(40)
        self.btn_start.setStyleSheet("background:#4caf50; color:white; font-size:14px; border-radius:6px;")
        self.btn_start.clicked.connect(self._on_start)

        self.btn_stop = QPushButton("Стоп")
        self.btn_stop.setFixedHeight(40)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("background:#f44336; color:white; font-size:14px; border-radius:6px;")
        self.btn_stop.clicked.connect(self._on_stop)

        self.btn_reset = QPushButton("Сброс")
        self.btn_reset.setFixedHeight(40)
        self.btn_reset.setStyleSheet("background:#2196f3; color:white; font-size:14px; border-radius:6px;")
        self.btn_reset.clicked.connect(self._on_reset)

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_reset)
        layout.addLayout(btn_row)

        self.lap_list = QListWidget()
        self.lap_list.setMaximumHeight(120)
        layout.addWidget(QLabel("Отсечки:"))
        layout.addWidget(self.lap_list)

        btn_lap = QPushButton("Отсечка")
        btn_lap.clicked.connect(self._on_lap)
        layout.addWidget(btn_lap)

    def _on_tick(self):
        self._elapsed_ms += 10
        self._update_display()

    def _on_start(self):
        if not self._running:
            self._running = True
            self._timer.start()
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)

    def _on_stop(self):
        if self._running:
            self._running = False
            self._timer.stop()
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.lap_list.addItem(f"Стоп #{self.lap_list.count() + 1}: {self._format_time()}")
            self.lap_list.scrollToBottom()

    def _on_reset(self):
        self._timer.stop()
        self._running = False
        self._elapsed_ms = 0
        self._update_display()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lap_list.clear()

    def _on_lap(self):
        if self._running:
            self.lap_list.addItem(f"Отсечка #{self.lap_list.count() + 1}: {self._format_time()}")
            self.lap_list.scrollToBottom()

    def _update_display(self):
        self.display.setText(self._format_time())

    def _format_time(self) -> str:
        total_cs = self._elapsed_ms // 10
        minutes = total_cs // 6000
        seconds = (total_cs % 6000) // 100
        centis  = total_cs % 100
        return f"{minutes:02d}:{seconds:02d}.{centis:02d}"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаба 1 — Кнопки и Формы (PyQt6)")
        self.resize(900, 700)
        self._click_counter = 0
        self._build_menu()
        self._build_status_bar()
        self._build_ui()

    def _build_menu(self):
        menubar: QMenuBar = self.menuBar()

        file_menu: QMenu = menubar.addMenu("Файл")
        act_clear = QAction("Очистить холст", self)
        act_clear.triggered.connect(self._on_menu_clear)
        file_menu.addAction(act_clear)
        act_exit = QAction("Выход", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        view_menu: QMenu = menubar.addMenu("Вид")
        act_color = QAction("Выбрать цвет фона", self)
        act_color.triggered.connect(self._on_menu_color)
        view_menu.addAction(act_color)

    def _on_menu_clear(self):
        self.canvas.clear_canvas()
        self.status_label.setText("Холст очищен")

    def _on_menu_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.canvas.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #aaa;")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)

        tabs = QTabWidget()
        tabs.currentChanged.connect(lambda idx: self.status_label.setText(f"Открыта вкладка {idx + 1}"))
        root_layout.addWidget(tabs)

        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tabs.addTab(tab1, "Базовые виджеты")

        self.info_label = QLabel("Введите текст ниже и нажмите кнопку")
        self.info_label.setFont(QFont("Arial", 11))
        tab1_layout.addWidget(self.info_label)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Введите что-нибудь...")
        self.line_edit.textChanged.connect(self._on_text_changed)
        tab1_layout.addWidget(self.line_edit)

        btn_row = QHBoxLayout()
        for label in ("Кнопка А", "Кнопка Б", "Кнопка В"):
            btn = QPushButton(label)
            btn.clicked.connect(self._shared_button_handler)
            btn_row.addWidget(btn)
        tab1_layout.addLayout(btn_row)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Лог событий появится здесь...")
        self.text_edit.setMaximumHeight(90)
        tab1_layout.addWidget(self.text_edit)

        self.chk_bold = QCheckBox("Жирный текст в label")
        self.chk_bold.stateChanged.connect(self._on_checkbox_changed)
        tab1_layout.addWidget(self.chk_bold)

        group_radio = QGroupBox("Размер шрифта")
        radio_layout = QHBoxLayout(group_radio)
        self.radio_small = QRadioButton("Маленький")
        self.radio_large = QRadioButton("Большой")
        self.radio_small.setChecked(True)
        self.radio_small.toggled.connect(self._on_radio_changed)
        radio_layout.addWidget(self.radio_small)
        radio_layout.addWidget(self.radio_large)
        tab1_layout.addWidget(group_radio)

        self.combo = QComboBox()
        self.combo.addItems(["Опция 1", "Опция 2", "Опция 3"])
        self.combo.currentTextChanged.connect(
            lambda text: self._log(f"Выбрано в комбобоксе: {text}")
        )
        tab1_layout.addWidget(QLabel("Выпадающий список:"))
        tab1_layout.addWidget(self.combo)

        spin_row = QHBoxLayout()
        self.spin = QSpinBox()
        self.spin.setRange(0, 100)
        self.spin.setValue(30)
        self.spin.valueChanged.connect(self._on_spin_changed)
        spin_row.addWidget(QLabel("SpinBox → ProgressBar:"))
        spin_row.addWidget(self.spin)
        tab1_layout.addLayout(spin_row)

        self.progress = QProgressBar()
        self.progress.setValue(30)
        tab1_layout.addWidget(self.progress)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(30)
        self.slider.valueChanged.connect(self._on_slider_changed)
        tab1_layout.addWidget(QLabel("Слайдер:"))
        tab1_layout.addWidget(self.slider)

        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tabs.addTab(tab2, "Холст (Paint + мышь)")

        hint = QLabel(
            "ЛКМ — нарисовать точку (paintEvent)\n"
            "ПКМ — создать кнопку динамически\n"
            "Кнопка «Очистить» — удалить всё"
        )
        hint.setStyleSheet("color: #555; font-size: 10px;")
        tab2_layout.addWidget(hint)

        self.canvas = DrawCanvas()
        tab2_layout.addWidget(self.canvas)

        btn_clear_canvas = QPushButton("Очистить холст")
        btn_clear_canvas.clicked.connect(self.canvas.clear_canvas)
        tab2_layout.addWidget(btn_clear_canvas)

        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tabs.addTab(tab3, "Список")

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.list_widget = QListWidget()
        self.list_widget.addItems([f"Элемент {i}" for i in range(1, 8)])
        self.list_widget.currentTextChanged.connect(
            lambda text: self._log(f"Выбран в списке: {text}")
        )
        splitter.addWidget(self.list_widget)

        btn_add_item = QPushButton("Добавить элемент в список")
        btn_add_item.clicked.connect(self._on_add_list_item)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(btn_add_item)
        right_layout.addStretch()
        splitter.addWidget(right_panel)

        tab3_layout.addWidget(splitter)

        stopwatch = StopwatchWidget()
        tabs.addTab(stopwatch, "Секундомер")

    def _build_status_bar(self):
        self.status_label = QLabel("Готово")
        self.statusBar().addWidget(self.status_label)

    def _on_text_changed(self, text: str):
        self.info_label.setText(f"Вы пишете: {text}" if text else "Введите текст ниже и нажмите кнопку")

    def _shared_button_handler(self):
        self._click_counter += 1
        sender_btn: QPushButton = self.sender()
        msg = f"[Кнопка] нажата '{sender_btn.text()}', всего нажатий: {self._click_counter}"
        self._log(msg)
        self.status_label.setText(msg)

    def _on_checkbox_changed(self, state: int):
        font = self.info_label.font()
        font.setBold(state == Qt.CheckState.Checked.value)
        self.info_label.setFont(font)
        self._log(f"Жирный текст: {'ВКЛ' if state else 'ВЫКЛ'}")

    def _on_radio_changed(self):
        font = self.info_label.font()
        font.setPointSize(14 if self.radio_large.isChecked() else 10)
        self.info_label.setFont(font)

    def _on_spin_changed(self, value: int):
        self.progress.setValue(value)
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)

    def _on_slider_changed(self, value: int):
        self.progress.setValue(value)
        self.spin.blockSignals(True)
        self.spin.setValue(value)
        self.spin.blockSignals(False)

    def _on_add_list_item(self):
        count = self.list_widget.count() + 1
        self.list_widget.addItem(f"Новый элемент {count}")

    def keyPressEvent(self, event):
        try:
            key_name = Qt.Key(event.key()).name
        except ValueError:
            key_name = str(event.key())
        self._log(f"[keyPressEvent] клавиша: {key_name}")
        self.status_label.setText(f"Нажата клавиша: {key_name}")
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        self.statusBar().showMessage(f"Мышь: x={pos.x()}, y={pos.y()}", 500)
        super().mouseMoveEvent(event)

    def resizeEvent(self, event):
        size = event.size()
        self.status_label.setText(f"Окно: {size.width()}×{size.height()}")
        super().resizeEvent(event)

    def _log(self, message: str):
        self.text_edit.append(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())