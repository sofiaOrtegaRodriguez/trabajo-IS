import os
import sys

from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QCompleter,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
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

from src.controlador.ControladorProductos import ControladorProductos
from src.modelo.Logica import Logica
from src.vista.ui.auth_common import C_CARD, C_CREAM, C_ORANGE, C_ORANGE_DARK, C_TEXT_DIM, C_TEXT_MUTED

ADMIN_CATEGORIES = ["Sushi", "Fritos", "Postres", "Bebidas"]


class AdminProductosUI(QWidget):
    volver_menu = pyqtSignal()

    def __init__(self, controlador=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.controlador = controlador
        self.schema_info = {"category_column": None}
        self.editing_name = None
        self.productos = []
        self.promociones = []
        self.current_mode = "productos"
        self.product_name_options = []
        self._build()
        self._load_schema()
        self._load_products()
        self._load_promotions()

    def _build(self):
        self.setWindowTitle("sushUle - Administracion de Productos")
        self.resize(1380, 820)
        self.setMinimumSize(1180, 720)
        self.setStyleSheet("background-color: #147DB2;")

        root = QHBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(22)

        left_card = QFrame()
        left_card.setObjectName("card")
        left_card.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CARD};
                border-radius: 34px;
            }}
            """
        )
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(24, 24, 24, 24)
        left_layout.setSpacing(18)

        back_row = QHBoxLayout()
        back_button = self._build_action_button("Volver", secondary=True)
        back_button.setMaximumWidth(130)
        back_button.clicked.connect(self._go_back)
        back_row.addWidget(back_button)
        back_row.addStretch()
        left_layout.addLayout(back_row)

        title = QLabel("Gestion de productos")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: 700;")
        subtitle = QLabel("Consulta, edita y elimina los productos actuales de la carta.")
        subtitle.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px;")
        subtitle.setWordWrap(True)

        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)

        self.empty_label = QLabel("TODAVIA NO HAY PRODUCTOS")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: white; font-size: 22px; font-weight: 700;")

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["Nombre", "Precio", "Ingredientes", "Disponible", "Stock", "Categoria", "Editar", "Eliminar"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setWordWrap(True)
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {C_CREAM};
                border: none;
                border-radius: 24px;
                color: #163246;
                font-size: 13px;
                gridline-color: transparent;
            }}
            QHeaderView::section {{
                background-color: {C_ORANGE};
                color: white;
                border: none;
                padding: 10px;
                font-size: 13px;
                font-weight: 700;
            }}
            """
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)

        left_layout.addWidget(self.empty_label, 1)
        left_layout.addWidget(self.table, 1)
        root.addWidget(left_card, 7)

        right_side = QVBoxLayout()
        right_side.setSpacing(18)

        switch_card = QFrame()
        switch_card.setObjectName("card")
        switch_card.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CREAM};
                border-radius: 28px;
            }}
            """
        )
        switch_layout = QHBoxLayout(switch_card)
        switch_layout.setContentsMargins(16, 16, 16, 16)
        switch_layout.setSpacing(12)

        self.products_mode_button = self._build_mode_button("Productos")
        self.promotions_mode_button = self._build_mode_button("Promociones")
        self.products_mode_button.clicked.connect(lambda: self._set_mode("productos"))
        self.promotions_mode_button.clicked.connect(lambda: self._set_mode("promociones"))

        switch_layout.addWidget(self.products_mode_button)
        switch_layout.addWidget(self.promotions_mode_button)

        self.product_form_card = self._build_product_form_card()
        self.promotion_card = self._build_promotion_card()

        right_side.addWidget(switch_card)
        right_side.addWidget(self.product_form_card, 1)
        right_side.addWidget(self.promotion_card, 1)

        right_container = QWidget()
        right_container.setLayout(right_side)
        root.addWidget(right_container, 5)
        self._set_mode(self.current_mode)

    def _build_product_form_card(self):
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CREAM};
                border-radius: 34px;
            }}
            QLabel {{
                color: #163246;
            }}
            QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox, QSpinBox {{
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
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        form_title = QLabel("Nuevo / editar producto")
        form_title.setStyleSheet("color: #163246; font-size: 22px; font-weight: 700;")
        layout.addWidget(form_title)

        self.form_status = QLabel("")
        self.form_status.setWordWrap(True)
        self.form_status.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(self.form_status)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(12)

        self.name_input = QLineEdit()
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(9999.99)
        self.price_input.setDecimals(2)
        self.price_input.setPrefix("EUR ")
        self.price_input.setMinimum(0.01)

        self.ingredients_input = QTextEdit()
        self.ingredients_input.setMinimumHeight(110)

        self.available_input = QComboBox()
        self.available_input.addItems(["Y", "N"])

        self.stock_input = QSpinBox()
        self.stock_input.setMinimum(0)
        self.stock_input.setMaximum(99999)

        self.category_input = QComboBox()
        self.category_input.addItems(ADMIN_CATEGORIES)
        self.category_hint = QLabel("")
        self.category_hint.setWordWrap(True)
        self.category_hint.setStyleSheet(f"color: {C_TEXT_DIM}; font-size: 11px;")

        form.addRow("Nombre", self.name_input)
        form.addRow("Precio", self.price_input)
        form.addRow("Ingredientes", self.ingredients_input)
        form.addRow("Disponible", self.available_input)
        form.addRow("Stock", self.stock_input)
        form.addRow("Categorias", self.category_input)
        form.addRow("", self.category_hint)
        layout.addLayout(form)

        actions = QHBoxLayout()
        actions.setSpacing(12)

        self.clear_button = self._build_action_button("Limpiar", secondary=True)
        self.save_button = self._build_action_button("Anadir producto")
        self.clear_button.clicked.connect(self._clear_form)
        self.save_button.clicked.connect(self._save_product)

        actions.addWidget(self.clear_button)
        actions.addWidget(self.save_button)
        layout.addLayout(actions)
        layout.addStretch()
        return card

    def _build_promotion_card(self):
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            f"""
            QFrame#card {{
                background-color: {C_CREAM};
                border-radius: 34px;
            }}
            QLabel {{
                color: #163246;
            }}
            QDateEdit, QSpinBox, QComboBox {{
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
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Promociones")
        title.setStyleSheet("color: #163246; font-size: 22px; font-weight: 700;")
        layout.addWidget(title)

        self.promotion_status = QLabel("")
        self.promotion_status.setWordWrap(True)
        self.promotion_status.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(self.promotion_status)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(12)

        self.discount_input = QSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setSuffix(" %")

        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setDisplayFormat("dd/MM/yyyy")

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate().addDays(7))
        self.end_date_input.setDisplayFormat("dd/MM/yyyy")

        self.promotion_product_input = QComboBox()
        self.promotion_product_input.setEditable(True)
        self.promotion_product_input.setInsertPolicy(QComboBox.NoInsert)
        self.promotion_product_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.promotion_product_completer = QCompleter([], self.promotion_product_input)
        self.promotion_product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.promotion_product_completer.setFilterMode(Qt.MatchContains)
        self.promotion_product_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.promotion_product_input.setCompleter(self.promotion_product_completer)

        form.addRow("Descuento", self.discount_input)
        form.addRow("Fecha inicio", self.start_date_input)
        form.addRow("Fecha fin", self.end_date_input)
        form.addRow("Producto", self.promotion_product_input)
        layout.addLayout(form)

        promo_actions = QHBoxLayout()
        promo_actions.setSpacing(12)
        self.clear_promo_button = self._build_action_button("Limpiar promo", secondary=True)
        self.save_promo_button = self._build_action_button("Anadir promocion")
        self.clear_promo_button.clicked.connect(self._clear_promotion_form)
        self.save_promo_button.clicked.connect(self._save_promotion)
        promo_actions.addWidget(self.clear_promo_button)
        promo_actions.addWidget(self.save_promo_button)
        layout.addLayout(promo_actions)

        self.empty_promotion_label = QLabel("TODAVIA NO HAY PROMOCIONES")
        self.empty_promotion_label.setAlignment(Qt.AlignCenter)
        self.empty_promotion_label.setStyleSheet("color: #163246; font-size: 18px; font-weight: 700;")

        self.promotion_table = QTableWidget(0, 5)
        self.promotion_table.setHorizontalHeaderLabels(["ID", "Producto", "Descuento", "Periodo", "Eliminar"])
        self.promotion_table.verticalHeader().setVisible(False)
        self.promotion_table.setSelectionMode(QTableWidget.NoSelection)
        self.promotion_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.promotion_table.setShowGrid(False)
        self.promotion_table.setStyleSheet(
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
                padding: 9px;
                font-size: 12px;
                font-weight: 700;
            }}
            """
        )
        self.promotion_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.promotion_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout.addWidget(self.empty_promotion_label, 1)
        layout.addWidget(self.promotion_table, 1)
        return card

    def _go_back(self, checked=False):
        self.volver_menu.emit()
        self.close()

    def _build_action_button(self, text, secondary=False):
        button = QPushButton(text)
        button.setMinimumHeight(48)
        button.setCursor(Qt.PointingHandCursor)
        background = C_CREAM if secondary else C_ORANGE
        foreground = "#163246" if secondary else "white"
        hover = "#F3E6D8" if secondary else C_ORANGE_DARK
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {background};
                color: {foreground};
                border: none;
                border-radius: 24px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            """
        )
        return button

    def _build_mode_button(self, text):
        button = QPushButton(text)
        button.setMinimumHeight(46)
        button.setCursor(Qt.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return button

    def _set_mode(self, mode):
        self.current_mode = mode
        showing_products = mode == "productos"
        self.product_form_card.setVisible(showing_products)
        self.promotion_card.setVisible(not showing_products)

        self._apply_mode_button_style(self.products_mode_button, showing_products)
        self._apply_mode_button_style(self.promotions_mode_button, not showing_products)

    def _apply_mode_button_style(self, button, active):
        background = C_ORANGE if active else C_CREAM
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

    def _load_schema(self):
        if self.controlador is None:
            self.form_status.setText("No hay un controlador de productos conectado.")
            return
        try:
            self.schema_info = self.controlador.describirProductos()
        except Exception as exc:
            self.form_status.setText(str(exc))
            return

        category_enabled = bool(self.schema_info.get("category_column"))
        self.category_input.setEnabled(category_enabled)
        if category_enabled:
            self.category_hint.setText("Selecciona una categoria valida de la carta.")
        else:
            self.category_hint.setText("La BD actual no tiene columna de categorias en PRODUCTOS.")

    def _load_products(self):
        if self.controlador is None:
            self.productos = []
            self.product_name_options = []
            self._refresh_promotion_product_selector()
            self.table.hide()
            self.empty_label.show()
            return
        try:
            self.productos = self.controlador.listarProductos()
        except Exception as exc:
            self.productos = []
            self.product_name_options = []
            self._refresh_promotion_product_selector()
            self.table.hide()
            self.empty_label.show()
            self.form_status.setText(str(exc))
            return

        self.table.setRowCount(len(self.productos))
        self.product_name_options = [producto.nombre for producto in self.productos]
        self._refresh_promotion_product_selector()
        for row, producto in enumerate(self.productos):
            self._set_item(self.table, row, 0, producto.nombre)
            self._set_item(self.table, row, 1, f"{producto.precio:.2f}")
            self._set_item(self.table, row, 2, producto.ingredientes)
            self._set_item(self.table, row, 3, producto.disponible)
            self._set_item(self.table, row, 4, str(producto.stock))
            self._set_item(self.table, row, 5, producto.categoria)
            self.table.setCellWidget(row, 6, self._build_row_button("Editar", lambda checked=False, p=producto: self._edit_product(p)))
            self.table.setCellWidget(row, 7, self._build_row_button("Eliminar", lambda checked=False, p=producto: self._delete_product(p)))
            self.table.setRowHeight(row, 62)

        has_products = bool(self.productos)
        self.empty_label.setVisible(not has_products)
        self.table.setVisible(has_products)
        if not has_products:
            self.form_status.setText("Puedes crear el primer producto desde el formulario.")
        elif self.editing_name is None:
            self.form_status.setText("Selecciona un producto para editarlo o crea uno nuevo.")

    def _load_promotions(self):
        if self.controlador is None:
            self.promociones = []
            self.promotion_table.hide()
            self.empty_promotion_label.show()
            return
        try:
            self.promociones = self.controlador.listarPromociones()
        except Exception as exc:
            self.promociones = []
            self.promotion_table.hide()
            self.empty_promotion_label.show()
            self.promotion_status.setText(str(exc))
            return

        self.promotion_table.setRowCount(len(self.promociones))
        for row, promocion in enumerate(self.promociones):
            period = f"{promocion.fecha_inicio:%d/%m/%Y} - {promocion.fecha_fin:%d/%m/%Y}"
            self._set_item(self.promotion_table, row, 0, promocion.id_promocion)
            self._set_item(self.promotion_table, row, 1, promocion.nombre_producto)
            self._set_item(self.promotion_table, row, 2, f"{promocion.descuento}%")
            self._set_item(self.promotion_table, row, 3, period)
            self.promotion_table.setCellWidget(
                row,
                4,
                self._build_row_button("Eliminar", lambda checked=False, promo=promocion: self._delete_promotion(promo)),
            )
            self.promotion_table.setRowHeight(row, 54)

        has_promotions = bool(self.promociones)
        self.empty_promotion_label.setVisible(not has_promotions)
        self.promotion_table.setVisible(has_promotions)
        if not has_promotions:
            self.promotion_status.setText("Puedes crear la primera promocion desde este bloque.")

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

    def _edit_product(self, producto):
        self.editing_name = producto.nombre
        self.name_input.setText(producto.nombre)
        self.price_input.setValue(producto.precio)
        self.ingredients_input.setPlainText(producto.ingredientes)
        self.available_input.setCurrentText(producto.disponible)
        self.stock_input.setValue(producto.stock)
        self._set_category_value(producto.categoria)
        self.save_button.setText("Guardar cambios")
        self.form_status.setText(f"Editando: {producto.nombre}")

    def _clear_form(self):
        self.editing_name = None
        self.name_input.clear()
        self.price_input.setValue(0.01)
        self.ingredients_input.clear()
        self.available_input.setCurrentText("Y")
        self.stock_input.setValue(0)
        self.category_input.setCurrentIndex(0)
        self.save_button.setText("Anadir producto")
        self.form_status.setText("Formulario listo para crear un producto nuevo.")

    def _save_product(self):
        product_data = self._collect_product_data()
        if product_data is None:
            return
        if self.controlador is None:
            QMessageBox.warning(self, "Productos", "No hay un controlador de productos conectado.")
            return

        try:
            if self.editing_name is None:
                self.controlador.crearProducto(*product_data)
                self.form_status.setText("Producto creado correctamente.")
            else:
                self.controlador.actualizarProducto(self.editing_name, *product_data)
                self.form_status.setText("Producto actualizado correctamente.")
        except Exception as exc:
            QMessageBox.warning(self, "Productos", str(exc))
            return

        self._clear_form()
        self._load_products()

    def _collect_product_data(self):
        nombre = self.name_input.text().strip()
        ingredientes = self.ingredients_input.toPlainText().strip()

        if not nombre:
            QMessageBox.warning(self, "Productos", "El nombre del producto es obligatorio.")
            return None
        if not ingredientes:
            QMessageBox.warning(self, "Productos", "Los ingredientes son obligatorios.")
            return None

        return (
            nombre,
            float(self.price_input.value()),
            ingredientes,
            self.available_input.currentText(),
            int(self.stock_input.value()),
            self.category_input.currentText().strip(),
        )

    def _set_category_value(self, categoria):
        normalized = str(categoria).strip().lower()
        for index in range(self.category_input.count()):
            if self.category_input.itemText(index).lower() == normalized:
                self.category_input.setCurrentIndex(index)
                return
        self.category_input.setCurrentIndex(0)

    def _delete_product(self, producto):
        reply = QMessageBox.question(
            self,
            "Eliminar producto",
            f"Quieres eliminar {producto.nombre}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        if self.controlador is None:
            QMessageBox.warning(self, "Productos", "No hay un controlador de productos conectado.")
            return

        try:
            self.controlador.eliminarProducto(producto.nombre)
        except Exception as exc:
            QMessageBox.warning(self, "Productos", str(exc))
            return

        if self.editing_name == producto.nombre:
            self._clear_form()
        self.form_status.setText("Producto eliminado correctamente.")
        self._load_products()

    def _clear_promotion_form(self):
        self.discount_input.setValue(0)
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate().addDays(7))
        if self.promotion_product_input.count() > 0:
            self.promotion_product_input.setCurrentIndex(0)
        self.promotion_product_input.lineEdit().clear()
        self.promotion_status.setText("Formulario de promocion listo.")

    def _save_promotion(self):
        if self.controlador is None:
            QMessageBox.warning(self, "Promociones", "No hay un controlador de promociones conectado.")
            return

        start_date = self.start_date_input.date()
        end_date = self.end_date_input.date()
        if end_date <= start_date:
            QMessageBox.warning(self, "Promociones", "La fecha fin debe ser posterior a la fecha inicio.")
            return

        nombre_producto = self.promotion_product_input.currentText().strip()
        if not nombre_producto:
            QMessageBox.warning(self, "Promociones", "Debes indicar el producto al que se aplica la promocion.")
            return
        if nombre_producto not in self.product_name_options:
            QMessageBox.warning(self, "Promociones", "El producto indicado no existe en la base de datos.")
            return

        try:
            self.controlador.crearPromocion(
                int(self.discount_input.value()),
                start_date.toPyDate(),
                end_date.toPyDate(),
                nombre_producto,
            )
        except Exception as exc:
            QMessageBox.warning(self, "Promociones", str(exc))
            return

        self._clear_promotion_form()
        self.promotion_status.setText("Promocion creada correctamente.")
        self._load_promotions()

    def _delete_promotion(self, promocion):
        reply = QMessageBox.question(
            self,
            "Eliminar promocion",
            f"Quieres eliminar la promocion {promocion.id_promocion}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.controlador.eliminarPromocion(promocion.id_promocion)
        except Exception as exc:
            QMessageBox.warning(self, "Promociones", str(exc))
            return

        self.promotion_status.setText("Promocion eliminada correctamente.")
        self._load_promotions()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controlador = ControladorProductos(Logica())
    window = AdminProductosUI(controlador=controlador)
    window.show()
    sys.exit(app.exec_())
