import os
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QStackedLayout, QVBoxLayout, QWidget

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from src.vista.ui.auth_common import BrandPanel, C_BACKGROUND, C_CREAM
from src.vista.ui.login_ui import LoginForm
from src.vista.ui.register_ui import RegisterForm


class AuthPopup(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.message = message
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self._build()

    def _build(self):
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: #072D44;
                border: 2px solid #FC814A;
                border-radius: 24px;
            }
            """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        top = QHBoxLayout()
        top.addStretch()

        close_button = QPushButton("X")
        close_button.setFixedSize(34, 34)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FC814A;
                color: white;
                border: none;
                border-radius: 17px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #E66E3A;
            }
            """
        )
        close_button.clicked.connect(self.accept)
        top.addWidget(close_button)

        label = QLabel(self.message)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("color: white; font-size: 16px; font-weight: 700;")

        layout.addLayout(top)
        layout.addWidget(label)
        root.addWidget(card)
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
        self.login_popup = None

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    from src.controlador.ControladorPrincipalNuevo import ControladorPrincipal
    from src.modelo.Logica import Logica
    from src.vista.LoginNueva import MiVentana

    window = MiVentana()
    modelo = Logica()
    controlador = ControladorPrincipal(window, modelo)
    window.controlador = controlador
    window.show()
    sys.exit(app.exec_())
