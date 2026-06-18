"""
Vista de la gestion de empleados.
"""

import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from src.vista.ui.auth_common import C_BACKGROUND, C_CARD, C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_DIM, C_TEXT_MUTED


class GestionPersonalUI(QWidget):
    volver_menu = pyqtSignal()
    cerrar_sesion = pyqtSignal()
    editar_empleado_requested = pyqtSignal(object)
    guardar_empleado_requested = pyqtSignal(object, str, str, str, str, str)
    eliminar_empleado_requested = pyqtSignal(int)

    def __init__(self, sesion, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self._sesion = sesion
        self._empleados = []
        self._tipos_empleado = []
        self._load_ui()
        self._wire_signals()

    def _ui_path(self, filename):
        return os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", filename)

    def _load_ui(self):
        self.setWindowTitle("sushUle - Gestion de personal")
        self.setMinimumSize(1260, 760)
        self.setStyleSheet(f"background-color: {C_BACKGROUND};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        topbar = QFrame()
        topbar.setObjectName("card")
        topbar.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CARD};
                border-radius: 30px;
            }}
            """
        )
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(18, 14, 18, 14)
        top_layout.setSpacing(12)

        self.back_button = QPushButton("Volver")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_CREAM};
                color: #163246;
                border: none;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: #F3E6D8;
            }}
            """
        )
        top_layout.addWidget(self.back_button)

        title = QLabel("Gestion de personal")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 800;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        self.logout_button = QPushButton("Cerrar sesion")
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 700;
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE_DARK};
            }}
            """
        )
        top_layout.addWidget(self.logout_button)

        root.addWidget(topbar)

        content = QHBoxLayout()
        content.setSpacing(18)

        self.left_card = QFrame()
        self.right_card = QFrame()
        uic.loadUi(self._ui_path("GestionPersonalListaUI.ui"), self.left_card)
        uic.loadUi(self._ui_path("GestionPersonalFormularioUI.ui"), self.right_card)

        content.addWidget(self.left_card, 7)
        content.addWidget(self.right_card, 5)
        root.addLayout(content, 1)

        self.table = self.left_card.findChild(QTableWidget, "table")
        self.empty_label = self.left_card.findChild(QLabel, "empty_label")
        self.status_label = self.right_card.findChild(QLabel, "status_label")
        self.ssn_input = self.right_card.findChild(QLineEdit, "ssn_input")
        self.user_input = self.right_card.findChild(QLineEdit, "user_input")
        self.correo_input = self.right_card.findChild(QLineEdit, "correo_input")
        self.pass_input = self.right_card.findChild(QLineEdit, "pass_input")
        self.tipo_input = self.right_card.findChild(QComboBox, "tipo_input")
        self.clear_button = self.right_card.findChild(QPushButton, "clear_button")
        self.save_button = self.right_card.findChild(QPushButton, "save_button")

        if self.table is not None:
            self.table.verticalHeader().setVisible(False)
            self.table.setSelectionMode(QTableWidget.NoSelection)
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.table.setShowGrid(False)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)

        if self.tipo_input is not None:
            self.tipo_input.setEditable(False)

    def _wire_signals(self):
        self.back_button.clicked.connect(self._go_back)
        self.logout_button.clicked.connect(lambda checked=False: self.cerrar_sesion.emit())
        self.clear_button.clicked.connect(self.activar_modo_creacion)
        self.save_button.clicked.connect(self._emit_guardar_requested)

    def inicializar_tipos(self, tipos):
        self._tipos_empleado = [str(tipo).strip().upper() for tipo in (tipos or []) if str(tipo).strip()]
        current = self.tipo_input.currentText()
        self.tipo_input.clear()
        self.tipo_input.addItems(self._tipos_empleado)
        if current in self._tipos_empleado:
            self.tipo_input.setCurrentText(current)
        elif self._tipos_empleado:
            self.tipo_input.setCurrentIndex(0)

    def set_empleados(self, empleados):
        self._empleados = list(empleados or [])
        self.status_label.setText("")
        self._refresh_table()

    def mostrar_info(self, mensaje):
        self.status_label.setText(str(mensaje))

    def mostrar_error(self, mensaje):
        self._empleados = []
        self.status_label.setText(str(mensaje))
        self._refresh_table()

    def activar_modo_edicion(self, empleado):
        self.ssn_input.setText(str(getattr(empleado, "ssn", "")))
        self.user_input.setText(str(getattr(empleado, "usuario", "")))
        self.correo_input.setText(str(getattr(empleado, "correo", "")))
        self.pass_input.clear()
        tipo = str(getattr(empleado, "tipo", "")).upper()
        if tipo:
            self.tipo_input.setCurrentText(tipo)
        self.save_button.setText("Guardar cambios")
        self.status_label.setText(f"Editando empleado #{getattr(empleado, 'id_empleado', '')}")

    def activar_modo_creacion(self):
        self.ssn_input.clear()
        self.user_input.clear()
        self.correo_input.clear()
        self.pass_input.clear()
        if self._tipos_empleado:
            self.tipo_input.setCurrentIndex(0)
        self.save_button.setText("Guardar")
        self.status_label.setText("Formulario listo para un nuevo empleado.")

    def _refresh_table(self):
        self.table.setRowCount(len(self._empleados))
        for row, empleado in enumerate(self._empleados):
            self._set_item(self.table, row, 0, empleado.id_empleado)
            self._set_item(self.table, row, 1, empleado.tipo)
            self._set_item(self.table, row, 2, empleado.usuario)
            self._set_item(self.table, row, 3, empleado.correo)
            self._set_item(self.table, row, 4, empleado.ssn)
            self.table.setCellWidget(
                row,
                5,
                self._build_row_button(
                    "Editar",
                    lambda checked=False, emp=empleado: self.editar_empleado_requested.emit(emp),
                ),
            )
            self.table.setCellWidget(
                row,
                6,
                self._build_row_button(
                    "Eliminar",
                    lambda checked=False, emp=empleado: self._confirmar_eliminar(emp),
                ),
            )
            self.table.setRowHeight(row, 54)

        has_rows = bool(self._empleados)
        self.table.setVisible(has_rows)
        self.empty_label.setVisible(not has_rows)

    def _set_item(self, table, row, column, value):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, column, item)

    def _build_row_button(self, text, slot):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 11px;
                font-weight: 700;
                padding: 7px 12px;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE_DARK};
            }}
            """
        )
        button.clicked.connect(slot)
        return button

    def _collect_form_data(self):
        return {
            "ssn": self.ssn_input.text(),
            "usuario": self.user_input.text(),
            "correo": self.correo_input.text(),
            "contrasena": self.pass_input.text(),
            "tipo": self.tipo_input.currentText(),
        }

    def _emit_guardar_requested(self):
        datos = self._collect_form_data()
        self.guardar_empleado_requested.emit(
            None,
            datos["ssn"],
            datos["usuario"],
            datos["correo"],
            datos["contrasena"],
            datos["tipo"],
        )

    def _confirmar_eliminar(self, empleado):
        self.eliminar_empleado_requested.emit(empleado.id_empleado)

    def _go_back(self, checked=False):
        self.volver_menu.emit()
