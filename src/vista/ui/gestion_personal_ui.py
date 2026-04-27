import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if __package__ is None or __package__ == "":
    import os

    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from PyQt5.QtWidgets import QApplication

from src.controlador.ControladorEmpleados import ControladorEmpleados
from src.modelo.Logica import Logica
from src.modelo.vo.SesionVo import SesionVo
from src.vista.ui.auth_common import C_BACKGROUND, C_CARD, C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_DIM, C_TEXT_MUTED


class GestionPersonalUI(QWidget):
    volver_menu = pyqtSignal()
    cerrar_sesion = pyqtSignal()

    def __init__(self, controlador, sesion, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.controlador = controlador
        self._sesion = sesion
        self._empleados = []
        self._editing_id = None
        self._build()
        self._load_empleados()

    def _build(self):
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

        back_button = QPushButton("Volver")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setStyleSheet(
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
        back_button.clicked.connect(self._go_back)
        top_layout.addWidget(back_button)

        title = QLabel("Gestion de personal")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 800;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        logout_button = QPushButton("Cerrar sesion")
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.setStyleSheet(
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
        logout_button.clicked.connect(lambda checked=False: self.cerrar_sesion.emit())
        top_layout.addWidget(logout_button)
        root.addWidget(topbar)

        content = QHBoxLayout()
        content.setSpacing(18)

        table_card = self._build_table_card()
        form_card = self._build_form_card()

        content.addWidget(table_card, 7)
        content.addWidget(form_card, 5)
        root.addLayout(content, 1)

    def _build_table_card(self):
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CREAM};
                border-radius: 32px;
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        title = QLabel("Personal de cocina y caja")
        title.setStyleSheet("color: #163246; font-size: 22px; font-weight: 800;")
        layout.addWidget(title)

        subtitle = QLabel("Aqui puedes dar de alta, editar o eliminar empleados.")
        subtitle.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 12px;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Tipo", "Usuario", "Correo", "SSN", "Editar", "Eliminar"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: white;
                border: none;
                border-radius: 24px;
                color: #163246;
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                padding: 10px;
                font-size: 12px;
                font-weight: 700;
            }}
            """
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)

        self.empty_label = QLabel("Todavia no hay empleados cargados.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 16px; font-weight: 700;")
        layout.addWidget(self.empty_label)
        return card

    def _build_form_card(self):
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CREAM};
                border-radius: 32px;
            }}
            QLabel {{
                color: #163246;
            }}
            QLineEdit, QComboBox {{
                background-color: white;
                border: 1px solid #D8C8BA;
                border-radius: 18px;
                color: #163246;
                font-size: 14px;
                padding: 10px 12px;
            }}
            """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        title = QLabel("Nuevo / editar empleado")
        title.setStyleSheet("color: #163246; font-size: 22px; font-weight: 800;")
        layout.addWidget(title)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(self.status_label)

        self.ssn_input = QLineEdit()
        self.ssn_input.setPlaceholderText("11 digitos")
        self.user_input = QLineEdit()
        self.correo_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.tipo_input = QComboBox()
        self.tipo_input.addItems(["CAJERO", "COCINA"])

        layout.addWidget(QLabel("SSN"))
        layout.addWidget(self.ssn_input)
        layout.addWidget(QLabel("Usuario"))
        layout.addWidget(self.user_input)
        layout.addWidget(QLabel("Correo"))
        layout.addWidget(self.correo_input)
        layout.addWidget(QLabel("Contrasena"))
        layout.addWidget(self.pass_input)
        layout.addWidget(QLabel("Tipo"))
        layout.addWidget(self.tipo_input)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_CREAM};
                color: #163246;
                border: 1px solid #D8C8BA;
                border-radius: 18px;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 14px;
            }}
            QPushButton:hover {{
                background-color: #F3E6D8;
            }}
            """
        )
        self.save_button = QPushButton("Guardar")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                border-radius: 18px;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 14px;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE_DARK};
            }}
            """
        )
        self.clear_button.clicked.connect(self._clear_form)
        self.save_button.clicked.connect(self._save_employee)
        buttons.addWidget(self.clear_button)
        buttons.addWidget(self.save_button)
        layout.addLayout(buttons)
        layout.addStretch()
        return card

    def _load_empleados(self):
        try:
            self._empleados = self.controlador.listarEmpleados()
        except Exception as exc:
            self._empleados = []
            self.status_label.setText(str(exc))
            self._refresh_table()
            return
        self._refresh_table()

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
                self._build_row_button("Editar", lambda checked=False, emp=empleado: self._edit_employee(emp)),
            )
            self.table.setCellWidget(
                row,
                6,
                self._build_row_button("Eliminar", lambda checked=False, emp=empleado: self._delete_employee(emp)),
            )
            self.table.setRowHeight(row, 54)

        has_rows = bool(self._empleados)
        self.table.setVisible(has_rows)
        self.empty_label.setVisible(not has_rows)
        if not has_rows and not self.status_label.text():
            self.status_label.setText("Puedes crear el primer empleado desde el formulario.")

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

    def _edit_employee(self, empleado):
        self._editing_id = empleado.id_empleado
        self.ssn_input.setText(str(empleado.ssn))
        self.user_input.setText(empleado.usuario)
        self.correo_input.setText(empleado.correo)
        self.pass_input.setText(empleado.contrasena)
        self.tipo_input.setCurrentText(empleado.tipo)
        self.save_button.setText("Guardar cambios")
        self.status_label.setText(f"Editando empleado #{empleado.id_empleado}")

    def _clear_form(self):
        self._editing_id = None
        self.ssn_input.clear()
        self.user_input.clear()
        self.correo_input.clear()
        self.pass_input.clear()
        self.tipo_input.setCurrentIndex(0)
        self.save_button.setText("Guardar")
        self.status_label.setText("Formulario listo para un nuevo empleado.")

    def _collect_form_data(self):
        ssn = self.ssn_input.text().strip()
        usuario = self.user_input.text().strip()
        correo = self.correo_input.text().strip()
        contrasena = self.pass_input.text()
        tipo = self.tipo_input.currentText().strip()

        if len(ssn) != 11 or not ssn.isdigit():
            QMessageBox.warning(self, "Personal", "El SSN debe tener 11 digitos.")
            return None
        if not usuario:
            QMessageBox.warning(self, "Personal", "El usuario es obligatorio.")
            return None
        if not correo or "@" not in correo:
            QMessageBox.warning(self, "Personal", "El correo no es valido.")
            return None
        if not contrasena:
            QMessageBox.warning(self, "Personal", "La contrasena es obligatoria.")
            return None

        return ssn, usuario, correo, contrasena, tipo

    def _save_employee(self):
        data = self._collect_form_data()
        if data is None:
            return

        try:
            if self._editing_id is None:
                self.controlador.crearEmpleado(*data)
                self.status_label.setText("Empleado creado correctamente.")
            else:
                self.controlador.actualizarEmpleado(self._editing_id, *data)
                self.status_label.setText("Empleado actualizado correctamente.")
        except Exception as exc:
            QMessageBox.warning(self, "Personal", str(exc))
            return

        self._clear_form()
        self._load_empleados()

    def _delete_employee(self, empleado):
        reply = QMessageBox.question(
            self,
            "Eliminar empleado",
            f"Quieres eliminar a {empleado.usuario}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.controlador.eliminarEmpleado(empleado.id_empleado)
        except Exception as exc:
            QMessageBox.warning(self, "Personal", str(exc))
            return

        if self._editing_id == empleado.id_empleado:
            self._clear_form()
        self.status_label.setText("Empleado eliminado correctamente.")
        self._load_empleados()

    def _go_back(self, checked=False):
        self.volver_menu.emit()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controlador = ControladorEmpleados(Logica())
    sesion_demo = SesionVo(0, "Administrador", "admin@sushule.local", 0, None, "administrador")
    window = GestionPersonalUI(controlador=controlador, sesion=sesion_demo)
    window.show()
    sys.exit(app.exec_())
