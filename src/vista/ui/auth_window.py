import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QDialog, QLabel, QWidget

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from src.vista.ui.auth_common import asset, C_BACKGROUND, C_CREAM
from src.vista.ui.login_ui import LoginForm
from src.vista.ui.register_ui import RegisterForm


class BrandPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_file = os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", "BrandPanel.ui")
        uic.loadUi(ui_file, self)
        self.sushi_px = None
        self.brush_px = None
        self._load_assets()

    def _load_assets(self):
        sushi_path = asset("fondos", "sushi_plate.png")
        brush_path = asset("fondos", "brush_stroke.png")
        if sushi_path:
            self.sushi_px = QPixmap(sushi_path)
        if brush_path:
            self.brush_px = QPixmap(brush_path)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render_hero()

    def _render_hero(self):
        hero = self.findChild(QLabel, "hero_label")
        if hero is None:
            return

        width = max(220, hero.width())
        height = max(200, hero.height())
        canvas = QPixmap(width, height)
        canvas.fill(Qt.transparent)

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if self.brush_px and not self.brush_px.isNull():
            brush = self.brush_px.scaled(int(width * 0.95), int(height * 0.55), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap((width - brush.width()) // 2, int(height * 0.18), brush)

        if self.sushi_px and not self.sushi_px.isNull():
            sushi = self.sushi_px.scaled(int(width * 0.72), int(height * 0.72), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap((width - sushi.width()) // 2, (height - sushi.height()) // 2, sushi)

        painter.setPen(QPen(QColor("#0B273A"), 2))
        for cx, cy, size in ((28, 28, 8), (width - 34, 52, 7), (width - 46, height - 36, 10)):
            painter.drawLine(cx - size, cy, cx + size, cy)
            painter.drawLine(cx, cy - size, cx, cy + size)
        painter.end()

        hero.setPixmap(canvas)


class AuthPopup(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.message = message
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", "AuthPopup.ui"), self)
        self.close_button.clicked.connect(self.accept)
        self.message_label.setText(self.message)
        self.setFixedSize(360, 150)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)


class AuthUI(QWidget):
    login_requested = pyqtSignal(str, str)
    register_requested = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("sushUle - Autenticacion")
        self.resize(980, 620)
        self.setMinimumSize(980, 620)
        self.setStyleSheet(f"background-color: {C_BACKGROUND};")
        uic.loadUi(os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", "AuthUI.ui"), self)

        self.brand_panel = BrandPanel(self.brand_host)
        self.brand_host.layout().addWidget(self.brand_panel)

        self.login_card = LoginForm()
        self.register_card = RegisterForm()
        self.forms_host.layout().addWidget(self.login_card)
        self.forms_host.layout().addWidget(self.register_card)
        self.forms_host.layout().setCurrentWidget(self.login_card)
        self.login_popup = None

        self.login_card.submitted.connect(self._submit_login)
        self.login_card.switch_requested.connect(self.show_register)
        self.register_card.submitted.connect(self._submit_register)
        self.register_card.switch_requested.connect(self.show_login)

    def _submit_login(self):
        correo = self.login_card.user_input.text().strip()
        contrasena = self.login_card.pass_input.text()
        self.login_requested.emit(correo, contrasena)

    def _submit_register(self):
        nombre = self.register_card.name_input.text().strip()
        correo = self.register_card.user_input.text().strip()
        contrasena = self.register_card.pass_input.text()
        self.register_requested.emit(nombre, correo, contrasena)

    def show_login(self):
        self.register_card.clear_fields()
        self.forms_host.layout().setCurrentWidget(self.login_card)

    def show_register(self):
        self.login_card.clear_fields()
        self.forms_host.layout().setCurrentWidget(self.register_card)

    def show_login_error(self, message):
        self.login_card.show_error(message)

    def show_center_popup(self, message):
        self.login_popup = AuthPopup(message, self)
        position = self.rect().center() - self.login_popup.rect().center()
        self.login_popup.move(self.mapToGlobal(position))
        self.login_popup.exec_()

    def show_register_error(self, message):
        self.register_card.show_error(message)

    def clear_fields(self):
        self.login_card.clear_fields()
        self.register_card.clear_fields()

    def mostrar(self):
        self.show()
