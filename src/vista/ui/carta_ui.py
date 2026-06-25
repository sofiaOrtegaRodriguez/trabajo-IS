import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QSizePolicy, QWidget

# ── Añade la raíz del proyecto al sys.path cuando el módulo se ejecuta directamente
# (no como parte de un paquete), para que los imports absolutos funcionen siempre.
if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

# ── Rutas absolutas a los ficheros .ui de Qt Designer
_DIR = os.path.dirname(__file__)
_UI_CARTA = os.path.join(_DIR, "../ui_pyqt/carta_ui.ui")   # Layout principal de la carta
_UI_CARD  = os.path.join(_DIR, "../ui_pyqt/product_card.ui")  # Layout de cada tarjeta de producto

# ── Paleta de colores reutilizable en los estilos QSS
C_ORANGE      = "#ff6600"
C_ORANGE_DARK = "#e65c00"
C_CARD        = "#5CA9D0"
C_TEXT_DIM    = "#F6F2F2"
C_WHITE       = "#F3EFEF"
C_BORDER      = "#133749"

# ── Mapeo (nombre_widget_en_.ui, clave_interna) para los botones de categoría.
# Si el examen pide añadir una categoría nueva, se añade aquí y se crea el botón en el .ui.
CATEGORIAS = [
    ("cat_btn_sushi",       "sushi"),
    ("cat_btn_fritos",      "fritos"),
    ("cat_btn_bebidas",     "bebidas"),
    ("cat_btn_postres",     "postres"),
    ("cat_btn_promociones", "promociones"),
]

# ── Estilos QSS para el botón de categoría seleccionado vs. el resto
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


