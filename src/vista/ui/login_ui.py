from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget


from src.vista.ui.auth_common import asset


class LoginForm(QWidget):

    submitted = pyqtSignal()
    switch_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        ui_file = Path(__file__).resolve().parent.parent / "ui_pyqt" / "login_form.ui"
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
                scaled = pixmap.scaled(
                    self.logo_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.logo_label.setPixmap(scaled)

    def _connect_signals(self):
        self.submit_button.clicked.connect(
            self.submitted.emit
        )

        self.switch_button.clicked.connect(
            self.switch_requested.emit
        )

        self.pass_input.returnPressed.connect(
            self.submitted.emit
        )

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def clear_fields(self):
        self.user_input.clear()
        self.pass_input.clear()
        self.error_label.hide()