import os
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QStackedLayout, QWidget

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from src.vista.ui.auth_common import BrandPanel, C_BACKGROUND, C_CREAM
from src.vista.ui.login_ui import LoginForm
from src.vista.ui.register_ui import RegisterForm


class AuthUI(QWidget):
    login_requested = pyqtSignal(str, str)
    register_requested = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("sushUle - Autenticacion")
        self.resize(980, 620)
        self.setMinimumSize(860, 560)
        self.setStyleSheet(f"background-color: {C_BACKGROUND};")

        root = QHBoxLayout(self)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(28)

        self.brand_panel = BrandPanel()
        self.brand_panel.setFixedWidth(340)
        self.brand_panel.setStyleSheet(f"background-color: {C_CREAM}; border-radius: 34px;")
        root.addWidget(self.brand_panel)

        right_side = QWidget()
        self.forms = QStackedLayout(right_side)
        self.forms.setContentsMargins(0, 0, 0, 0)

        self.login_card = LoginForm()
        self.register_card = RegisterForm()

        self.forms.addWidget(self.login_card)
        self.forms.addWidget(self.register_card)
        root.addWidget(right_side, 1)

        self.login_card.submitted.connect(self._submit_login)
        self.login_card.switch_requested.connect(self.show_register)
        self.register_card.submitted.connect(self._submit_register)
        self.register_card.switch_requested.connect(self.show_login)

    def _submit_login(self):
        usuario = self.login_card.user_input.text().strip()
        contrasena = self.login_card.pass_input.text()
        if not usuario or not contrasena:
            self.login_card.show_error("Completa usuario y contrasena.")
            return
        self.login_card.error_label.hide()
        self.login_requested.emit(usuario, contrasena)

    def _submit_register(self):
        nombre = self.register_card.name_input.text().strip()
        usuario = self.register_card.user_input.text().strip()
        contrasena = self.register_card.pass_input.text()
        confirmacion = self.register_card.confirm_input.text()

        if not nombre or not usuario or not contrasena or not confirmacion:
            self.register_card.show_error("Rellena todos los campos.")
            return
        if contrasena != confirmacion:
            self.register_card.show_error("Las contrasenas no coinciden.")
            return
        self.register_card.error_label.hide()
        self.register_requested.emit(nombre, usuario, contrasena)

    def show_login(self):
        self.register_card.clear_fields()
        self.forms.setCurrentWidget(self.login_card)

    def show_register(self):
        self.login_card.clear_fields()
        self.forms.setCurrentWidget(self.register_card)

    def show_login_error(self, message):
        self.login_card.show_error(message)

    def show_register_error(self, message):
        self.register_card.show_error(message)

    def clear_fields(self):
        self.login_card.clear_fields()
        self.register_card.clear_fields()

    def mostrar(self):
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthUI()
    window.show()
    sys.exit(app.exec_())
