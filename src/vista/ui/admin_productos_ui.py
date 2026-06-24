"""
Vista de administración de productos y promociones.

Esta clase representa la pantalla completa de gestión del admin:
  - Panel izquierdo: tabla de productos (o promociones)
  - Panel derecho: formulario de edición/creación (o formulario de promoción)

Patrón MVC: esta clase es pura VISTA. No tiene lógica de negocio.
Toda acción del usuario se comunica al controlador mediante señales (pyqtSignal).
"""

import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QCompleter,
    QDateEdit,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Arreglo para que el módulo funcione tanto ejecutado directamente
# como importado desde otro paquete: añade la raíz del proyecto al sys.path
if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

# Colores naranja usados en botones de acción (editar, eliminar, guardar)
from src.vista.ui.auth_common import C_ORANGE, C_ORANGE_DARK


class AdminProductosUI(QWidget):
    """
    Widget principal de la pantalla de administración de productos y promociones.

    ┌─────────────────────────────────────────────────────────────────┐
    │  Panel izquierdo (left_card)   │  Panel derecho (right_card)    │
    │  ─────────────────────────     │  ──────────────────────────    │
    │  Tabla de productos            │  Botones modo: Productos /      │
    │  (o mensaje de vacío)          │  Promociones                   │
    │                                │                                │
    │  Botón "Volver al menú"        │  Formulario producto           │
    │                                │  (o formulario promoción)      │
    └─────────────────────────────────────────────────────────────────┘

    SEÑALES (comunicación vista → controlador):
    """

    # Se emite cuando el usuario pulsa "Volver al menú"
    volver_menu = pyqtSignal()

    # Se emite cuando el usuario pulsa "Editar" en una fila de la tabla.
    # Pasa el objeto producto (VO) como argumento.
    editar_producto_requested = pyqtSignal(object)

    # Se emite cuando el usuario pulsa "Añadir producto" o "Guardar cambios".
    # Pasa los 6 campos del formulario: nombre, precio, ingredientes,
    # disponible, stock, categoría.
    guardar_producto_requested = pyqtSignal(str, float, str, str, int, str)

    # Se emite cuando el usuario pulsa "Eliminar" en una fila de la tabla.
    # Pasa el nombre del producto como argumento.
    eliminar_producto_requested = pyqtSignal(str)

    # Se emite cuando el usuario pulsa "Guardar promoción".
    # Pasa un dict con: descuento, fecha_inicio, fecha_fin, nombre_producto.
    guardar_promocion_requested = pyqtSignal(dict)

    # Se emite cuando el usuario pulsa "Eliminar" en una fila de promociones.
    # Pasa el id_promocion (int) como argumento.
    eliminar_promocion_requested = pyqtSignal(int)

    # ─────────────────────────────────────────────────────────────────
    # CONSTRUCTOR
    # ─────────────────────────────────────────────────────────────────

    def __init__(self, parent=None):
        super().__init__(parent)

        # WA_DeleteOnClose: libera la memoria del widget cuando se cierra
        # (importante para evitar fugas en PyQt5)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Estado interno de la vista (NO lógica de negocio)
        self.productos = []              # lista de VOs de producto para renderizar la tabla
        self.promociones = []            # lista de dicts de promoción para renderizar la tabla
        self.current_mode = "productos"  # modo activo: "productos" o "promociones"
        self.product_name_options = []   # nombres de productos para el autocomplete del form de promoción
        self._categorias = []            # categorías disponibles para el combobox del form de producto
        self._mensaje_productos_vacios = "No hay productos para mostrar."
        self._mensaje_promociones_vacias = "No hay promociones para mostrar."
        self._producto_editando = None   # nombre del producto en edición (None = modo creación)

        # Secuencia de inicialización:
        self._load_ui()        # 1. construye la interfaz (carga .ui, crea layouts, obtiene refs a widgets)
        self._wire_children()  # 2. conecta señales de botones a métodos internos
        self._set_mode(self.current_mode)  # 3. muestra el panel inicial (productos)

    # ─────────────────────────────────────────────────────────────────
    # HELPERS DE RUTAS
    # ─────────────────────────────────────────────────────────────────

    def _ui_path(self, filename):
        """
        Devuelve la ruta absoluta de un archivo .ui dentro de la carpeta
        ui_pyqt/ (hermana de la carpeta actual).
        Uso: self._ui_path("AdminProductosListaUI.ui")
        """
        return os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", filename)

    # ─────────────────────────────────────────────────────────────────
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ─────────────────────────────────────────────────────────────────

    def _load_ui(self):
        """
        Construye toda la estructura visual del widget.

        Estructura de layouts:
          QHBoxLayout (root)
          ├── left_card  (QFrame, peso 7) ← cargado desde AdminProductosListaUI.ui
          └── right_container (QWidget, peso 5)
               └── QVBoxLayout
                    ├── right_card       ← cargado desde AdminProductosProductoUI.ui
                    ├── promotion_card   ← cargado desde AdminProductosPromocionesUI.ui
                    └── stretch

        Después de cargar los .ui, se obtienen referencias a todos los
        widgets hijos con findChild() para poder usarlos desde otros métodos.
        """

        self.setWindowTitle("sushUle - Administracion de Productos")
        self.resize(1380, 820)
        self.setMinimumSize(1180, 720)
        self.setStyleSheet("background-color: #147DB2;")

        # Layout raíz horizontal: tabla a la izquierda, formularios a la derecha
        root = QHBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(22)

        # ── Panel izquierdo: tabla de productos/promociones ──────────
        self.left_card = QFrame()
        uic.loadUi(self._ui_path("AdminProductosListaUI.ui"), self.left_card)

        # ── Panel derecho superior: formulario de producto ───────────
        self.right_card = QFrame()
        uic.loadUi(self._ui_path("AdminProductosProductoUI.ui"), self.right_card)

        # ── Panel derecho inferior: formulario de promoción ──────────
        self.promotion_card = QFrame()
        uic.loadUi(self._ui_path("AdminProductosPromocionesUI.ui"), self.promotion_card)

        # Referencias a los botones de cambio de modo (Productos / Promociones)
        # y al contenedor del formulario de producto (se oculta en modo promociones)
        self.products_mode_button = self.right_card.findChild(QPushButton, "products_mode_button")
        self.promotions_mode_button = self.right_card.findChild(QPushButton, "promotions_mode_button")
        self.products_panel = self.right_card.findChild(QWidget, "products_panel")

        # El right_container apila el right_card y el promotion_card verticalmente
        right_container = QWidget()
        right_side = QVBoxLayout(right_container)
        right_side.setContentsMargins(0, 0, 0, 0)
        right_side.setSpacing(18)
        right_side.addWidget(self.right_card)
        right_side.addWidget(self.promotion_card)
        right_side.addStretch(1)  # empuja el contenido hacia arriba

        # Añade los dos bloques al layout raíz con proporciones 7:5
        root.addWidget(self.left_card, 7)
        root.addWidget(right_container, 5)

        # ── Referencias a widgets concretos (para uso posterior) ─────

        # Tabla principal de productos y etiqueta de "vacío"
        self.table = self.findChild(QTableWidget, "table")
        self.empty_label = self.findChild(QLabel, "empty_label")

        # Etiquetas de estado/mensajes del formulario de producto y de promoción
        self.form_status = self.right_card.findChild(QLabel, "form_status")
        self.promotion_status = self.promotion_card.findChild(QLabel, "promotion_status")

        # Campos del formulario de producto
        self.name_input = self.right_card.findChild(QLineEdit, "name_input")
        self.price_input = self.right_card.findChild(QDoubleSpinBox, "price_input")
        self.ingredients_input = self.right_card.findChild(QTextEdit, "ingredients_input")
        self.available_input = self.right_card.findChild(QComboBox, "available_input")
        self.stock_input = self.right_card.findChild(QSpinBox, "stock_input")
        self.category_input = self.right_card.findChild(QComboBox, "category_input")
        self.category_hint = self.right_card.findChild(QLabel, "category_hint")

        # Botones del formulario de producto
        self.clear_button = self.right_card.findChild(QPushButton, "clear_button")   # "Limpiar / nuevo"
        self.save_button = self.right_card.findChild(QPushButton, "save_button")     # "Guardar"

        # Campos del formulario de promoción
        self.discount_input = self.promotion_card.findChild(QSpinBox, "discount_input")
        self.start_date_input = self.promotion_card.findChild(QDateEdit, "start_date_input")
        self.end_date_input = self.promotion_card.findChild(QDateEdit, "end_date_input")
        self.promotion_product_input = self.promotion_card.findChild(QComboBox, "promotion_product_input")
        self.promotion_product_completer = self.promotion_card.findChild(QCompleter, "promotion_product_completer")
        self.clear_promo_button = self.promotion_card.findChild(QPushButton, "clear_promo_button")
        self.save_promo_button = self.promotion_card.findChild(QPushButton, "save_promo_button")
        self.empty_promotion_label = self.promotion_card.findChild(QLabel, "empty_promotion_label")
        self.promotion_table = self.promotion_card.findChild(QTableWidget, "promotion_table")

        # ── Configuración de la tabla de productos ───────────────────
        if self.table is not None:
            self.table.verticalHeader().setVisible(False)           # sin números de fila
            self.table.setSelectionMode(QTableWidget.NoSelection)   # no se puede seleccionar filas
            self.table.setEditTriggers(QTableWidget.NoEditTriggers) # no editable directamente
            self.table.setShowGrid(False)                           # sin líneas de cuadrícula
            # La mayoría de columnas se estiran para ocupar el espacio disponible
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # Las columnas de acción (ingredientes, Editar, Eliminar) ajustan su tamaño al contenido
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)

        # ── Configuración de la tabla de promociones ─────────────────
        if self.promotion_table is not None:
            self.promotion_table.verticalHeader().setVisible(False)
            self.promotion_table.setSelectionMode(QTableWidget.NoSelection)
            self.promotion_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.promotion_table.setShowGrid(False)
            self.promotion_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # Columna de acción "Eliminar" ajusta tamaño al contenido
            self.promotion_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # ── Configuración de campos con valores por defecto ──────────

        if self.start_date_input is not None:
            self.start_date_input.setCalendarPopup(True)           # muestra calendario al hacer clic
            self.start_date_input.setDate(QDate.currentDate())     # fecha por defecto: hoy

        if self.end_date_input is not None:
            self.end_date_input.setCalendarPopup(True)
            self.end_date_input.setDate(QDate.currentDate().addDays(7))  # por defecto: hoy + 7 días

        if self.discount_input is not None:
            self.discount_input.setRange(0, 100)                   # descuento entre 0% y 100%

        if self.price_input is not None:
            self.price_input.setMaximum(9999.99)
            self.price_input.setDecimals(2)
            self.price_input.setPrefix("EUR ")                     # muestra "EUR " delante del número
            self.price_input.setMinimum(0.01)                      # precio mínimo: 0.01 €

        if self.available_input is not None and self.available_input.count() == 0:
            # Solo añade las opciones si el combobox está vacío
            # (evita duplicados si se llama a _load_ui varias veces)
            self.available_input.addItems(["Y", "N"])

    # ─────────────────────────────────────────────────────────────────
    # CONEXIÓN DE SEÑALES INTERNAS
    # ─────────────────────────────────────────────────────────────────

    def _wire_children(self):
        """
        Conecta los eventos click de los botones a los métodos internos
        de la vista.

        IMPORTANTE: estos métodos internos solo leen el estado del widget
        y emiten señales. Nunca contienen lógica de negocio.
        """

        # Botón "Volver al menú" (está en left_card, no en el widget raíz)
        self.left_back_button = self.left_card.findChild(QPushButton, "left_back_button")
        if self.left_back_button is not None:
            self.left_back_button.clicked.connect(self._go_back)

        # Botones de cambio de modo: muestran/ocultan paneles
        if self.products_mode_button is not None:
            self.products_mode_button.clicked.connect(lambda: self._set_mode("productos"))
        if self.promotions_mode_button is not None:
            self.promotions_mode_button.clicked.connect(lambda: self._set_mode("promociones"))

        # Formulario de producto
        if self.clear_button is not None:
            self.clear_button.clicked.connect(self.activar_modo_creacion)  # limpia el formulario
        if self.save_button is not None:
            self.save_button.clicked.connect(self._emit_guardar_producto_requested)

        # Formulario de promoción
        if self.clear_promo_button is not None:
            self.clear_promo_button.clicked.connect(self._clear_promotion_form)
        if self.save_promo_button is not None:
            self.save_promo_button.clicked.connect(self._emit_guardar_promocion_requested)

        # Combobox de selección de producto en el formulario de promoción:
        # se hace editable y se añade un QCompleter para autocompletar
        if self.promotion_product_input is not None:
            self.promotion_product_input.setEditable(True)
            self.promotion_product_input.setInsertPolicy(QComboBox.NoInsert)  # no añade texto nuevo a la lista
            self.promotion_product_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            # Completer: busca coincidencias ignorando mayúsculas,
            # filtra por "contiene" (no solo "empieza por")
            self.promotion_product_completer = QCompleter([], self.promotion_product_input)
            self.promotion_product_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.promotion_product_completer.setFilterMode(Qt.MatchContains)
            self.promotion_product_completer.setCompletionMode(QCompleter.PopupCompletion)
            self.promotion_product_input.setCompleter(self.promotion_product_completer)

    # ─────────────────────────────────────────────────────────────────
    # MÉTODOS INTERNOS: navegación y modos
    # ─────────────────────────────────────────────────────────────────

    def _go_back(self, checked=False):
        """Emite la señal volver_menu cuando el usuario pulsa "Volver"."""
        self.volver_menu.emit()

    def _set_mode(self, mode):
        """
        Cambia entre el modo "productos" y el modo "promociones".

        En modo "productos":
          - products_panel (formulario de producto) → visible
          - promotion_card (formulario de promoción) → oculto

        En modo "promociones":
          - products_panel → oculto
          - promotion_card → visible

        También actualiza el estilo visual de los botones de modo
        para indicar cuál está activo.
        """
        self.current_mode = mode
        showing_products = mode == "productos"

        if self.products_panel is not None:
            self.products_panel.setVisible(showing_products)
        if self.promotion_card is not None:
            self.promotion_card.setVisible(not showing_products)

        # Aplica estilo "activo" al botón del modo actual, "inactivo" al otro
        self._apply_mode_button_style(self.products_mode_button, showing_products)
        self._apply_mode_button_style(self.promotions_mode_button, not showing_products)

    def _apply_mode_button_style(self, button, active):
        """
        Aplica el estilo CSS al botón según si está activo o inactivo.

        Activo:   fondo naranja, texto blanco
        Inactivo: fondo crema claro, texto oscuro
        """
        if button is None:
            return
        background = C_ORANGE if active else "#FEF5ED"
        foreground = "white" if active else "#163246"
        hover = C_ORANGE_DARK if active else "#F3E6D8"
        border = C_ORANGE if active else "#D8C8BA"
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {background};
                color: {foreground};
                border: 1px solid {border};
                border-radius: 23px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            """
        )

    # ─────────────────────────────────────────────────────────────────
    # API PÚBLICA: métodos que el CONTROLADOR llama para actualizar la vista
    # ─────────────────────────────────────────────────────────────────

    def configurar_schema(self, tiene_categoria, mensaje=""):
        """
        Habilita o deshabilita el combobox de categoría según si la BD
        tiene columna de categoría en la tabla PRODUCTOS.

        Llamado por el controlador al inicializar la pantalla.
        """
        self.category_input.setEnabled(bool(tiene_categoria))
        if mensaje:
            self.category_hint.setText(mensaje)
        elif tiene_categoria:
            self.category_hint.setText("Selecciona una categoria valida de la carta.")
        else:
            self.category_hint.setText("La BD actual no tiene columna de categorias en PRODUCTOS.")

    def inicializar_categorias(self, categorias):
        """
        Rellena el combobox de categorías con la lista recibida del controlador.
        Preserva la selección actual si la categoría sigue existiendo.

        Bloquea señales durante la actualización para evitar disparar
        eventos intermedios innecesarios.
        """
        self._categorias = [str(c).strip() for c in (categorias or []) if str(c).strip()]
        current = self.category_input.currentText()

        self.category_input.blockSignals(True)
        self.category_input.clear()
        self.category_input.addItems(self._categorias)
        self.category_input.blockSignals(False)

        if current in self._categorias:
            self.category_input.setCurrentText(current)  # mantiene selección previa
        elif self._categorias:
            self.category_input.setCurrentIndex(0)        # selecciona la primera si la previa no existe

    def set_productos(self, productos, mensaje_vacio="No hay productos para mostrar.", mensaje_estado=""):
        """
        Actualiza la tabla de productos con la lista de VOs recibida.
        También actualiza la lista de nombres para el autocomplete del form de promoción.
        Llamado por el controlador cuando los datos cambian (carga inicial, ABM, etc.)
        """
        self.productos = list(productos or [])
        self.product_name_options = [p.nombre for p in self.productos]
        self._mensaje_productos_vacios = mensaje_vacio
        self._refresh_promotion_product_selector()  # sincroniza el combobox de promociones
        self._render_productos(mensaje_estado)

    def mostrar_error_productos(self, mensaje):
        """
        Muestra un error en la tabla de productos (p.ej. fallo de BD).
        Limpia la tabla y el selector de productos del form de promoción.
        """
        self.productos = []
        self.product_name_options = []
        self._refresh_promotion_product_selector()
        self._render_productos(str(mensaje))

    def mostrar_error_formulario(self, mensaje):
        """
        Muestra un mensaje de error en el label de estado del formulario de producto.
        Llamado por el controlador cuando hay un error de validación o de BD.
        """
        self.form_status.setText(f"ERROR {mensaje}")

    def set_promociones(self, promociones, mensaje_vacio="No hay promociones para mostrar.", mensaje_estado=""):
        """
        Actualiza la tabla de promociones con la lista de dicts recibida.
        Llamado por el controlador cuando los datos de promociones cambian.
        """
        self.promociones = list(promociones or [])
        self._mensaje_promociones_vacias = mensaje_vacio
        self._render_promociones(mensaje_estado)

    def mostrar_error_promociones(self, mensaje):
        """
        Muestra un error en la tabla de promociones.
        """
        self.promociones = []
        self._render_promociones(str(mensaje))

    def activar_modo_edicion(self, producto):
        """
        Rellena el formulario de producto con los datos del VO recibido
        y cambia el texto del botón de guardar a "Guardar cambios".

        Llamado por el controlador cuando el usuario pulsa "Editar" en una fila.
        El controlador recibe la señal editar_producto_requested, busca el VO
        completo si hace falta, y llama a este método.
        """
        self._producto_editando = getattr(producto, "nombre", None)
        self.name_input.setText(getattr(producto, "nombre", ""))
        self.price_input.setValue(float(getattr(producto, "precio", 0) or 0))
        self.ingredients_input.setPlainText(getattr(producto, "ingredientes", ""))
        self.available_input.setCurrentText(str(getattr(producto, "disponible", "Y")).strip() or "Y")
        self.stock_input.setValue(int(getattr(producto, "stock", 0) or 0))
        self._set_category_value(getattr(producto, "categoria", ""))
        self.save_button.setText("Guardar cambios")
        self.form_status.setText(f"Editando: {getattr(producto, 'nombre', '')}")

    def activar_modo_creacion(self):
        """
        Limpia el formulario de producto y lo prepara para crear uno nuevo.
        Restablece todos los campos a sus valores por defecto.

        Llamado internamente al pulsar "Limpiar" y por el controlador
        después de guardar un producto con éxito.
        """
        self._producto_editando = None
        self.name_input.clear()
        self.price_input.setValue(0.01)
        self.ingredients_input.clear()
        self.available_input.setCurrentText("Y")
        self.stock_input.setValue(0)
        if self._categorias:
            self.category_input.setCurrentIndex(0)
        self.save_button.setText("Anadir producto")
        self.form_status.setText("Formulario listo para crear un producto nuevo.")

    # ─────────────────────────────────────────────────────────────────
    # RENDERIZADO DE TABLAS
    # ─────────────────────────────────────────────────────────────────

    def _render_productos(self, mensaje_estado=""):
        """
        Dibuja la tabla de productos con los datos de self.productos.

        Columnas: nombre | precio | ingredientes | disponible | stock | categoría | [Editar] | [Eliminar]

        Si la lista está vacía, muestra el empty_label y oculta la tabla.
        Si hay productos, muestra la tabla y oculta el empty_label.
        """
        self.table.setRowCount(len(self.productos))

        for row, producto in enumerate(self.productos):
            self._set_item(self.table, row, 0, producto.nombre)
            self._set_item(self.table, row, 1, f"{producto.precio:.2f}")
            self._set_item(self.table, row, 2, producto.ingredientes)
            self._set_item(self.table, row, 3, producto.disponible)
            self._set_item(self.table, row, 4, str(producto.stock))
            self._set_item(self.table, row, 5, producto.categoria)

            # Botón "Editar": emite editar_producto_requested con el VO del producto
            # TRUCO: p=producto en el lambda captura el valor actual del bucle,
            # evitando el problema clásico de closures en Python.
            self.table.setCellWidget(
                row, 6,
                self._build_row_button(
                    "Editar",
                    lambda checked=False, p=producto: self.editar_producto_requested.emit(p)
                )
            )

            # Botón "Eliminar": pasa por _confirmar_eliminar_producto primero
            self.table.setCellWidget(
                row, 7,
                self._build_row_button(
                    "Eliminar",
                    lambda checked=False, p=producto: self._confirmar_eliminar_producto(p)
                )
            )

            self.table.setRowHeight(row, 62)  # altura fija por fila

        has_products = bool(self.productos)
        self.empty_label.setVisible(not has_products)  # muestra aviso si no hay datos
        self.table.setVisible(has_products)

        # Actualiza el label de estado según el contexto
        if mensaje_estado:
            self.form_status.setText(mensaje_estado)
        elif not has_products:
            self.form_status.setText(self._mensaje_productos_vacios)
        else:
            self.form_status.setText("")

    def _render_promociones(self, mensaje_estado=""):
        """
        Dibuja la tabla de promociones con los datos de self.promociones.

        Columnas: id | nombre producto | descuento | periodo | [Eliminar]

        Misma lógica de visibilidad que _render_productos.
        """
        self.promotion_table.setRowCount(len(self.promociones))

        for row, promocion in enumerate(self.promociones):
            self._set_item(self.promotion_table, row, 0, promocion.get("id_promocion", ""))
            self._set_item(self.promotion_table, row, 1, promocion.get("nombre_producto", ""))
            self._set_item(self.promotion_table, row, 2, f"{promocion.get('descuento', 0)}%")
            self._set_item(self.promotion_table, row, 3, promocion.get("periodo_texto", ""))

            self.promotion_table.setCellWidget(
                row, 4,
                self._build_row_button(
                    "Eliminar",
                    lambda checked=False, p=promocion: self._confirmar_eliminar_promocion(p)
                )
            )
            self.promotion_table.setRowHeight(row, 54)

        has_promotions = bool(self.promociones)
        self.empty_promotion_label.setVisible(not has_promotions)
        self.promotion_table.setVisible(has_promotions)

        if mensaje_estado:
            self.promotion_status.setText(mensaje_estado)
        elif not has_promotions:
            self.promotion_status.setText(self._mensaje_promociones_vacias)
        else:
            self.promotion_status.setText("")

    # ─────────────────────────────────────────────────────────────────
    # HELPERS DE RENDERIZADO
    # ─────────────────────────────────────────────────────────────────

    def _set_item(self, table, row, column, value):
        """
        Crea un QTableWidgetItem centrado y lo inserta en la celda indicada.
        Centraliza la creación para no repetir siempre los mismos 3 pasos.
        """
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, column, item)

    def _build_row_button(self, text, slot):
        """
        Crea un QPushButton de acción (naranja) para una celda de la tabla.

        Parámetros:
          text: texto del botón ("Editar" o "Eliminar")
          slot: función a ejecutar al hacer clic

        Devuelve el botón ya conectado y estilizado.
        """
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setStyleSheet(
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
        button.clicked.connect(slot)
        return button

    # ─────────────────────────────────────────────────────────────────
    # RECOLECCIÓN DE DATOS DEL FORMULARIO
    # ─────────────────────────────────────────────────────────────────

    def _collect_product_data(self):
        """
        Lee los valores actuales del formulario de producto y los devuelve
        como diccionario.

        No valida nada: esa responsabilidad es del controlador.
        """
        return {
            "nombre": self.name_input.text(),
            "precio": float(self.price_input.value()),
            "ingredientes": self.ingredients_input.toPlainText(),
            "disponible": self.available_input.currentText(),
            "stock": int(self.stock_input.value()),
            "categoria": self.category_input.currentText().strip(),
        }

    # ─────────────────────────────────────────────────────────────────
    # EMISIÓN DE SEÑALES (vista → controlador)
    # ─────────────────────────────────────────────────────────────────

    def _emit_guardar_producto_requested(self):
        """
        Lee el formulario y emite guardar_producto_requested con los 6 campos.
        El controlador decide si es una creación (self._producto_editando is None)
        o una edición.
        """
        datos = self._collect_product_data()
        self.guardar_producto_requested.emit(
            datos["nombre"],
            datos["precio"],
            datos["ingredientes"],
            datos["disponible"],
            datos["stock"],
            datos["categoria"],
        )


    def _set_category_value(self, categoria):
        """Selecciona la categoría indicada en el combobox (usado en modo edición)."""
        self.category_input.setCurrentText(str(categoria).strip())

    def _confirmar_eliminar_producto(self, producto):
        """
        Emite eliminar_producto_requested con el nombre del producto.
        Si en el examen piden confirmación (QMessageBox), este sería el lugar
        para añadirla ANTES de emitir la señal.
        """
        self.eliminar_producto_requested.emit(producto.nombre)

    def _emit_guardar_promocion_requested(self):
        """
        Lee el formulario de promoción y emite guardar_promocion_requested
        con un dict que contiene:
          - descuento: int (0-100)
          - fecha_inicio: datetime.date
          - fecha_fin: datetime.date
          - nombre_producto: str (texto actual del combobox editable)
        """
        self.guardar_promocion_requested.emit(
            {
                "descuento": int(self.discount_input.value()),
                "fecha_inicio": self.start_date_input.date().toPyDate(),   # QDate → datetime.date
                "fecha_fin": self.end_date_input.date().toPyDate(),
                "nombre_producto": self.promotion_product_input.currentText().strip(),
            }
        )

    def _clear_promotion_form(self):
        """
        Restablece el formulario de promoción a sus valores por defecto:
          - descuento → 0
          - fecha inicio → hoy
          - fecha fin → hoy + 7 días
          - producto → primero de la lista (si existe)

        También limpia el texto libre del combobox editable.
        """
        self.discount_input.setValue(0)
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate().addDays(7))
        if self.promotion_product_input.count() > 0:
            self.promotion_product_input.setCurrentIndex(0)
        if self.promotion_product_input.lineEdit() is not None:
            self.promotion_product_input.lineEdit().clear()
        self.promotion_status.setText("Formulario de promocion listo.")

    def _confirmar_eliminar_promocion(self, promocion):
        """
        Obtiene el ID de la promoción del dict y emite eliminar_promocion_requested.
        """
        promocion_id = int(promocion.get("id_promocion"))
        self.eliminar_promocion_requested.emit(promocion_id)

    # ─────────────────────────────────────────────────────────────────
    # SINCRONIZACIÓN DEL COMBOBOX DE PRODUCTOS EN EL FORM DE PROMOCIÓN
    # ─────────────────────────────────────────────────────────────────

    def _refresh_promotion_product_selector(self):
        """
        Actualiza el combobox de selección de producto en el formulario
        de promoción con la lista actual de product_name_options.

        Lógica de preservación de selección:
          - Si el texto actual sigue siendo válido → lo mantiene
          - Si no → selecciona el primer producto disponible

        Bloquea señales durante la actualización para evitar efectos secundarios.
        También actualiza el modelo del completer para que el autocompletar
        funcione con los nuevos nombres.
        """
        current_text = self.promotion_product_input.currentText().strip()

        self.promotion_product_input.blockSignals(True)
        self.promotion_product_input.clear()
        self.promotion_product_input.addItems(self.product_name_options)
        self.promotion_product_input.blockSignals(False)

        # El completer debe usar el mismo modelo que el combobox
        self.promotion_product_completer.setModel(self.promotion_product_input.model())

        if current_text and current_text in self.product_name_options:
            self.promotion_product_input.setCurrentText(current_text)
        elif self.promotion_product_input.count() > 0:
            self.promotion_product_input.setCurrentIndex(0)