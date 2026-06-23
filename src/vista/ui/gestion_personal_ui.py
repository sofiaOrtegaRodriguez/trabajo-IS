"""
Vista de la gestión de empleados.

Pantalla que permite al gerente/admin ver, crear, editar y eliminar empleados.

Patrón MVC: pura VISTA. No contiene lógica de negocio.
Toda acción del usuario se comunica al controlador mediante señales (pyqtSignal).
El controlador llama a los métodos públicos de esta clase para actualizar los datos.
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

# Arreglo para ejecución directa o como módulo importado
if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

# Constantes de color compartidas con el resto de la app
from src.vista.ui.auth_common import C_BACKGROUND, C_CARD, C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_DIM, C_TEXT_MUTED


class GestionPersonalUI(QWidget):
    """
    Pantalla de gestión de empleados. Estructura visual:

    ┌─────────────────────────────────────────────────────────────┐
    │  [Volver]   Gestión de personal              [Cerrar sesión]│  ← topbar
    ├──────────────────────────────┬──────────────────────────────┤
    │  left_card (peso 7)          │  right_card (peso 5)         │
    │  ── GestionPersonalListaUI   │  ── GestionPersonalFormula.. │
    │                              │                              │
    │  Tabla de empleados          │  Formulario: SSN, usuario,   │
    │  (o mensaje de vacío)        │  correo, contraseña, tipo    │
    │                              │                              │
    │                              │  [Limpiar]  [Guardar]        │
    └──────────────────────────────┴──────────────────────────────┘

    A diferencia de AdminProductosUI y GerenteDashboardUI, la topbar
    (con "Volver" y "Cerrar sesión") se construye COMPLETAMENTE POR CÓDIGO
    en _load_ui(), sin archivo .ui. Solo left_card y right_card usan .ui.

    SEÑALES (vista → controlador):
    """

    # Se emite cuando el usuario pulsa "Volver"
    volver_menu = pyqtSignal()

    # Se emite cuando el usuario pulsa "Cerrar sesión"
    cerrar_sesion = pyqtSignal()

    # Se emite cuando el usuario pulsa "Editar" en una fila de la tabla.
    # Lleva el VO del empleado como argumento.
    editar_empleado_requested = pyqtSignal(object)

    # Se emite cuando el usuario pulsa "Guardar".
    # Lleva: VO empleado (None si es creación), ssn, usuario, correo, contraseña, tipo
    guardar_empleado_requested = pyqtSignal(object, str, str, str, str, str)

    # Se emite cuando el usuario pulsa "Eliminar" en una fila de la tabla.
    # Lleva el id_empleado (int) como argumento.
    eliminar_empleado_requested = pyqtSignal(int)

    # ─────────────────────────────────────────────────────────────
    # CONSTRUCTOR
    # ─────────────────────────────────────────────────────────────

    def __init__(self, sesion, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)  # libera memoria al cerrar

        self._sesion = sesion          # VO de sesión (no se usa actualmente en esta vista)
        self._empleados = []           # lista de VOs de empleado para la tabla
        self._tipos_empleado = []      # lista de tipos válidos para el combobox
        self._load_ui()        # 1. construye la interfaz
        self._wire_signals()   # 2. conecta botones a sus emisores de señal

    # ─────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────

    def _ui_path(self, filename):
        """Devuelve la ruta absoluta del archivo .ui dado su nombre."""
        return os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", filename)

    # ─────────────────────────────────────────────────────────────
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ─────────────────────────────────────────────────────────────

    def _load_ui(self):
        """
        Construye toda la estructura visual del widget.

        Layout principal (QVBoxLayout):
          ├── topbar (QFrame construido por código)
          │     ├── [Volver]
          │     ├── "Gestión de personal"
          │     ├── stretch
          │     └── [Cerrar sesión]
          └── content (QHBoxLayout)
                ├── left_card  ← GestionPersonalListaUI.ui   (peso 7)
                └── right_card ← GestionPersonalFormularioUI.ui (peso 5)
        """
        self.setWindowTitle("sushUle - Gestion de personal")
        self.setMinimumSize(1260, 760)
        self.setStyleSheet(f"background-color: {C_BACKGROUND};")

        # Layout raíz vertical: topbar arriba, contenido abajo
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        # ── Topbar (construida por código, sin .ui) ───────────────
        topbar = QFrame()
        topbar.setObjectName("card")  # necesario para que el selector CSS QFrame#card funcione
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

        # Botón "Volver" (crema, izquierda)
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

        # Título de la pantalla
        title = QLabel("Gestion de personal")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 800;")
        top_layout.addWidget(title)

        top_layout.addStretch()  # empuja el botón de logout hacia la derecha

        # Botón "Cerrar sesión" (naranja, derecha)
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

        # ── Contenido principal: tabla + formulario ───────────────
        content = QHBoxLayout()
        content.setSpacing(18)

        # Carga los .ui sobre QFrames vacíos
        self.left_card = QFrame()
        self.right_card = QFrame()
        uic.loadUi(self._ui_path("GestionPersonalListaUI.ui"), self.left_card)
        uic.loadUi(self._ui_path("GestionPersonalFormularioUI.ui"), self.right_card)

        content.addWidget(self.left_card, 7)   # tabla ocupa más espacio
        content.addWidget(self.right_card, 5)  # formulario ocupa menos espacio
        root.addLayout(content, 1)             # el contenido ocupa todo el espacio restante

        # ── Referencias a widgets del left_card (tabla) ──────────
        self.table = self.left_card.findChild(QTableWidget, "table")
        self.empty_label = self.left_card.findChild(QLabel, "empty_label")

        # ── Referencias a widgets del right_card (formulario) ────
        self.status_label = self.right_card.findChild(QLabel, "status_label")
        self.ssn_input = self.right_card.findChild(QLineEdit, "ssn_input")       # número seguridad social
        self.user_input = self.right_card.findChild(QLineEdit, "user_input")     # nombre de usuario
        self.correo_input = self.right_card.findChild(QLineEdit, "correo_input") # correo electrónico
        self.pass_input = self.right_card.findChild(QLineEdit, "pass_input")     # contraseña
        self.tipo_input = self.right_card.findChild(QComboBox, "tipo_input")     # tipo de empleado
        self.clear_button = self.right_card.findChild(QPushButton, "clear_button") # "Limpiar / nuevo"
        self.save_button = self.right_card.findChild(QPushButton, "save_button")   # "Guardar"

        # ── Configuración de la tabla ─────────────────────────────
        if self.table is not None:
            self.table.verticalHeader().setVisible(False)            # sin números de fila
            self.table.setSelectionMode(QTableWidget.NoSelection)    # no se puede seleccionar filas
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # no editable directamente
            self.table.setShowGrid(False)                            # sin líneas de cuadrícula
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # Columnas de acción (Editar, Eliminar) se ajustan al contenido
            self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)

        # El combobox de tipo no es editable: solo se puede elegir de la lista
        if self.tipo_input is not None:
            self.tipo_input.setEditable(False)

    # ─────────────────────────────────────────────────────────────
    # CONEXIÓN DE SEÑALES INTERNAS
    # ─────────────────────────────────────────────────────────────

    def _wire_signals(self):
        """
        Conecta los eventos click de los botones a los métodos internos
        que emiten las señales hacia el controlador.
        """
        self.back_button.clicked.connect(self._go_back)
        self.logout_button.clicked.connect(lambda checked=False: self.cerrar_sesion.emit())
        self.clear_button.clicked.connect(self.activar_modo_creacion)  # limpia el formulario
        self.save_button.clicked.connect(self._emit_guardar_requested)

    # ─────────────────────────────────────────────────────────────
    # API PÚBLICA: métodos que el CONTROLADOR llama para actualizar la vista
    # ─────────────────────────────────────────────────────────────

    def inicializar_tipos(self, tipos):
        """
        Rellena el combobox de tipo de empleado con la lista recibida.
        Convierte todos los valores a mayúsculas para consistencia.
        Preserva la selección actual si sigue siendo válida.

        Llamado por el controlador al inicializar la pantalla.
        """
        self._tipos_empleado = [str(t).strip().upper() for t in (tipos or []) if str(t).strip()]
        current = self.tipo_input.currentText()
        self.tipo_input.clear()
        self.tipo_input.addItems(self._tipos_empleado)
        if current in self._tipos_empleado:
            self.tipo_input.setCurrentText(current)  # mantiene selección previa
        elif self._tipos_empleado:
            self.tipo_input.setCurrentIndex(0)        # selecciona el primero si la previa no existe

    def set_empleados(self, empleados):
        """
        Actualiza la tabla con la lista de VOs de empleado recibida.
        Limpia el label de estado y redibuja la tabla.

        Llamado por el controlador cuando los datos cambian (carga inicial o tras ABM).
        """
        self._empleados = list(empleados or [])
        self.status_label.setText("")  # limpia cualquier mensaje anterior
        self._refresh_table()

    def mostrar_info(self, mensaje):
        """
        Muestra un mensaje informativo en el label de estado del formulario.
        (p.ej. "Empleado guardado correctamente.")
        """
        self.status_label.setText(str(mensaje))

    def mostrar_error(self, mensaje):
        """
        Muestra un error en el label de estado y vacía la tabla.
        Llamado por el controlador cuando hay un fallo de BD o validación.
        """
        self._empleados = []
        self.status_label.setText(str(mensaje))
        self._refresh_table()

    def activar_modo_edicion(self, empleado):
        """
        Rellena el formulario con los datos del VO recibido y cambia
        el texto del botón de guardar a "Guardar cambios".

        NOTA: el campo de contraseña se limpia siempre por seguridad;
        el controlador deberá manejar el caso de contraseña vacía
        (mantener la anterior o pedir que se introduzca una nueva).

        Llamado por el controlador al recibir editar_empleado_requested.
        """
        self.ssn_input.setText(str(getattr(empleado, "ssn", "")))
        self.user_input.setText(str(getattr(empleado, "usuario", "")))
        self.correo_input.setText(str(getattr(empleado, "correo", "")))
        self.pass_input.clear()  # nunca se muestra la contraseña actual
        tipo = str(getattr(empleado, "tipo", "")).upper()
        if tipo:
            self.tipo_input.setCurrentText(tipo)
        self.save_button.setText("Guardar cambios")
        self.status_label.setText(f"Editando empleado #{getattr(empleado, 'id_empleado', '')}")

    def activar_modo_creacion(self):
        """
        Limpia todos los campos del formulario y lo prepara para crear
        un empleado nuevo. Restablece el botón de guardar a "Guardar".

        Llamado internamente al pulsar "Limpiar" y por el controlador
        después de guardar un empleado con éxito.
        """
        self.ssn_input.clear()
        self.user_input.clear()
        self.correo_input.clear()
        self.pass_input.clear()
        if self._tipos_empleado:
            self.tipo_input.setCurrentIndex(0)
        self.save_button.setText("Guardar")
        self.status_label.setText("Formulario listo para un nuevo empleado.")

    # ─────────────────────────────────────────────────────────────
    # RENDERIZADO DE LA TABLA
    # ─────────────────────────────────────────────────────────────

    def _refresh_table(self):
        """
        Redibuja la tabla de empleados con los datos de self._empleados.

        Columnas: id | tipo | usuario | correo | ssn | [Editar] | [Eliminar]

        Si la lista está vacía: oculta la tabla y muestra empty_label.
        Si hay datos: muestra la tabla y oculta empty_label.

        TRUCO de closures: emp=empleado en los lambdas captura el valor
        del bucle en ese momento, evitando que todos los botones apunten
        al último empleado de la lista.
        """
        self.table.setRowCount(len(self._empleados))

        for row, empleado in enumerate(self._empleados):
            self._set_item(self.table, row, 0, empleado.id_empleado)
            self._set_item(self.table, row, 1, empleado.tipo)
            self._set_item(self.table, row, 2, empleado.usuario)
            self._set_item(self.table, row, 3, empleado.correo)
            self._set_item(self.table, row, 4, empleado.ssn)

            # Botón "Editar": emite editar_empleado_requested con el VO completo
            self.table.setCellWidget(
                row, 5,
                self._build_row_button(
                    "Editar",
                    lambda checked=False, emp=empleado: self.editar_empleado_requested.emit(emp),
                ),
            )

            # Botón "Eliminar": pasa por _confirmar_eliminar antes de emitir la señal
            self.table.setCellWidget(
                row, 6,
                self._build_row_button(
                    "Eliminar",
                    lambda checked=False, emp=empleado: self._confirmar_eliminar(emp),
                ),
            )

            self.table.setRowHeight(row, 54)  # altura fija por fila

        has_rows = bool(self._empleados)
        self.table.setVisible(has_rows)
        self.empty_label.setVisible(not has_rows)

    # ─────────────────────────────────────────────────────────────
    # HELPERS DE RENDERIZADO
    # ─────────────────────────────────────────────────────────────

    def _set_item(self, table, row, column, value):
        """
        Crea un QTableWidgetItem centrado y lo inserta en la celda indicada.
        Centraliza la creación para no repetir siempre los mismos pasos.
        """
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, column, item)

    def _build_row_button(self, text, slot):
        """
        Crea un QPushButton naranja para una celda de la tabla.

        Parámetros:
          text: texto del botón ("Editar" o "Eliminar")
          slot: función a ejecutar al hacer clic

        Devuelve el botón ya conectado y estilizado.
        """
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

    # ─────────────────────────────────────────────────────────────
    # RECOLECCIÓN DE DATOS Y EMISIÓN DE SEÑALES
    # ─────────────────────────────────────────────────────────────

    def _collect_form_data(self):
        """
        Lee los valores actuales del formulario y los devuelve como dict.
        No valida nada: esa responsabilidad es del controlador.
        """
        return {
            "ssn": self.ssn_input.text(),
            "usuario": self.user_input.text(),
            "correo": self.correo_input.text(),
            "contrasena": self.pass_input.text(),
            "tipo": self.tipo_input.currentText(),
        }

    def _emit_guardar_requested(self):
        """
        Lee el formulario y emite guardar_empleado_requested con los 6 argumentos.

        El primer argumento es siempre None desde la vista: el controlador sabe
        si es creación o edición porque conoce el contexto (qué empleado se estaba
        editando). Si en el examen piden pasar el ID, aquí habría que leer
        self._empleado_editando o similar.
        """
        datos = self._collect_form_data()
        self.guardar_empleado_requested.emit(
            None,               # VO del empleado (None = crear nuevo; el controlador lo gestiona)
            datos["ssn"],
            datos["usuario"],
            datos["correo"],
            datos["contrasena"],
            datos["tipo"],
        )

    def _confirmar_eliminar(self, empleado):
        """
        Emite eliminar_empleado_requested con el ID del empleado.
        Si en el examen piden añadir un QMessageBox de confirmación,
        este es el método donde añadirlo ANTES de emitir la señal.
        """
        self.eliminar_empleado_requested.emit(empleado.id_empleado)

    def _go_back(self, checked=False):
        """Emite volver_menu cuando el usuario pulsa "Volver"."""
        self.volver_menu.emit()