import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QSizePolicy, QWidget

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

_DIR = os.path.dirname(__file__)
_UI_CARTA = os.path.join(_DIR, "../ui_pyqt/carta_ui.ui")
_UI_CARD = os.path.join(_DIR, "../ui_pyqt/product_card.ui")

C_ORANGE = "#ff6600"
C_ORANGE_DARK = "#e65c00"
C_CARD = "#5CA9D0"
C_TEXT_DIM = "#F6F2F2"
C_WHITE = "#F3EFEF"
C_BORDER = "#133749"

CATEGORIAS = [
    ("cat_btn_sushi", "sushi"),
    ("cat_btn_fritos", "fritos"),
    ("cat_btn_bebidas", "bebidas"),
    ("cat_btn_postres", "postres"),
    ("cat_btn_promociones", "promociones"),
]

_STYLE_ACTIVE = (
    f"QPushButton {{ background-color: {C_ORANGE}; color: {C_WHITE};"
    f" border: 1px solid {C_ORANGE}; border-radius: 20px;"
    f" font-family: Arial; font-size: 14px; font-weight: 700; padding: 12px; }}"
    f"QPushButton:hover {{ background-color: {C_ORANGE_DARK}; color: {C_WHITE}; border: 1px solid {C_ORANGE}; }}"
)
_STYLE_INACTIVE = (
    f"QPushButton {{ background-color: {C_CARD}; color: {C_TEXT_DIM};"
    f" border: 1px solid {C_BORDER}; border-radius: 20px;"
    f" font-family: Arial; font-size: 14px; font-weight: 700; padding: 12px; }}"
    f"QPushButton:hover {{ background-color: {C_ORANGE}; color: {C_WHITE}; border: 1px solid {C_ORANGE}; }}"
)


class ProductCard(QFrame):
    add_clicked = pyqtSignal(str, int)
    remove_clicked = pyqtSignal(str)

    def __init__(self, product_id, nombre, precio, promo_texto, imagen_path, has_image, quantity=0, parent=None):
        super().__init__(parent)
        uic.loadUi(_UI_CARD, self)
        self._product_id = product_id

        self.name_label.setText(nombre)
        self.price_label.setText(precio)

        if promo_texto:
            self.promo_label.setText(promo_texto)
        else:
            self.promo_label.hide()

        pixmap = QPixmap(imagen_path) if has_image and imagen_path else QPixmap()
        if not pixmap.isNull():
            if has_image:
                pixmap = pixmap.scaled(210, 190, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            else:
                pixmap = pixmap.scaled(145, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

        self.set_quantity(quantity)

        self.minus_button.clicked.connect(self._emit_remove)
        self.plus_button.clicked.connect(self._emit_add)

    def _emit_add(self):
        self.add_clicked.emit(self._product_id, 1)

    def _emit_remove(self):
        self.remove_clicked.emit(self._product_id)

    def set_quantity(self, quantity):
        self.quantity_label.setText(str(quantity))
        self.minus_button.setEnabled(quantity > 0)


class CartaUI(QWidget):
    add_product = pyqtSignal(str, int)
    remove_product = pyqtSignal(str)
    profile_clicked = pyqtSignal()
    cart_clicked = pyqtSignal()
    cerrar_sesion = pyqtSignal()
    category_clicked = pyqtSignal(str)
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(_UI_CARTA, self)
        self._category_buttons = {}
        self._product_cards = {}

        for widget_name, key in CATEGORIAS:
            btn = getattr(self, widget_name)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(lambda checked=False, k=key: self.category_clicked.emit(k))
            self._category_buttons[key] = btn

        self.btn_cerrar_sesion.clicked.connect(self.cerrar_sesion.emit)
        self.prev_button.clicked.connect(self.prev_clicked.emit)
        self.next_button.clicked.connect(self.next_clicked.emit)
        self.profile_button.clicked.connect(self.profile_clicked.emit)
        self.cart_button.clicked.connect(self.cart_clicked.emit)

    def mostrar_productos(self, productos_render):
        self._product_cards = {}
        while self.product_grid.count():
            item = self.product_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for idx, p in enumerate(productos_render):
            row, col = divmod(idx, 2)
            card = ProductCard(
                p["id"], p["nombre"], p["precio_str"],
                p["promo_texto"], p["imagen_path"], p["has_image"], p["quantity"],
            )
            card.add_clicked.connect(lambda pid, amt: self.add_product.emit(pid, amt))
            card.remove_clicked.connect(lambda pid: self.remove_product.emit(pid))
            self.product_grid.addWidget(card, row, col)
            self._product_cards[p["id"]] = card

    def set_page_info(self, texto):
        self.page_info.setText(texto)

    def set_categoria_activa(self, key):
        for k, btn in self._category_buttons.items():
            btn.setStyleSheet(_STYLE_ACTIVE if k == key else _STYLE_INACTIVE)

    def set_cantidad_producto(self, product_id, quantity):
        card = self._product_cards.get(product_id)
        if card:
            card.set_quantity(quantity)

    def set_texto_sesion(self, texto):
        self.btn_cerrar_sesion.setText(texto)
