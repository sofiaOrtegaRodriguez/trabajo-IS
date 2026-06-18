from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from src.vista.ui.auth_common import asset


class RegisterForm(QWidget):

    submitted = pyqtSignal()
    switch_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        ui_file = (
            Path(__file__).resolve().parent.parent
            / "ui_pyqt"
            / "register_form.ui"
        )

        uic.loadUi(str(ui_file), self)

        self._load_logo()
        self._connect_signals()

    def _load_logo(self):

        logo_path = (
            asset("logos", "sushule_logo_circulo.png")
            or asset("logos", "sushule_logo.png")
            or asset("logos", "sushule_logo.jpeg")
        )

        if logo_path:
            pixmap = QPixmap(logo_path)

            if not pixmap.isNull():
                self.logo_label.setPixmap(
                    pixmap.scaled(
                        self.logo_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )

    def _connect_signals(self):

        self.submit_button.clicked.connect(
            self.submitted.emit
        )

        self.confirm_input.returnPressed.connect(
            self.submitted.emit
        )

        self.switch_button.clicked.connect(
            self.switch_requested.emit
        )

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def clear_fields(self):
        self.name_input.clear()
        self.user_input.clear()
        self.pass_input.clear()
        self.confirm_input.clear()
        self.error_label.hide()