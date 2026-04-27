from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from src.vista.ui.auth_common import C_BACKGROUND, C_CARD, C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_MUTED


class AdminDashboardUI(QWidget):
    productos_clicked = pyqtSignal()
    personal_clicked = pyqtSignal()
    cerrar_sesion = pyqtSignal()

    def __init__(self, sesion, parent=None):
        super().__init__(parent)
        self._sesion = sesion
        self._build()

    def _build(self):
        self.setWindowTitle("sushUle - Panel de administracion")
        self.setMinimumSize(980, 640)
        self.setStyleSheet(f"background-color: {C_BACKGROUND};")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(20)

        header = QFrame()
        header.setObjectName("card")
        header.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CARD};
                border-radius: 34px;
            }}
            """
        )
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(28, 28, 28, 28)
        header_layout.setSpacing(10)

        top_row = QHBoxLayout()
        title = QLabel("Panel de administracion")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 800;")
        top_row.addWidget(title)
        top_row.addStretch()

        logout_button = QPushButton("Cerrar sesion")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE_DARK};
            }}
            """
        )
        logout_button.clicked.connect(lambda checked=False: self.cerrar_sesion.emit())
        top_row.addWidget(logout_button)
        header_layout.addLayout(top_row)

        greeting = QLabel(f"HOLA {self._sesion.nombre}")
        greeting.setStyleSheet("color: white; font-size: 34px; font-weight: 900;")
        greeting.setWordWrap(True)
        header_layout.addWidget(greeting)

        subtitle = QLabel("Desde aqui puedes entrar al area de productos o gestionar al personal de cocina y caja.")
        subtitle.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 14px;")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        root.addWidget(header)

        actions = QHBoxLayout()
        actions.setSpacing(18)

        products_card = self._build_action_card(
            "Administrar productos",
            "Crear, editar y eliminar productos y promociones.",
        )
        products_card.clicked.connect(lambda checked=False: self.productos_clicked.emit())

        staff_card = self._build_action_card(
            "Gestionar personal",
            "Dar de alta, modificar o borrar cajeros y personal de cocina.",
        )
        staff_card.clicked.connect(lambda checked=False: self.personal_clicked.emit())

        actions.addWidget(products_card, 1)
        actions.addWidget(staff_card, 1)
        root.addLayout(actions, 1)

    def _build_action_card(self, title_text, body_text):
        button = QPushButton()
        button.setCursor(Qt.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_CREAM};
                border: none;
                border-radius: 32px;
                padding: 26px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #F3E6D8;
            }}
            """
        )

        layout = QVBoxLayout(button)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel(title_text)
        title.setStyleSheet("color: #163246; font-size: 24px; font-weight: 800;")
        title.setWordWrap(True)
        body = QLabel(body_text)
        body.setStyleSheet("color: #4B6473; font-size: 14px;")
        body.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(body)
        layout.addStretch()
        return button