# ══════════════════════════════════════════════════════════════
#  ProductCard  –  tarjeta visual de un único producto
# ══════════════════════════════════════════════════════════════
class ProductCard(QFrame):
    """
    Widget que representa un producto en la carta.
    Emite señales hacia arriba (CartaUI → Controlador) para añadir
    o quitar unidades; nunca modifica el modelo directamente.
    """

    # Señal emitida al pulsar '+': lleva (product_id, cantidad_a_añadir)
    add_clicked    = pyqtSignal(str, int)
    # Señal emitida al pulsar '-': lleva (product_id,)
    remove_clicked = pyqtSignal(str)

    def __init__(self, product_id, nombre, precio, promo_texto,
                 imagen_path, has_image, quantity=0, parent=None):
        super().__init__(parent)
        uic.loadUi(_UI_CARD, self)          # Carga el layout desde el .ui
        self._product_id = product_id       # ID interno del producto (se usa en las señales)

        # ── Textos básicos (widgets definidos en product_card.ui)
        self.name_label.setText(nombre)
        self.price_label.setText(precio)

        # ── Etiqueta de promoción: se oculta si el producto no tiene promo
        if promo_texto:
            self.promo_label.setText(promo_texto)
        else:
            self.promo_label.hide()

        # ── Imagen del producto
        # Se escala distinto según si el producto tiene imagen propia o usa un placeholder
        pixmap = QPixmap(imagen_path) if has_image and imagen_path else QPixmap()
        if not pixmap.isNull():
            if has_image:
                # Imagen real: recorte expansivo para rellenar el hueco sin deformar
                pixmap = pixmap.scaled(210, 190, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            else:
                # Placeholder: se encaja sin recortar
                pixmap = pixmap.scaled(145, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

        # ── Cantidad inicial (puede venir de la cesta ya existente)
        self.set_quantity(quantity)

        # ── Conexión de botones a emisores de señal locales
        self.minus_button.clicked.connect(self._emit_remove)
        self.plus_button.clicked.connect(self._emit_add)

    # ── Emite add_clicked con cantidad fija = 1
    def _emit_add(self):
        self.add_clicked.emit(self._product_id, 1)

    # ── Emite remove_clicked con el ID del producto
    def _emit_remove(self):
        self.remove_clicked.emit(self._product_id)

    def set_quantity(self, quantity):
        """
        Actualiza el contador visible y deshabilita el botón '-'
        cuando la cantidad es 0 (no se puede quitar lo que no hay).
        El controlador llama a este método tras cada cambio en la cesta.
        """
        self.quantity_label.setText(str(quantity))
        self.minus_button.setEnabled(quantity > 0)


# ══════════════════════════════════════════════════════════════
#  CartaUI  –  vista principal de la carta de productos
# ══════════════════════════════════════════════════════════════
class CartaUI(QWidget):
    """
    Vista MVC pura: no contiene lógica de negocio.
    Solo define señales, conecta widgets del .ui a esas señales
    y expone métodos públicos que el controlador usa para actualizar la pantalla.
    """

    # ── Señales hacia el controlador
    add_product      = pyqtSignal(str, int)   # (product_id, cantidad)  – re-emitida desde ProductCard
    remove_product   = pyqtSignal(str)         # (product_id,)           – re-emitida desde ProductCard
    profile_clicked  = pyqtSignal()            # Botón de perfil
    cart_clicked     = pyqtSignal()            # Botón de cesta/carrito
    cerrar_sesion    = pyqtSignal()            # Botón cerrar sesión
    category_clicked = pyqtSignal(str)         # (clave_categoría)  – filtra productos
    next_clicked     = pyqtSignal()            # Paginación → página siguiente
    prev_clicked     = pyqtSignal()            # Paginación → página anterior

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(_UI_CARTA, self)            # Carga el layout principal desde el .ui

        self._category_buttons = {}            # {clave: QPushButton} – para cambiar estilos
        self._product_cards     = {}           # {product_id: ProductCard} – para actualizar cantidades

        # ── Inicialización de botones de categoría
        for widget_name, key in CATEGORIAS:
            btn = getattr(self, widget_name)           # Obtiene el widget por nombre desde el .ui
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # Lambda con valor por defecto evita el cierre clásico de Python sobre 'key'
            btn.clicked.connect(lambda checked=False, k=key: self.category_clicked.emit(k))
            self._category_buttons[key] = btn

        # ── Resto de botones del layout principal
        self.btn_cerrar_sesion.clicked.connect(self.cerrar_sesion.emit)
        self.prev_button.clicked.connect(self.prev_clicked.emit)
        self.next_button.clicked.connect(self.next_clicked.emit)
        self.profile_button.clicked.connect(self.profile_clicked.emit)
        self.cart_button.clicked.connect(self.cart_clicked.emit)

    # ── Métodos públicos llamados por el controlador ──────────────

    def mostrar_productos(self, productos_render):
        """
        Reconstruye completamente la cuadrícula de productos.
        'productos_render' es una lista de dicts con las claves:
            id, nombre, precio_str, promo_texto, imagen_path, has_image, quantity
        El controlador la prepara en ServicioCarta/ControladorCarta y la pasa aquí.

        Disposición: 2 columnas, tantas filas como hagan falta (divmod calcula row, col).
        """
        self._product_cards = {}

        # Vacía la cuadrícula actual y destruye los widgets hijos
        while self.product_grid.count():
            item   = self.product_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Crea y añade una ProductCard por cada producto de la página actual
        for idx, p in enumerate(productos_render):
            row, col = divmod(idx, 2)          # 2 columnas: 0→(0,0), 1→(0,1), 2→(1,0), …
            card = ProductCard(
                p["id"], p["nombre"], p["precio_str"],
                p["promo_texto"], p["imagen_path"], p["has_image"], p["quantity"],
            )
            # Re-emite las señales de la tarjeta hacia arriba (burbujeo manual)
            card.add_clicked.connect(lambda pid, amt: self.add_product.emit(pid, amt))
            card.remove_clicked.connect(lambda pid: self.remove_product.emit(pid))
            self.product_grid.addWidget(card, row, col)
            self._product_cards[p["id"]] = card    # Registra para poder actualizar después

    def set_page_info(self, texto):
        """Actualiza el label de paginación (ej. 'Página 1 / 3')."""
        self.page_info.setText(texto)

    def set_categoria_activa(self, key):
        """
        Resalta el botón de la categoría seleccionada y desactiva los demás.
        Llamado por el controlador cada vez que cambia la categoría.
        """
        for k, btn in self._category_buttons.items():
            btn.setStyleSheet(_STYLE_ACTIVE if k == key else _STYLE_INACTIVE)

    def set_cantidad_producto(self, product_id, quantity):
        """
        Actualiza el contador de cantidad en una tarjeta concreta
        sin reconstruir toda la cuadrícula.
        Llamado por el controlador tras añadir/quitar un producto de la cesta.
        """
        card = self._product_cards.get(product_id)
        if card:
            card.set_quantity(quantity)

    def set_texto_sesion(self, texto):
        """Cambia el texto del botón de cerrar sesión (ej. nombre del usuario)."""
        self.btn_cerrar_sesion.setText(texto)