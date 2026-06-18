"""
Vista de administracion de productos y promociones.
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

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from src.vista.ui.auth_common import C_ORANGE, C_ORANGE_DARK


class AdminProductosUI(QWidget):
    volver_menu = pyqtSignal()
    editar_producto_requested = pyqtSignal(object)
    guardar_producto_requested = pyqtSignal(str, float, str, str, int, str)
    eliminar_producto_requested = pyqtSignal(str)
    guardar_promocion_requested = pyqtSignal(dict)
    eliminar_promocion_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.productos = []
        self.promociones = []
        self.current_mode = "productos"
        self.product_name_options = []
        self._categorias = []
        self._mensaje_productos_vacios = "No hay productos para mostrar."
        self._mensaje_promociones_vacias = "No hay promociones para mostrar."
        self._producto_editando = None

        self._load_ui()
        self._wire_children()
        self._set_mode(self.current_mode)

    def _ui_path(self, filename):
        return os.path.join(os.path.dirname(__file__), "..", "ui_pyqt", filename)

    def _load_ui(self):
        self.setWindowTitle("sushUle - Administracion de Productos")
        self.resize(1380, 820)
        self.setMinimumSize(1180, 720)
        self.setStyleSheet("background-color: #147DB2;")

        root = QHBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(22)

        self.left_card = QFrame()
        self.right_card = QFrame()
        uic.loadUi(self._ui_path("AdminProductosListaUI.ui"), self.left_card)
        uic.loadUi(self._ui_path("AdminProductosProductoUI.ui"), self.right_card)

        self.promotion_card = QFrame()
        uic.loadUi(self._ui_path("AdminProductosPromocionesUI.ui"), self.promotion_card)

        self.products_mode_button = self.right_card.findChild(QPushButton, "products_mode_button")
        self.promotions_mode_button = self.right_card.findChild(QPushButton, "promotions_mode_button")
        self.products_panel = self.right_card.findChild(QWidget, "products_panel")

        right_container = QWidget()
        right_side = QVBoxLayout(right_container)
        right_side.setContentsMargins(0, 0, 0, 0)
        right_side.setSpacing(18)
        right_side.addWidget(self.right_card)
        right_side.addWidget(self.promotion_card)
        right_side.addStretch(1)

        root.addWidget(self.left_card, 7)
        root.addWidget(right_container, 5)

        self.table = self.findChild(QTableWidget, "table")
        self.empty_label = self.findChild(QLabel, "empty_label")
        self.form_status = self.right_card.findChild(QLabel, "form_status")
        self.promotion_status = self.promotion_card.findChild(QLabel, "promotion_status")

        self.name_input = self.right_card.findChild(QLineEdit, "name_input")
        self.price_input = self.right_card.findChild(QDoubleSpinBox, "price_input")
        self.ingredients_input = self.right_card.findChild(QTextEdit, "ingredients_input")
        self.available_input = self.right_card.findChild(QComboBox, "available_input")
        self.stock_input = self.right_card.findChild(QSpinBox, "stock_input")
        self.category_input = self.right_card.findChild(QComboBox, "category_input")
        self.category_hint = self.right_card.findChild(QLabel, "category_hint")

        self.clear_button = self.right_card.findChild(QPushButton, "clear_button")
        self.save_button = self.right_card.findChild(QPushButton, "save_button")

        self.discount_input = self.promotion_card.findChild(QSpinBox, "discount_input")
        self.start_date_input = self.promotion_card.findChild(QDateEdit, "start_date_input")
        self.end_date_input = self.promotion_card.findChild(QDateEdit, "end_date_input")
        self.promotion_product_input = self.promotion_card.findChild(QComboBox, "promotion_product_input")
        self.promotion_product_completer = self.promotion_card.findChild(QCompleter, "promotion_product_completer")
        self.clear_promo_button = self.promotion_card.findChild(QPushButton, "clear_promo_button")
        self.save_promo_button = self.promotion_card.findChild(QPushButton, "save_promo_button")
        self.empty_promotion_label = self.promotion_card.findChild(QLabel, "empty_promotion_label")
        self.promotion_table = self.promotion_card.findChild(QTableWidget, "promotion_table")

        if self.table is not None:
            self.table.verticalHeader().setVisible(False)
            self.table.setSelectionMode(QTableWidget.NoSelection)
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.table.setShowGrid(False)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)

        if self.promotion_table is not None:
            self.promotion_table.verticalHeader().setVisible(False)
            self.promotion_table.setSelectionMode(QTableWidget.NoSelection)
            self.promotion_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.promotion_table.setShowGrid(False)
            self.promotion_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.promotion_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        if self.start_date_input is not None:
            self.start_date_input.setCalendarPopup(True)
            self.start_date_input.setDate(QDate.currentDate())
        if self.end_date_input is not None:
            self.end_date_input.setCalendarPopup(True)
            self.end_date_input.setDate(QDate.currentDate().addDays(7))
        if self.discount_input is not None:
            self.discount_input.setRange(0, 100)
        if self.price_input is not None:
            self.price_input.setMaximum(9999.99)
            self.price_input.setDecimals(2)
            self.price_input.setPrefix("EUR ")
            self.price_input.setMinimum(0.01)
        if self.available_input is not None and self.available_input.count() == 0:
            self.available_input.addItems(["Y", "N"])

    def _wire_children(self):
        self.left_back_button = self.left_card.findChild(QPushButton, "left_back_button")
        if self.left_back_button is not None:
            self.left_back_button.clicked.connect(self._go_back)

        if self.products_mode_button is not None:
            self.products_mode_button.clicked.connect(lambda: self._set_mode("productos"))
        if self.promotions_mode_button is not None:
            self.promotions_mode_button.clicked.connect(lambda: self._set_mode("promociones"))

        if self.clear_button is not None:
            self.clear_button.clicked.connect(self.activar_modo_creacion)
        if self.save_button is not None:
            self.save_button.clicked.connect(self._emit_guardar_producto_requested)

        if self.clear_promo_button is not None:
            self.clear_promo_button.clicked.connect(self._clear_promotion_form)
        if self.save_promo_button is not None:
            self.save_promo_button.clicked.connect(self._emit_guardar_promocion_requested)

        if self.promotion_product_input is not None:
            self.promotion_product_input.setEditable(True)
            self.promotion_product_input.setInsertPolicy(QComboBox.NoInsert)
            self.promotion_product_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.promotion_product_completer = QCompleter([], self.promotion_product_input)
            self.promotion_product_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.promotion_product_completer.setFilterMode(Qt.MatchContains)
            self.promotion_product_completer.setCompletionMode(QCompleter.PopupCompletion)
            self.promotion_product_input.setCompleter(self.promotion_product_completer)

    def _go_back(self, checked=False):
        self.volver_menu.emit()

    def _set_mode(self, mode):
        self.current_mode = mode
        showing_products = mode == "productos"
        if self.products_panel is not None:
            self.products_panel.setVisible(showing_products)
        if self.promotion_card is not None:
            self.promotion_card.setVisible(not showing_products)
        self._apply_mode_button_style(self.products_mode_button, showing_products)
        self._apply_mode_button_style(self.promotions_mode_button, not showing_products)

    def _apply_mode_button_style(self, button, active):
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

    def configurar_schema(self, tiene_categoria, mensaje=""):
        self.category_input.setEnabled(bool(tiene_categoria))
        if mensaje:
            self.category_hint.setText(mensaje)
        elif tiene_categoria:
            self.category_hint.setText("Selecciona una categoria valida de la carta.")
        else:
            self.category_hint.setText("La BD actual no tiene columna de categorias en PRODUCTOS.")

    def inicializar_categorias(self, categorias):
        self._categorias = [str(categoria).strip() for categoria in (categorias or []) if str(categoria).strip()]
        current = self.category_input.currentText()
        self.category_input.blockSignals(True)
        self.category_input.clear()
        self.category_input.addItems(self._categorias)
        self.category_input.blockSignals(False)
        if current in self._categorias:
            self.category_input.setCurrentText(current)
        elif self._categorias:
            self.category_input.setCurrentIndex(0)

    def set_productos(self, productos, mensaje_vacio="No hay productos para mostrar.", mensaje_estado=""):
        self.productos = list(productos or [])
        self.product_name_options = [producto.nombre for producto in self.productos]
        self._mensaje_productos_vacios = mensaje_vacio
        self._refresh_promotion_product_selector()
        self._render_productos(mensaje_estado)

    def mostrar_error_productos(self, mensaje):
        self.productos = []
        self.product_name_options = []
        self._refresh_promotion_product_selector()
        self._render_productos(str(mensaje))

    def mostrar_error_formulario(self, mensaje):
        self.form_status.setText(f"ERROR {mensaje}")

    def set_promociones(self, promociones, mensaje_vacio="No hay promociones para mostrar.", mensaje_estado=""):
        self.promociones = list(promociones or [])
        self._mensaje_promociones_vacias = mensaje_vacio
        self._render_promociones(mensaje_estado)

    def mostrar_error_promociones(self, mensaje):
        self.promociones = []
        self._render_promociones(str(mensaje))

    def activar_modo_edicion(self, producto):
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

    def _render_productos(self, mensaje_estado=""):
        self.table.setRowCount(len(self.productos))
        for row, producto in enumerate(self.productos):
            self._set_item(self.table, row, 0, producto.nombre)
            self._set_item(self.table, row, 1, f"{producto.precio:.2f}")
            self._set_item(self.table, row, 2, producto.ingredientes)
            self._set_item(self.table, row, 3, producto.disponible)
            self._set_item(self.table, row, 4, str(producto.stock))
            self._set_item(self.table, row, 5, producto.categoria)
            self.table.setCellWidget(row, 6, self._build_row_button("Editar", lambda checked=False, p=producto: self.editar_producto_requested.emit(p)))
            self.table.setCellWidget(row, 7, self._build_row_button("Eliminar", lambda checked=False, p=producto: self._confirmar_eliminar_producto(p)))
            self.table.setRowHeight(row, 62)

        has_products = bool(self.productos)
        self.empty_label.setVisible(not has_products)
        self.table.setVisible(has_products)
        if mensaje_estado:
            self.form_status.setText(mensaje_estado)
        elif not has_products:
            self.form_status.setText(self._mensaje_productos_vacios)
        else:
            self.form_status.setText("")

    def _render_promociones(self, mensaje_estado=""):
        self.promotion_table.setRowCount(len(self.promociones))
        for row, promocion in enumerate(self.promociones):
            self._set_item(self.promotion_table, row, 0, promocion.get("id_promocion", ""))
            self._set_item(self.promotion_table, row, 1, promocion.get("nombre_producto", ""))
            self._set_item(self.promotion_table, row, 2, f"{promocion.get('descuento', 0)}%")
            self._set_item(self.promotion_table, row, 3, promocion.get("periodo_texto", ""))
            self.promotion_table.setCellWidget(
                row,
                4,
                self._build_row_button("Eliminar", lambda checked=False, p=promocion: self._confirmar_eliminar_promocion(p)),
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

    def _set_item(self, table, row, column, value):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row, column, item)

    def _build_row_button(self, text, slot):
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

    def _collect_product_data(self):
        return {
            "nombre": self.name_input.text(),
            "precio": float(self.price_input.value()),
            "ingredientes": self.ingredients_input.toPlainText(),
            "disponible": self.available_input.currentText(),
            "stock": int(self.stock_input.value()),
            "categoria": self.category_input.currentText().strip(),
        }

    def _emit_guardar_producto_requested(self):
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
        self.category_input.setCurrentText(str(categoria).strip())

    def _confirmar_eliminar_producto(self, producto):
        self.eliminar_producto_requested.emit(producto.nombre)

    def _emit_guardar_promocion_requested(self):
        self.guardar_promocion_requested.emit(
            {
                "descuento": int(self.discount_input.value()),
                "fecha_inicio": self.start_date_input.date().toPyDate(),
                "fecha_fin": self.end_date_input.date().toPyDate(),
                "nombre_producto": self.promotion_product_input.currentText().strip(),
            }
        )

    def _clear_promotion_form(self):
        self.discount_input.setValue(0)
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate().addDays(7))
        if self.promotion_product_input.count() > 0:
            self.promotion_product_input.setCurrentIndex(0)
        if self.promotion_product_input.lineEdit() is not None:
            self.promotion_product_input.lineEdit().clear()
        self.promotion_status.setText("Formulario de promocion listo.")

    def _confirmar_eliminar_promocion(self, promocion):
        promocion_id = int(promocion.get("id_promocion"))
        self.eliminar_promocion_requested.emit(promocion_id)

    def _refresh_promotion_product_selector(self):
        current_text = self.promotion_product_input.currentText().strip()
        self.promotion_product_input.blockSignals(True)
        self.promotion_product_input.clear()
        self.promotion_product_input.addItems(self.product_name_options)
        self.promotion_product_input.blockSignals(False)
        self.promotion_product_completer.setModel(self.promotion_product_input.model())
        if current_text and current_text in self.product_name_options:
            self.promotion_product_input.setCurrentText(current_text)
        elif self.promotion_product_input.count() > 0:
            self.promotion_product_input.setCurrentIndex(0)
