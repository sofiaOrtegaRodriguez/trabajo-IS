import os
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

if __package__ is None or __package__ == "":
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from src.controlador.ControladorProductos import ControladorProductos
from src.modelo.Logica import Logica


C_CARD = "#5CA9D0"
C_ORANGE = "#ff6600"
C_ORANGE_DARK = "#e65c00"
C_TEXT_MUTED = "#e65c00"
C_TEXT_DIM = "#F6F2F2"
C_WHITE = "#F3EFEF"
C_PANEL = "#133749"
C_BORDER = "#133749"

CATEGORIAS = [
    ("Sushi", "sushi"),
    ("Fritos", "fritos"),
    ("Bebidas", "bebidas"),
    ("Postres", "postres"),
    ("Promociones", "promociones"),
]


class CircularIconButton(QPushButton):
    def __init__(self, kind, parent=None):
        super().__init__(parent)
        self.kind = kind
        self.setFixedSize(58, 58)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_CARD};
                color: {C_ORANGE};
                border: 2px solid {C_ORANGE};
                border-radius: 29px;
                font-family: Arial;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE};
            }}
            """
        )

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        hovered = self.underMouse()
        pen_color = QColor(C_WHITE if hovered else C_ORANGE)
        painter.setPen(QPen(pen_color, 2))
        painter.setBrush(Qt.NoBrush)

        if self.kind == "profile":
            painter.drawEllipse(22, 13, 14, 14)
            painter.drawArc(16, 26, 26, 18, 0, 180 * 16)
        elif self.kind == "cart":
            painter.drawRect(18, 20, 20, 14)
            painter.drawLine(15, 17, 20, 20)
            painter.drawLine(38, 20, 42, 16)
            painter.drawEllipse(20, 36, 5, 5)
            painter.drawEllipse(32, 36, 5, 5)
        painter.end()


class ProductCard(QFrame):
    add_clicked = pyqtSignal(str, int)
    remove_clicked = pyqtSignal(str)

    def __init__(self, product, pixmap, has_image, quantity=0, parent=None):
        super().__init__(parent)
        self.product = product
        self.pixmap = pixmap
        self.has_image = has_image
        self.quantity = max(0, int(quantity))
        self.minus_button = None
        self.plus_button = None
        self.quantity_label = None
        self._build()

    def _build(self):
        self.setObjectName("productCard")
        self.setMinimumSize(250, 320)
        self.setStyleSheet(
            f"""
            QFrame#productCard {{
                background-color: {C_CARD};
                border: 1px solid {C_BORDER};
                border-radius: 24px;
            }}
            QLabel {{
                background: transparent;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        image_label = QLabel()
        image_label.setMinimumHeight(205)
        image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet(f"background-color: {C_PANEL}; border-radius: 20px;")
        if self.has_image:
            image_label.setPixmap(
                self.pixmap.scaled(210, 190, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            )
        else:
            image_label.setPixmap(
                self.pixmap.scaled(145, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        info_block = QWidget()
        info_layout = QVBoxLayout(info_block)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(6)

        name_label = QLabel(self.product["nombre"])
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(
            f"color: {C_WHITE}; font-family: Arial; font-size: 14px; font-weight: 700;"
        )

        price_label = QLabel(f"{self.product['precio']:.2f} EUR")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet(
            f"color: {C_ORANGE}; font-family: Arial; font-size: 12px; font-weight: 700;"
        )

        promo_label = QLabel("")
        promo_label.setAlignment(Qt.AlignCenter)
        promo_label.setStyleSheet(
            f"color: {C_WHITE}; font-family: Arial; font-size: 11px; font-weight: 700;"
        )
        promo_label.hide()

        if self.product.get("promocion_hasta"):
            promo_label.setText(
                f"-{self.product.get('promocion_descuento', 0)}% hasta {self.product['promocion_hasta']}"
            )
            promo_label.show()

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addStretch()

        self.minus_button = self._action_button("-")
        self.plus_button = self._action_button("+")
        self.quantity_label = QLabel(str(self.quantity))
        self.quantity_label.setAlignment(Qt.AlignCenter)
        self.quantity_label.setMinimumWidth(28)
        self.quantity_label.setStyleSheet(
            f"color: {C_WHITE}; font-family: Arial; font-size: 14px; font-weight: 700;"
        )
        self.minus_button.clicked.connect(lambda: self.remove_clicked.emit(self.product["id"]))
        self.plus_button.clicked.connect(lambda: self.add_clicked.emit(self.product["id"], 1))

        buttons.addWidget(self.minus_button)
        buttons.addWidget(self.quantity_label)
        buttons.addWidget(self.plus_button)
        buttons.addStretch()

        info_layout.addWidget(name_label)
        info_layout.addWidget(price_label)
        info_layout.addWidget(promo_label)
        info_layout.addLayout(buttons)

        layout.addWidget(image_label, 1)
        layout.addWidget(info_block, 0)
        self._update_quantity_state()

    def _action_button(self, text):
        button = QPushButton(text)
        button.setFixedSize(30, 30)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {C_ORANGE};
                color: {C_WHITE};
                border: none;
                border-radius: 15px;
                font-family: Arial;
                font-size: 16px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {C_ORANGE_DARK};
            }}
            """
        )
        return button

    def set_quantity(self, quantity):
        self.quantity = max(0, int(quantity))
        if self.quantity_label is not None:
            self.quantity_label.setText(str(self.quantity))
        self._update_quantity_state()

    def _update_quantity_state(self):
        if self.minus_button is None:
            return
        self.minus_button.setEnabled(self.quantity > 0)
        self.minus_button.setToolTip("Quitar una unidad" if self.quantity > 0 else "No hay unidades para quitar")


class CartaUI(QWidget):
    add_product = pyqtSignal(str, int)
    remove_product = pyqtSignal(str)
    profile_clicked = pyqtSignal()
    cart_clicked = pyqtSignal()

    def __init__(self, controlador=None, quantity_provider=None, parent=None):
        super().__init__(parent)
        self.controlador = controlador
        self.quantity_provider = quantity_provider
        self.current_category = "sushi"
        self.current_page = 0
        self.products_per_page = 4
        self.category_buttons = {}
        self.product_pixmaps = {}
        self.image_presence = {}
        self.products_by_category = {key: [] for _, key in CATEGORIAS}
        self.products = []
        self.product_grid = None
        self.page_info = None
        self.prev_button = None
        self.next_button = None
        self.product_cards = {}
        self._load_data()
        self._build()
        self._load_products(self.current_category)

    def _load_data(self):
        self.products_by_category = {key: [] for _, key in CATEGORIAS}
        self.product_pixmaps = {}
        self.image_presence = {}

        if self.controlador is None:
            return

        products_by_category = self.controlador.listarProductosCarta()
        for category_key in self.products_by_category:
            products = products_by_category.get(category_key, [])
            self.products_by_category[category_key] = products
            for product in products:
                image_path = self._find_product_image(product["categoria"], product["nombre"])
                has_image = bool(image_path)
                pixmap = QPixmap(image_path) if has_image else self._build_placeholder_pixmap()
                self.product_pixmaps[product["id"]] = pixmap
                self.image_presence[product["id"]] = has_image

    def _find_product_image(self, categoria, nombre_producto):
        image_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "imagenes", "comida"))
        folder_candidates = {
            "sushi": ["sushi"],
            "fritos": ["fritos"],
            "postres": ["postres"],
            "bebidas": ["bebidas", "bebida"],
        }.get(categoria, [categoria])

        normalized_name = self._normalize_name(nombre_producto)
        for folder in folder_candidates:
            folder_path = os.path.join(image_root, folder)
            if not os.path.isdir(folder_path):
                continue

            for filename in os.listdir(folder_path):
                full_path = os.path.join(folder_path, filename)
                if not os.path.isfile(full_path):
                    continue

                stem, _ = os.path.splitext(filename)
                if self._normalize_name(stem) == normalized_name:
                    return full_path
        return None

    def _normalize_name(self, text):
        return "".join(char.lower() for char in str(text) if char.isalnum())

    def _build_placeholder_pixmap(self):
        pixmap = QPixmap(240, 220)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(C_PANEL))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 240, 220, 24, 24)

        painter.setPen(QPen(QColor(C_ORANGE), 5))
        painter.drawRect(72, 66, 96, 72)
        painter.drawLine(86, 66, 104, 46)
        painter.drawLine(104, 46, 132, 46)
        painter.drawLine(132, 46, 150, 66)
        painter.drawEllipse(92, 88, 16, 16)
        painter.drawLine(74, 142, 166, 50)

        painter.setPen(QColor(C_WHITE))
        painter.drawText(pixmap.rect(), Qt.AlignBottom | Qt.AlignHCenter, "SIN FOTO")
        painter.end()
        return pixmap

    def _build(self):
        self.setStyleSheet(f"background-color: {C_CARD};")

        root = QHBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        left_panel = QFrame()
        left_panel.setStyleSheet(
            f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 34px;
            }}
            """
        )
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(18, 18, 18, 18)
        left_layout.setSpacing(18)

        header = QLabel("Carta")
        header.setStyleSheet(
            f"color: {C_WHITE}; font-family: Arial; font-size: 26px; font-weight: 700;"
        )
        left_layout.addWidget(header)

        self._build_products(left_layout)
        root.addWidget(left_panel, 7)

        right_panel = QFrame()
        right_panel.setFixedWidth(210)
        right_panel.setStyleSheet(
            f"""
            QFrame {{
                background-color: {C_PANEL};
                border-radius: 34px;
            }}
            """
        )
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 18, 16, 18)
        right_layout.setSpacing(14)

        self._build_categories(right_layout)

        right_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        bottom_buttons = QHBoxLayout()
        bottom_buttons.setSpacing(14)

        profile_button = CircularIconButton("profile")
        cart_button = CircularIconButton("cart")
        profile_button.clicked.connect(self.profile_clicked.emit)
        cart_button.clicked.connect(self.cart_clicked.emit)

        bottom_buttons.addStretch()
        bottom_buttons.addWidget(profile_button)
        bottom_buttons.addWidget(cart_button)
        bottom_buttons.addStretch()
        right_layout.addLayout(bottom_buttons)

        root.addWidget(right_panel, 3)

    def _build_categories(self, parent_layout):
        title = QLabel("Categorias")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {C_TEXT_MUTED}; font-family: Arial; font-size: 14px; font-weight: 700;"
        )
        parent_layout.addWidget(title)

        for label, key in CATEGORIAS:
            button = QPushButton(label)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(76)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.clicked.connect(lambda checked=False, category=key: self._on_category_clicked(category))
            parent_layout.addWidget(button)
            self.category_buttons[key] = button

        self._update_category_styles()

    def _build_products(self, parent_layout):
        grid_container = QWidget()
        self.product_grid = QGridLayout(grid_container)
        self.product_grid.setContentsMargins(0, 0, 0, 0)
        self.product_grid.setHorizontalSpacing(18)
        self.product_grid.setVerticalSpacing(18)
        parent_layout.addWidget(grid_container, 1)

        navigation = QHBoxLayout()
        navigation.setSpacing(16)
        navigation.addStretch()

        self.prev_button = QPushButton("<")
        self.next_button = QPushButton(">")
        for button in (self.prev_button, self.next_button):
            button.setFixedSize(48, 48)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {C_ORANGE};
                    color: {C_WHITE};
                    border: none;
                    border-radius: 24px;
                    font-family: Arial;
                    font-size: 20px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background-color: {C_ORANGE_DARK};
                }}
                """
            )

        self.page_info = QLabel("")
        self.page_info.setAlignment(Qt.AlignCenter)
        self.page_info.setStyleSheet(
            f"color: {C_TEXT_MUTED}; font-family: Arial; font-size: 14px;"
        )

        self.prev_button.clicked.connect(self._show_prev_page)
        self.next_button.clicked.connect(self._show_next_page)

        navigation.addWidget(self.prev_button)
        navigation.addWidget(self.page_info)
        navigation.addWidget(self.next_button)
        navigation.addStretch()
        parent_layout.addLayout(navigation)

    def _load_products(self, categoria):
        self.current_category = categoria
        self.current_page = 0
        self.products = list(self.products_by_category.get(categoria, []))
        self._update_category_styles()
        self._refresh_products()

    def _refresh_products(self):
        self.product_cards = {}
        while self.product_grid.count():
            item = self.product_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        start = self.current_page * self.products_per_page
        end = start + self.products_per_page
        page_products = self.products[start:end]

        for index, product in enumerate(page_products):
            row = index // 2
            col = index % 2
            card = ProductCard(
                product,
                self.product_pixmaps[product["id"]],
                self.image_presence.get(product["id"], False),
                quantity=self._get_product_quantity(product["id"]),
            )
            card.add_clicked.connect(lambda product_id, amount: self.add_product.emit(product_id, amount))
            card.remove_clicked.connect(lambda product_id: self.remove_product.emit(product_id))
            self.product_grid.addWidget(card, row, col)
            self.product_cards[product["id"]] = card

        total_pages = max(1, (len(self.products) + self.products_per_page - 1) // self.products_per_page)
        self.page_info.setText(f"Pagina {self.current_page + 1} / {total_pages}")

    def update_product_quantity(self, product_id, quantity):
        card = self.product_cards.get(product_id)
        if card is not None:
            card.set_quantity(quantity)

    def sync_cart_quantities(self, quantities):
        for product_id, card in self.product_cards.items():
            card.set_quantity(quantities.get(product_id, 0))

    def _get_product_quantity(self, product_id):
        if callable(self.quantity_provider):
            return self.quantity_provider(product_id)
        return 0

    def _on_category_clicked(self, categoria):
        if categoria == self.current_category:
            return
        self._load_products(categoria)

    def _update_category_styles(self):
        for key, button in self.category_buttons.items():
            selected = key == self.current_category
            background = C_ORANGE if selected else C_CARD
            foreground = C_WHITE if selected else C_TEXT_DIM
            border = C_ORANGE if selected else C_BORDER
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {background};
                    color: {foreground};
                    border: 1px solid {border};
                    border-radius: 20px;
                    font-family: Arial;
                    font-size: 14px;
                    font-weight: 700;
                    padding: 12px;
                }}
                QPushButton:hover {{
                    background-color: {C_ORANGE if not selected else C_ORANGE_DARK};
                    color: {C_WHITE};
                    border: 1px solid {C_ORANGE};
                }}
                """
            )

    def _show_next_page(self):
        next_start = (self.current_page + 1) * self.products_per_page
        if next_start >= len(self.products):
            return
        self.current_page += 1
        self._refresh_products()

    def _show_prev_page(self):
        if self.current_page == 0:
            return
        self.current_page -= 1
        self._refresh_products()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controlador = ControladorProductos(Logica())
    window = CartaUI(controlador=controlador)
    window.resize(1100, 720)
    window.show()
    sys.exit(app.exec_())
