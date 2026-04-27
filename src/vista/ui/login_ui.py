import os
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from src.vista.ui.auth_common import C_CARD, C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_DIM, C_TEXT_MUTED, IconInput, asset


class LoginForm(QWidget):
    submitted = pyqtSignal()
    switch_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_px = None
        self._load_assets()
        self._build()

    def _load_assets(self):
        logo_path = (
            asset("logos", "sushule_logo_circulo.png")
            or asset("logos", "sushule_logo.png")
            or asset("logos", "sushule_logo.jpeg")
        )
        self.logo_px = QPixmap(logo_path) if logo_path else None

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CARD};
                border-radius: 34px;
            }}
            """
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(34, 34, 34, 24)
        card_layout.setSpacing(0)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(18)

        header_text = QVBoxLayout()
        header_text.setSpacing(6)

        title = QLabel("Iniciar sesion")
        title.setWordWrap(True)
        title.setFixedWidth(210)
        title.setStyleSheet("color: white; font-size: 26px; font-weight: 700;")

        subtitle = QLabel("Accede a tu cuenta y sigue con tu pedido.")
        subtitle.setWordWrap(True)
        subtitle.setFixedWidth(210)
        subtitle.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 14px;")

        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_text.addStretch()
        header_row.addLayout(header_text, 1)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(108, 108)
        self.logo_label.setStyleSheet("background: transparent;")
        self.logo_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        if self.logo_px and not self.logo_px.isNull():
            scaled_logo = self.logo_px.scaled(
                self.logo_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.logo_label.setPixmap(scaled_logo)
        header_row.addWidget(self.logo_label, 0, Qt.AlignTop)

        card_layout.addLayout(header_row)
        card_layout.addSpacing(26)

        self.user_input = IconInput("Correo o usuario", "@")
        self.pass_input = IconInput("Contrasena", "*", password=True)
        card_layout.addWidget(self.user_input)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.pass_input)
        card_layout.addSpacing(12)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(f"color: {C_ORANGE}; font-size: 12px;")
        self.error_label.hide()
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(12)

        self.submit_button = QPushButton("Acceder   >")
        self.submit_button.setMinimumHeight(58)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.submit_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                border-radius: 29px;
                font-size: 17px;
                font-weight: 700;
                text-align: center;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE_DARK};
            }}
            """
        )
        card_layout.addWidget(self.submit_button)
        card_layout.addSpacing(18)

        footer = QHBoxLayout()
        footer.addStretch()

        footer_text = QLabel("No tienes cuenta?")
        footer_text.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 12px;")

        self.switch_button = QPushButton("Registrate")
        self.switch_button.setCursor(Qt.PointingHandCursor)
        self.switch_button.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {C_CREAM};
                font-size: 12px;
                text-decoration: underline;
            }}
            QPushButton:hover {{
                color: {C_ORANGE};
            }}
            """
        )

        footer.addWidget(footer_text)
        footer.addWidget(self.switch_button)
        footer.addStretch()
        card_layout.addLayout(footer)

        root.addWidget(card)

        self.submit_button.clicked.connect(self.submitted.emit)
        self.pass_input.returnPressed.connect(self.submitted.emit)
        self.switch_button.clicked.connect(self.switch_requested.emit)

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def clear_fields(self):
        self.user_input.clear()
        self.pass_input.clear()
        self.error_label.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginForm()
    window.resize(520, 560)
    window.show()
    sys.exit(app.exec_())
